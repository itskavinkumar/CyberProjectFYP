import os
from typing import Dict, Any, List, Optional

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.forecast import ThreatForecaster
from backend.app.ml.preprocessor import get_threat_slug
from backend.app.ml.evaluator import load_evaluation_metrics

class ForecastService:
    """Service layer coordinating forecasting inference and model statuses."""

    def __init__(self):
        self.forecaster = ThreatForecaster()

    def get_forecast(self, threat_type: str, forecast_days: int = 30) -> Dict[str, Any]:
        """Generate time-series forecast for given threat category and horizon."""
        return self.forecaster.forecast(threat_type=threat_type, forecast_days=forecast_days)

    def get_model_status(self, threat_type: str) -> Dict[str, Any]:
        """Check if model and scaler artifacts exist for threat type."""
        slug = get_threat_slug(threat_type)
        model_file = os.path.join(settings.MODELS_PATH, f"{slug}_lstm.keras")
        scaler_file = os.path.join(settings.MODELS_PATH, f"{slug}_scaler.joblib")
        metrics_file = os.path.join(settings.MODELS_PATH, f"{slug}_metrics.json")
        
        exists = os.path.exists(model_file) and os.path.exists(scaler_file)
        metrics = None
        if os.path.exists(metrics_file):
            try:
                metrics = load_evaluation_metrics(threat_type)
            except Exception:
                pass
                
        return {
            "threat_type": threat_type,
            "is_trained": exists,
            "model_path": model_file if exists else None,
            "scaler_path": scaler_file if exists else None,
            "metrics": metrics
        }

    def get_all_models_status(self) -> List[Dict[str, Any]]:
        """Return status and metrics for all 8 supported threat categories."""
        return [self.get_model_status(t) for t in settings.SUPPORTED_THREAT_TYPES]

forecast_service = ForecastService()
