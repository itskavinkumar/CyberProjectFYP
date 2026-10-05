import os
import sys
import json
import pytest
import numpy as np
import pandas as pd
from pymongo import MongoClient

# Ensure root paths
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = os.path.join(WORKSPACE_ROOT, "backend")
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app.config import settings
from backend.app.ml.preprocessor import ThreatDataPreprocessor, get_threat_slug
from backend.app.ml.model import build_lstm_model, load_lstm_model, get_model_path
from backend.app.ml.evaluator import (
    calculate_evaluation_metrics,
    calculate_forecast_confidence_intervals,
    load_evaluation_metrics
)
from backend.app.ml.forecast import ThreatForecaster
from backend.app.services.forecast_service import forecast_service

def test_preprocessor_daily_aggregation_and_features():
    """Verify daily aggregation continuity and engineered features."""
    preprocessor = ThreatDataPreprocessor()
    df_raw = preprocessor.load_raw_dataset()
    assert len(df_raw) >= 15000, "Raw dataset should have at least 15,000 records"
    
    daily_matrix = preprocessor.aggregate_daily_threats(df_raw)
    assert len(daily_matrix) == 730, f"Expected 730 continuous days, got {len(daily_matrix)}"
    assert list(daily_matrix.columns) == settings.SUPPORTED_THREAT_TYPES
    
    # Test feature engineering for a specific category
    p_series = daily_matrix["Phishing"]
    features_df = preprocessor.engineer_features_for_category(p_series, df_raw, "Phishing")
    
    expected_cols = [
        "Count", "day_of_week", "day_of_month", "month", "is_weekend",
        "rolling_mean_7", "rolling_std_7", "rolling_mean_14", "rolling_mean_30",
        "lag_1", "lag_7", "lag_14", "ema_7", "daily_change"
    ]
    for col in expected_cols:
        assert col in features_df.columns, f"Missing feature column: {col}"
    assert not features_df["Count"].isna().any(), "Target count should not contain NaNs"
    assert not features_df["rolling_mean_7"].isna().any(), "Rolling mean should not contain NaNs"

def test_sequence_generation_and_scaler():
    """Verify sliding window sequence creation and scaler invertibility."""
    preprocessor = ThreatDataPreprocessor(sequence_length=30)
    synthetic_series = np.sin(np.linspace(0, 50, 200)) * 50 + 100
    
    X_train, y_train, X_test, y_test, scaler = preprocessor.create_sequences(
        series_values=synthetic_series,
        train_ratio=0.8
    )
    
    expected_samples = 200 - 30
    assert len(X_train) + len(X_test) == expected_samples
    assert X_train.shape[1] == 30, "Sequence length should be 30"
    assert X_train.shape[2] == 1, "Feature count should be 1"
    assert y_train.shape[1] == 1, "Target shape should be (samples, 1)"
    
    # Scaler check
    inv_y = scaler.inverse_transform(y_test)
    assert np.allclose(inv_y.ravel(), synthetic_series[len(X_train)+30:], atol=1e-4)

def test_lstm_model_architecture():
    """Verify LSTM architecture specifications, layer count, and shapes."""
    model = build_lstm_model(sequence_length=30, n_features=1)
    
    layer_names = [layer.__class__.__name__ for layer in model.layers]
    assert "LSTM" in layer_names
    assert "Dropout" in layer_names
    assert "Dense" in layer_names
    
    # Verify input and output shapes
    assert model.input_shape == (None, 30, 1)
    assert model.output_shape == (None, 1)
    assert model.optimizer is not None

def test_confidence_interval_calculation():
    """Verify confidence interval bounds expansion and ordering."""
    preds = np.array([50.0, 52.0, 55.0, 58.0, 60.0])
    residual_std = 5.0
    lower, upper = calculate_forecast_confidence_intervals(preds, residual_std, confidence_level=0.95)
    
    assert len(lower) == len(preds)
    assert len(upper) == len(preds)
    for p, l, u in zip(preds, lower, upper):
        assert l <= p, f"Lower bound {l} must be <= prediction {p}"
        assert u >= p, f"Upper bound {u} must be >= prediction {p}"
        assert l >= 0.0, "Lower bound must be non-negative"

def test_all_8_models_and_artifacts_exist_on_disk():
    """Verify that all 8 threat categories have trained models and scalers on disk."""
    assert len(settings.SUPPORTED_THREAT_TYPES) == 8
    
    for threat_type in settings.SUPPORTED_THREAT_TYPES:
        slug = get_threat_slug(threat_type)
        
        # Check model file (.keras)
        model_file = os.path.join(settings.MODELS_PATH, f"{slug}_lstm.keras")
        assert os.path.exists(model_file), f"Model file missing for {threat_type}: {model_file}"
        assert os.path.getsize(model_file) > 10000, f"Model file too small: {model_file}"
        
        # Check scaler file (.joblib)
        scaler_file = os.path.join(settings.MODELS_PATH, f"{slug}_scaler.joblib")
        assert os.path.exists(scaler_file), f"Scaler file missing for {threat_type}: {scaler_file}"
        assert os.path.getsize(scaler_file) > 100, f"Scaler file too small: {scaler_file}"
        
        # Check metrics file (.json)
        metrics_file = os.path.join(settings.MODELS_PATH, f"{slug}_metrics.json")
        assert os.path.exists(metrics_file), f"Metrics file missing for {threat_type}: {metrics_file}"
        with open(metrics_file, "r") as f:
            metrics_data = json.load(f)
            assert "mae" in metrics_data
            assert "rmse" in metrics_data
            assert "mape" in metrics_data
            assert metrics_data["mae"] > 0
            assert metrics_data["rmse"] > 0
            assert metrics_data["mape"] > 0

def test_processed_data_files_exist():
    """Verify that feature-engineered datasets exist in backend/data/processed/."""
    master_summary = os.path.join(settings.PROCESSED_DATA_PATH, "daily_threats_summary.csv")
    assert os.path.exists(master_summary), f"Master summary missing: {master_summary}"
    
    df_summary = pd.read_csv(master_summary)
    assert len(df_summary) == 730
    
    for threat_type in settings.SUPPORTED_THREAT_TYPES:
        slug = get_threat_slug(threat_type)
        cat_file = os.path.join(settings.PROCESSED_DATA_PATH, f"daily_{slug}.csv")
        assert os.path.exists(cat_file), f"Processed category file missing: {cat_file}"

def test_mongodb_models_metadata():
    """Verify that MongoDB 'models' collection has all 8 models registered."""
    client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = client[settings.DATABASE_NAME]
    
    count = db.models.count_documents({})
    assert count == 8, f"Expected 8 models registered in MongoDB, found {count}"
    
    for threat_type in settings.SUPPORTED_THREAT_TYPES:
        doc = db.models.find_one({"threat_type": threat_type})
        assert doc is not None, f"Missing MongoDB model registration for {threat_type}"
        assert doc["model_version"] == "v1.0.0"
        assert doc["status"] == "active"
        assert doc["sequence_length"] == 30
        assert doc["mae"] > 0
        assert doc["rmse"] > 0
        
    client.close()

def test_forecaster_inference_30_days():
    """Verify recursive forecast inference for 30-day horizon."""
    forecaster = ThreatForecaster()
    res = forecaster.forecast("Phishing", forecast_days=30)
    
    assert res["threat_type"] == "Phishing"
    assert res["forecast_days"] == 30
    assert len(res["forecast_data"]) == 30
    assert len(res["historical_data"]) >= 30
    assert res["risk_level"] in ["Low", "Medium", "High", "Critical"]
    assert res["trend_direction"] in ["Increasing", "Stable", "Decreasing"]
    
    # Check forecast points structure
    for pt in res["forecast_data"]:
        assert "date" in pt
        assert "predicted_count" in pt
        assert "lower_bound" in pt
        assert "upper_bound" in pt
        assert pt["predicted_count"] >= 0
        assert pt["lower_bound"] <= pt["upper_bound"]
        assert pt["lower_bound"] <= pt["predicted_count"] + 0.1

def test_forecaster_horizons_and_service():
    """Verify multi-horizon support (7, 14, 30 days) and forecast service."""
    for threat, days in [("Ransomware", 7), ("DDoS", 14), ("Malware", 30)]:
        res = forecast_service.get_forecast(threat, forecast_days=days)
        assert len(res["forecast_data"]) == days
        assert res["threat_type"] == threat

    # Test status check
    statuses = forecast_service.get_all_models_status()
    assert len(statuses) == 8
    for s in statuses:
        assert s["is_trained"] is True
        assert s["model_path"] is not None
        assert s["scaler_path"] is not None
