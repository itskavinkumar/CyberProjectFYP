import os
import json
from typing import Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.preprocessor import get_threat_slug

def calculate_evaluation_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Computes standard academic and industry forecasting metrics:
    - MAE: Mean Absolute Error
    - RMSE: Root Mean Squared Error
    - MAPE: Mean Absolute Percentage Error (safe division against zero counts)
    - R2: Coefficient of determination
    - Residual STD: Standard deviation of prediction residuals (for confidence intervals)
    """
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    
    # Safe MAPE calculation
    denom = np.maximum(y_true, 1.0)
    mape = float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)
    
    # R2 Score (can be negative if model performs poorly on burst outliers)
    r2 = float(r2_score(y_true, y_pred))
    
    # Residual standard error
    residuals = y_true - y_pred
    residual_std = float(np.std(residuals))

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2),
        "r2_score": round(r2, 4),
        "residual_std": round(residual_std, 4),
        "mean_actual": round(float(np.mean(y_true)), 2),
        "mean_predicted": round(float(np.mean(y_pred)), 2)
    }

def calculate_forecast_confidence_intervals(
    predictions: np.ndarray,
    residual_std: float,
    confidence_level: float = 0.95
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates dynamic confidence interval bounds that expand with forecast horizon:
    lower_bound = max(0, pred - z * sigma * sqrt(1 + step / 30))
    upper_bound = pred + z * sigma * sqrt(1 + step / 30)
    """
    predictions = np.asarray(predictions).ravel()
    # z-score for 95% is ~1.96, for 90% is ~1.645
    z_score = 1.96 if confidence_level >= 0.95 else 1.645
    
    lower_bounds = []
    upper_bounds = []
    
    for step_idx, pred in enumerate(predictions):
        # Uncertainty cone expands slightly into the future
        horizon_factor = np.sqrt(1.0 + (step_idx / 30.0))
        margin = z_score * residual_std * horizon_factor
        
        lower = max(0.0, float(pred - margin))
        upper = max(lower, float(pred + margin))
        
        lower_bounds.append(round(lower, 2))
        upper_bounds.append(round(upper, 2))
        
    return np.array(lower_bounds), np.array(upper_bounds)

def save_evaluation_metrics(
    metrics: Dict[str, Any],
    threat_type: str,
    models_dir: Optional[str] = None
) -> str:
    """Saves evaluation metrics JSON to disk."""
    m_dir = models_dir or settings.MODELS_PATH
    slug = get_threat_slug(threat_type)
    metrics_path = os.path.join(m_dir, f"{slug}_metrics.json")
    
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    logger.info(f"Saved evaluation metrics for '{threat_type}' to: {metrics_path}")
    return metrics_path

def load_evaluation_metrics(
    threat_type: str,
    models_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Loads evaluation metrics JSON from disk."""
    m_dir = models_dir or settings.MODELS_PATH
    slug = get_threat_slug(threat_type)
    metrics_path = os.path.join(m_dir, f"{slug}_metrics.json")
    
    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Metrics file for '{threat_type}' not found at: {metrics_path}")
        
    with open(metrics_path, "r") as f:
        return json.load(f)
