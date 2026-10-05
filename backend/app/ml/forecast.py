import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.preprocessor import ThreatDataPreprocessor, get_threat_slug
from backend.app.ml.model import load_lstm_model
from backend.app.ml.evaluator import load_evaluation_metrics, calculate_forecast_confidence_intervals

# Risk weights for different threat categories
THREAT_SEVERITY_WEIGHTS = {
    "Ransomware": 1.4,
    "Data Breach": 1.35,
    "DDoS": 1.25,
    "Malware": 1.15,
    "Botnet": 1.05,
    "SQL Injection": 1.0,
    "Phishing": 0.95,
    "Brute Force": 0.85
}

class ThreatForecaster:
    """
    Inference engine that executes recursive multi-step forecasting
    for a chosen threat category over a requested horizon (7, 14, 30, etc.).
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or settings.MODELS_PATH
        self.preprocessor = ThreatDataPreprocessor(models_dir=self.models_dir)

    def _get_recent_history(self, threat_type: str, num_days: int = 60) -> pd.Series:
        """
        Retrieves the most recent consecutive daily threat incident counts
        from processed data files or raw dataset.
        """
        slug = get_threat_slug(threat_type)
        proc_file = os.path.join(settings.PROCESSED_DATA_PATH, f"daily_{slug}.csv")
        
        if os.path.exists(proc_file):
            df = pd.read_csv(proc_file, index_col=0, parse_dates=True)
            series = df["Count"].tail(num_days)
            return series
            
        # Fallback to loading and aggregating directly
        daily_matrix = self.preprocessor.aggregate_daily_threats()
        return daily_matrix[threat_type].tail(num_days)

    def calculate_risk_profile(
        self,
        threat_type: str,
        avg_historical: float,
        avg_predicted: float,
        peak_predicted: float
    ) -> Dict[str, Any]:
        """
        Derives cyber risk indicator levels, scores, and trend direction.
        """
        pct_change = ((avg_predicted - avg_historical) / max(avg_historical, 1.0)) * 100.0
        
        # Trend direction
        if pct_change >= 4.0:
            trend = "Increasing"
        elif pct_change <= -4.0:
            trend = "Decreasing"
        else:
            trend = "Stable"
            
        # Composite Risk Score Calculation (0 - 100)
        category_weight = THREAT_SEVERITY_WEIGHTS.get(threat_type, 1.0)
        base_volume_score = min(50.0, (avg_predicted / 2.5))
        trend_score = min(25.0, max(-15.0, pct_change * 0.5))
        burst_score = min(25.0, ((peak_predicted - avg_predicted) / max(avg_predicted, 1.0)) * 20.0)
        
        raw_score = (base_volume_score + trend_score + burst_score) * category_weight
        risk_score = round(float(np.clip(raw_score, 5.0, 98.0)), 1)
        
        # Risk Category classification
        if risk_score >= 75.0:
            risk_level = "Critical"
        elif risk_score >= 50.0:
            risk_level = "High"
        elif risk_score >= 25.0:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "trend_direction": trend,
            "pct_change": round(pct_change, 2)
        }

    def forecast(
        self,
        threat_type: str,
        forecast_days: int = 30,
        historical_lookback_days: int = 60
    ) -> Dict[str, Any]:
        """
        Runs multi-step recursive LSTM forecast for the given threat type.
        Returns full schema-compliant output including historical context,
        forecast points with confidence bounds, and risk analysis.
        """
        if threat_type not in settings.SUPPORTED_THREAT_TYPES:
            raise ValueError(f"Unsupported threat category '{threat_type}'.")

        # 1. Load model, scaler, and evaluation metrics
        model = load_lstm_model(threat_type, self.models_dir)
        scaler = self.preprocessor.load_scaler(threat_type)
        metrics = load_evaluation_metrics(threat_type, self.models_dir)

        # 2. Retrieve recent historical series
        history_series = self._get_recent_history(threat_type, num_days=historical_lookback_days)
        last_date = history_series.index[-1]
        
        # We need at least sequence_length days to prime the LSTM
        seq_len = settings.DEFAULT_SEQUENCE_LENGTH
        if len(history_series) < seq_len:
            raise ValueError(f"Insufficient history ({len(history_series)} days). Required: {seq_len} days.")
            
        initial_window = history_series.values[-seq_len:].reshape(-1, 1)
        current_scaled_window = scaler.transform(initial_window)  # shape (seq_len, 1)

        # 3. Recursive multi-step rollout
        predicted_scaled = []
        rolling_input = current_scaled_window.copy()
        
        for _ in range(forecast_days):
            # Input shape: (1, seq_len, 1)
            inp = rolling_input.reshape(1, seq_len, 1)
            pred_val = model.predict(inp, verbose=0)[0, 0]
            predicted_scaled.append(pred_val)
            
            # Slide window: drop oldest, append prediction
            rolling_input = np.vstack([rolling_input[1:], [[pred_val]]])

        # 4. Inverse transform predictions to raw counts
        pred_scaled_arr = np.array(predicted_scaled).reshape(-1, 1)
        pred_counts = scaler.inverse_transform(pred_scaled_arr).ravel()
        # Counts cannot be negative
        pred_counts = np.clip(np.round(pred_counts, 2), 0.0, None)

        # 5. Compute confidence intervals
        residual_std = metrics.get("residual_std", float(np.std(pred_counts) * 0.2))
        lower_bounds, upper_bounds = calculate_forecast_confidence_intervals(
            predictions=pred_counts,
            residual_std=residual_std,
            confidence_level=0.95
        )

        # 6. Build timeline date arrays
        forecast_dates = [
            (last_date + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            for i in range(forecast_days)
        ]

        # 7. Assemble structured forecast points
        forecast_points = []
        for d, p, lb, ub in zip(forecast_dates, pred_counts, lower_bounds, upper_bounds):
            forecast_points.append({
                "date": d,
                "predicted_count": round(float(p), 2),
                "lower_bound": round(float(lb), 2),
                "upper_bound": round(float(ub), 2)
            })

        # 8. Assemble historical points for visualization
        historical_points = [
            {"date": d.strftime("%Y-%m-%d"), "count": float(round(c, 2))}
            for d, c in history_series.items()
        ]

        # 9. Compute summary metrics and risk profile
        avg_hist = float(history_series.mean())
        avg_pred = float(np.mean(pred_counts))
        peak_pred = float(np.max(pred_counts))
        peak_idx = int(np.argmax(pred_counts))
        peak_date = forecast_dates[peak_idx]

        risk_profile = self.calculate_risk_profile(
            threat_type=threat_type,
            avg_historical=avg_hist,
            avg_predicted=avg_pred,
            peak_predicted=peak_pred
        )

        summary_stats = {
            "historical_days": len(history_series),
            "avg_historical_count": round(avg_hist, 2),
            "avg_forecast_count": round(avg_pred, 2),
            "predicted_change_pct": risk_profile["pct_change"],
            "peak_forecast_date": peak_date,
            "peak_forecast_count": round(peak_pred, 2),
            "min_forecast_count": round(float(np.min(pred_counts)), 2),
            "risk_score": risk_profile["risk_score"]
        }

        return {
            "threat_type": threat_type,
            "forecast_days": forecast_days,
            "model_name": f"{threat_type} LSTM Forecaster",
            "model_version": "v1.0.0",
            "evaluation_metrics": {
                "mae": metrics.get("mae", 0.0),
                "rmse": metrics.get("rmse", 0.0),
                "mape": metrics.get("mape", 0.0),
                "r2_score": metrics.get("r2_score", 0.0)
            },
            "historical_data": historical_points,
            "forecast_data": forecast_points,
            "summary_stats": summary_stats,
            "risk_level": risk_profile["risk_level"],
            "trend_direction": risk_profile["trend_direction"]
        }
