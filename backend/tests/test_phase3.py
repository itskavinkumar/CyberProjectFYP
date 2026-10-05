import os
import sys
import io
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure root paths
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = os.path.join(WORKSPACE_ROOT, "backend")
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app.main import app
from backend.app.config import settings

@pytest.fixture(scope="module")
def client():
    """Module-scoped test client running startup and shutdown lifespans."""
    with TestClient(app) as test_client:
        yield test_client

# ============================================================================
# 1. Authentication & Security Tests
# ============================================================================

def test_auth_registration_success_and_duplicate(client):
    unique_email = f"analyst_{uuid.uuid4().hex[:8]}@soc.defense.gov"
    payload = {
        "name": "SOC Cyber Lead",
        "email": unique_email,
        "password": "SecurePassword123!",
        "role": "analyst"
    }
    
    # 1. Successful registration
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "analyst"

    # 2. Duplicate registration attempt should be rejected
    dup_res = client.post("/api/auth/register", json=payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

def test_auth_login_success_and_invalid_credentials(client):
    email = f"user_{uuid.uuid4().hex[:8]}@enterprise.net"
    password = "CorrectPassword123"
    
    # Register first
    client.post("/api/auth/register", json={
        "name": "Threat Hunter",
        "email": email,
        "password": password,
        "role": "analyst"
    })
    
    # Successful login
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == email

    # Invalid password login
    bad_login = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword"})
    assert bad_login.status_code == 401
    assert "invalid" in bad_login.json()["detail"].lower()

    # Nonexistent user login
    ghost_login = client.post("/api/auth/login", json={"email": "nobody@cyber.org", "password": password})
    assert ghost_login.status_code == 401

def test_auth_protected_me_and_invalid_token(client):
    email = f"auth_test_{uuid.uuid4().hex[:8]}@soc.mil"
    reg = client.post("/api/auth/register", json={
        "name": "Intelligence Officer",
        "email": email,
        "password": "Password123!",
        "role": "analyst"
    })
    token = reg.json()["access_token"]

    # 1. Valid token accessing /api/auth/me
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    user_info = res.json()
    assert user_info["email"] == email
    assert user_info["name"] == "Intelligence Officer"
    assert user_info["role"] == "analyst"

    # 2. Missing authorization header
    unauth = client.get("/api/auth/me")
    assert unauth.status_code == 401

    # 3. Forged/invalid token
    bad_token = client.get("/api/auth/me", headers={"Authorization": "Bearer totally_fake_token_value"})
    assert bad_token.status_code == 401

# ============================================================================
# 2. Threat Events Ingestion & Query Tests
# ============================================================================

def test_threats_list_and_filters(client):
    # Fetch default list
    res = client.get("/api/threats?limit=25")
    assert res.status_code == 200
    body = res.json()
    assert "total" in body
    assert body["total"] >= 15000
    assert len(body["data"]) == 25

    # Filter by threat category
    res_phish = client.get("/api/threats?threat_type=Phishing&limit=10")
    assert res_phish.status_code == 200
    for item in res_phish.json()["data"]:
        assert item["threat_type"] == "Phishing"

    # Filter by severity
    res_crit = client.get("/api/threats?severity=Critical&limit=10")
    assert res_crit.status_code == 200
    for item in res_crit.json()["data"]:
        assert item["severity"] == "Critical"

def test_threats_create_valid_and_invalid(client):
    # 1. Valid threat event creation
    valid_payload = {
        "date": "2025-11-15",
        "threat_type": "DDoS",
        "severity": "Critical",
        "source": "BGP-Scrubbing-Sensor",
        "location": "Asia-Pacific",
        "count": 45,
        "description": "Volumetric SYN amplification surge flagged by perimeter IDS"
    }
    create_res = client.post("/api/threats", json=valid_payload)
    assert create_res.status_code == 201
    created_item = create_res.json()
    assert "id" in created_item
    assert created_item["threat_type"] == "DDoS"
    assert created_item["count"] == 45

    # 2. Invalid threat type
    invalid_threat = valid_payload.copy()
    invalid_threat["threat_type"] = "AlienInvasion"
    assert client.post("/api/threats", json=invalid_threat).status_code == 400

    # 3. Invalid severity
    invalid_sev = valid_payload.copy()
    invalid_sev["severity"] = "UltraExtreme"
    assert client.post("/api/threats", json=invalid_sev).status_code == 400

    # 4. Invalid date format
    invalid_date = valid_payload.copy()
    invalid_date["date"] = "15/11/2025"
    assert client.post("/api/threats", json=invalid_date).status_code == 400

def test_threats_summary_and_categories(client):
    # Summary test
    res = client.get("/api/threats/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_events"] > 0
    assert summary["category_count"] == 8
    assert len(summary["threat_counts"]) == 8
    assert "Critical" in summary["severity_distribution"]
    assert summary["most_frequent_threat"] is not None

    # Categories test
    cat_res = client.get("/api/threats/categories")
    assert cat_res.status_code == 200
    cat_body = cat_res.json()
    assert len(cat_body["supported_threat_types"]) == 8
    assert "Phishing" in cat_body["supported_threat_types"]
    assert "Critical" in cat_body["allowed_severities"]

# ============================================================================
# 3. LSTM Threat Forecasting Tests
# ============================================================================

def test_forecast_endpoint_30_days_post(client):
    payload = {
        "threat_type": "Phishing",
        "forecast_days": 30
    }
    res = client.post("/api/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["threat_type"] == "Phishing"
    assert data["forecast_days"] == 30
    assert len(data["forecast_data"]) == 30
    assert len(data["historical_data"]) >= 30
    assert data["risk_level"] in ["Low", "Medium", "High", "Critical"]
    assert data["trend_direction"] in ["Increasing", "Stable", "Decreasing"]
    assert "peak_forecast_count" in data["summary_stats"]
    assert "mae" in data["evaluation_metrics"]

def test_forecast_endpoint_get_by_path_multi_horizon(client):
    # Test 7 days on Ransomware
    res_7 = client.get("/api/forecast/Ransomware?days=7")
    assert res_7.status_code == 200
    assert len(res_7.json()["forecast_data"]) == 7

    # Test 14 days on DDoS
    res_14 = client.get("/api/forecast/DDoS?days=14")
    assert res_14.status_code == 200
    assert len(res_14.json()["forecast_data"]) == 14

def test_forecast_invalid_inputs(client):
    # Unsupported category
    res_bad_cat = client.post("/api/forecast", json={"threat_type": "NoSuchThreat", "forecast_days": 30})
    assert res_bad_cat.status_code == 400

    # Horizon out of bounds (> 90)
    res_bad_days = client.post("/api/forecast", json={"threat_type": "Malware", "forecast_days": 200})
    assert res_bad_days.status_code == 422 or res_bad_days.status_code == 400

def test_forecast_models_status(client):
    res = client.get("/api/forecast/models/status")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 8
    for m in body["models"]:
        assert m["is_trained"] is True
        assert m["model_path"] is not None
        assert m["metrics"] is not None
        assert m["metrics"]["mae"] > 0

# ============================================================================
# 4. Datasets Ingestion & Validation Tests
# ============================================================================

def test_dataset_upload_valid_csv(client):
    csv_content = (
        "Date,Threat_Type,Severity,Source,Location,Count,Description\n"
        "2025-10-01,Phishing,High,Email-Gateway,North America,15,Credential phishing surge\n"
        "2025-10-02,Malware,Critical,EDR-Agent,Europe,22,Ransomware dropper detected\n"
        "2025-10-03,Brute Force,Medium,SSH-Auth,Global,40,High-frequency credential stuffing\n"
    )
    file_obj = io.BytesIO(csv_content.encode("utf-8"))
    files = {"file": ("test_upload_dataset.csv", file_obj, "text/csv")}

    res = client.post("/api/datasets/upload", files=files)
    assert res.status_code == 201
    body = res.json()
    assert body["is_valid"] is True
    assert body["number_of_records"] == 3
    assert "dataset_id" in body

def test_dataset_upload_invalid_csv_missing_columns(client):
    bad_csv = "Timestamp,AttackType\n2025-01-01,SQLi\n"
    file_obj = io.BytesIO(bad_csv.encode("utf-8"))
    files = {"file": ("broken_dataset.csv", file_obj, "text/csv")}

    res = client.post("/api/datasets/upload", files=files)
    assert res.status_code == 400
    assert "validation failed" in res.json()["detail"]["message"].lower()

def test_dataset_upload_non_csv_rejected(client):
    txt_content = "This is not a CSV file."
    file_obj = io.BytesIO(txt_content.encode("utf-8"))
    files = {"file": ("notes.txt", file_obj, "text/plain")}

    res = client.post("/api/datasets/upload", files=files)
    assert res.status_code == 400

def test_dataset_listing_and_inspection(client):
    res = client.get("/api/datasets")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    
    # Inspect synthetic dataset
    inspect_res = client.get("/api/datasets/synthetic_threat_events.csv")
    assert inspect_res.status_code == 200
    assert inspect_res.json()["filename"] == "synthetic_threat_events.csv"

# ============================================================================
# 5. Analytics & SOC Dashboard Tests
# ============================================================================

def test_analytics_soc_overview_and_risk_matrix(client):
    # Overview
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_threat_events"] > 0
    assert data["threat_categories_count"] == 8
    assert len(data["threat_distribution"]) == 8
    assert len(data["severity_distribution"]) > 0
    assert len(data["daily_trend"]) > 0
    assert len(data["risk_indicators"]) == 8
    for ri in data["risk_indicators"]:
        assert ri["risk_level"] in ["Low", "Medium", "High", "Critical"]
        assert 0.0 <= ri["risk_score"] <= 100.0
        assert len(ri["contributing_factors"]) > 0

    # Risk matrix
    matrix_res = client.get("/api/analytics/risk-matrix")
    assert matrix_res.status_code == 200
    matrix = matrix_res.json()
    for level in ["Critical", "High", "Medium", "Low"]:
        assert level in matrix
