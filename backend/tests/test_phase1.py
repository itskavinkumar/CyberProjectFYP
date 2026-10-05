import os
import sys
import pytest
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
from backend.app.utils.validation import validate_csv_dataset, validate_threat_type, validate_forecast_horizon
from backend.app.main import app

def test_settings_and_categories():
    assert len(settings.SUPPORTED_THREAT_TYPES) == 8
    assert "Phishing" in settings.SUPPORTED_THREAT_TYPES
    assert "Ransomware" in settings.SUPPORTED_THREAT_TYPES
    assert validate_threat_type("DDoS") is True
    assert validate_threat_type("FakeThreat") is False
    assert validate_forecast_horizon(7) is True
    assert validate_forecast_horizon(30) is True
    assert validate_forecast_horizon(100) is False

def test_synthetic_csv_data():
    csv_path = os.path.join(settings.RAW_DATA_PATH, "synthetic_threat_events.csv")
    assert os.path.exists(csv_path), f"File {csv_path} does not exist"
    
    df = pd.read_csv(csv_path)
    assert len(df) >= 15000, f"Expected >= 15000 records, got {len(df)}"
    
    is_valid, errors, summary = validate_csv_dataset(df)
    assert is_valid is True, f"Validation failed with errors: {errors}"
    assert len(summary["threat_types_found"]) == 8
    assert set(summary["severities_found"]) == {"Low", "Medium", "High", "Critical"}

def test_mongodb_connection_and_data():
    client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = client[settings.DATABASE_NAME]
    
    # Check count
    count = db.threat_events.count_documents({})
    assert count >= 15000, f"Expected >= 15000 documents in threat_events, found {count}"
    
    # Check distinct threat types
    threat_types = db.threat_events.distinct("threat_type")
    assert len(threat_types) == 8
    
    # Check dataset registry
    dataset_entry = db.datasets.find_one({"filename": "synthetic_threat_events.csv"})
    assert dataset_entry is not None
    assert dataset_entry["processing_status"] == "processed"
    
    client.close()

def test_fastapi_app_routes():
    route_paths = [route.path for route in app.routes]
    assert "/" in route_paths
    assert "/api/health" in route_paths
