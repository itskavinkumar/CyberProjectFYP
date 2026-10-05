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
from backend.app.database import get_database
from backend.app.utils.security import hash_password

@pytest.fixture(scope="module")
def client():
    """Module-scoped test client running startup and shutdown lifespans."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def setup_users(client):
    """Seed test admin, analyst, and viewer accounts."""
    db = get_database()
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@soc.test.gov"
    analyst_email = f"analyst_{uuid.uuid4().hex[:6]}@soc.test.gov"
    viewer_email = f"viewer_{uuid.uuid4().hex[:6]}@soc.test.gov"
    pwd = "TestPassword2026!"

    from pymongo import MongoClient
    from datetime import datetime
    sync_client = MongoClient(settings.MONGODB_URI)
    sync_db = sync_client[settings.DATABASE_NAME]

    sync_db.users.insert_one({
        "name": "Super Admin Lead",
        "email": admin_email,
        "password_hash": hash_password(pwd),
        "role": "admin",
        "status": "active",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "last_login_at": None,
        "last_logout_at": None,
        "login_count": 0,
        "failed_login_count": 0
    })
    sync_client.close()

    # Register analyst through public API
    reg_analyst = client.post("/api/auth/register", json={
        "name": "Field Analyst",
        "email": analyst_email,
        "password": pwd,
        "role": "analyst"
    })
    assert reg_analyst.status_code == 201
    analyst_token = reg_analyst.json()["access_token"]

    # Register viewer through public API
    reg_viewer = client.post("/api/auth/register", json={
        "name": "Audit Viewer",
        "email": viewer_email,
        "password": pwd,
        "role": "viewer"
    })
    assert reg_viewer.status_code == 201
    viewer_token = reg_viewer.json()["access_token"]

    # Login admin to obtain token
    admin_login = client.post("/api/auth/login", json={
        "email": admin_email,
        "password": pwd
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    return {
        "admin_email": admin_email,
        "admin_token": admin_token,
        "analyst_email": analyst_email,
        "analyst_token": analyst_token,
        "viewer_email": viewer_email,
        "viewer_token": viewer_token,
        "password": pwd
    }

# ============================================================================
# 1. USER MANAGEMENT TESTS (Feature 1, 8, 9, 10, 11)
# ============================================================================

def test_admin_can_list_users(client, setup_users):
    headers = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "users" in body
    assert body["total"] >= 3
    # Verify password hash is never exposed
    for u in body["users"]:
        assert "password_hash" not in u
        assert "password" not in u
        assert "email" in u
        assert "role" in u
        assert "status" in u

def test_non_admin_cannot_list_users(client, setup_users):
    # Analyst attempt
    res_analyst = client.get("/api/admin/users", headers={"Authorization": f"Bearer {setup_users['analyst_token']}"})
    assert res_analyst.status_code == 403

    # Viewer attempt
    res_viewer = client.get("/api/admin/users", headers={"Authorization": f"Bearer {setup_users['viewer_token']}"})
    assert res_viewer.status_code == 403

    # Unauthenticated attempt
    res_anon = client.get("/api/admin/users")
    assert res_anon.status_code == 401

def test_admin_can_create_user_and_duplicate_rejected(client, setup_users):
    headers = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    new_email = f"provisioned_{uuid.uuid4().hex[:6]}@soc.test.gov"
    create_payload = {
        "name": "Provisioned Operator",
        "email": new_email,
        "password": "PasswordStrong123!",
        "role": "analyst",
        "status": "active"
    }

    # 1. Successful creation
    res = client.post("/api/admin/users", json=create_payload, headers=headers)
    assert res.status_code == 201
    created = res.json()
    assert created["email"] == new_email
    assert created["role"] == "analyst"
    assert created["status"] == "active"
    assert "password_hash" not in created

    # 2. Duplicate email rejected with 409 Conflict
    dup_res = client.post("/api/admin/users", json=create_payload, headers=headers)
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["detail"].lower()

def test_admin_can_change_role_and_non_admin_cannot(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    headers_analyst = {"Authorization": f"Bearer {setup_users['analyst_token']}"}
    target_email = setup_users["viewer_email"]

    # 1. Non-admin cannot change role
    fail_res = client.patch(
        f"/api/admin/users/{target_email}/role",
        json={"role": "analyst"},
        headers=headers_analyst
    )
    assert fail_res.status_code == 403

    # 2. Admin can change role
    ok_res = client.patch(
        f"/api/admin/users/{target_email}/role",
        json={"role": "analyst"},
        headers=headers_admin
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["new_role"] == "analyst"

    # Verify updated via get user details
    detail_res = client.get(f"/api/admin/users/{target_email}", headers=headers_admin)
    assert detail_res.status_code == 200
    assert detail_res.json()["user"]["role"] == "analyst"

def test_admin_can_disable_user_and_disabled_user_cannot_login(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    target_email = setup_users["analyst_email"]
    pwd = setup_users["password"]

    # 1. Disable analyst account
    disable_res = client.patch(
        f"/api/admin/users/{target_email}/status",
        json={"status": "disabled"},
        headers=headers_admin
    )
    assert disable_res.status_code == 200
    assert disable_res.json()["new_status"] == "disabled"
    assert disable_res.json()["is_active"] is False

    # 2. Disabled user login attempt is rejected
    login_attempt = client.post("/api/auth/login", json={
        "email": target_email,
        "password": pwd
    })
    assert login_attempt.status_code == 403
    assert "disabled" in login_attempt.json()["detail"].lower()

    # 3. Re-enable user account
    enable_res = client.patch(
        f"/api/admin/users/{target_email}/status",
        json={"status": "active"},
        headers=headers_admin
    )
    assert enable_res.status_code == 200
    assert enable_res.json()["new_status"] == "active"

    # 4. Login succeeds again
    login_again = client.post("/api/auth/login", json={
        "email": target_email,
        "password": pwd
    })
    assert login_again.status_code == 200

def test_last_admin_protection(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    admin_email = setup_users["admin_email"]

    from pymongo import MongoClient
    sync_client = MongoClient(settings.MONGODB_URI)
    active_admins = sync_client[settings.DATABASE_NAME].users.count_documents({"role": "admin", "status": "active"})
    sync_client.close()
    
    if active_admins == 1:
        # Should reject demoting last admin
        demote_res = client.patch(
            f"/api/admin/users/{admin_email}/role",
            json={"role": "analyst"},
            headers=headers_admin
        )
        assert demote_res.status_code == 400
        assert "final remaining active administrator" in demote_res.json()["detail"]

        # Should reject disabling last admin
        disable_res = client.patch(
            f"/api/admin/users/{admin_email}/status",
            json={"status": "disabled"},
            headers=headers_admin
        )
        assert disable_res.status_code == 400
        assert "final remaining active administrator" in disable_res.json()["detail"]

# ============================================================================
# 2. LOGIN & LOGOUT HISTORY AUDIT TESTS (Feature 3, 4, 5)
# ============================================================================

def test_login_and_logout_audit_trail(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    test_user_email = f"login_audit_{uuid.uuid4().hex[:6]}@soc.test.gov"
    pwd = "AuditPassword123!"

    # Register user
    reg = client.post("/api/auth/register", json={
        "name": "Telemetry Subject",
        "email": test_user_email,
        "password": pwd,
        "role": "analyst"
    })
    assert reg.status_code == 201

    # 1. Failed login increments failed_login_count and logs LOGIN_FAILED
    bad_login = client.post("/api/auth/login", json={
        "email": test_user_email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 2. Successful login updates last_login_at and increments login_count
    good_login = client.post("/api/auth/login", json={
        "email": test_user_email,
        "password": pwd
    })
    assert good_login.status_code == 200
    token = good_login.json()["access_token"]

    # 3. Explicit logout records LOGOUT audit event
    logout_res = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

    # 4. Verify user stats in admin API
    user_detail = client.get(f"/api/admin/users/{test_user_email}", headers=headers_admin)
    assert user_detail.status_code == 200
    u_data = user_detail.json()["user"]
    assert u_data["login_count"] >= 1
    assert u_data["failed_login_count"] >= 1
    assert u_data["last_login_at"] is not None
    assert u_data["last_logout_at"] is not None

    # 5. Verify events in /api/admin/login-history
    hist_res = client.get(
        f"/api/admin/login-history?search={test_user_email}",
        headers=headers_admin
    )
    assert hist_res.status_code == 200
    actions = [e["action"] for e in hist_res.json()["history"]]
    assert "LOGIN_SUCCESS" in actions
    assert "LOGIN_FAILED" in actions
    assert "LOGOUT" in actions

# ============================================================================
# 3. OPERATIONAL AUDIT LOGGING TESTS (Feature 6, 7, 12, 13)
# ============================================================================

def test_forecast_generates_audit_event(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    headers_analyst = {"Authorization": f"Bearer {setup_users['analyst_token']}"}

    # Generate a forecast as analyst
    fc_res = client.post(
        "/api/forecast",
        json={"threat_type": "DDoS", "forecast_days": 14},
        headers=headers_analyst
    )
    assert fc_res.status_code == 200

    # Query audit logs for FORECAST_GENERATED
    logs_res = client.get(
        "/api/admin/audit-logs?action=FORECAST_GENERATED&limit=10",
        headers=headers_admin
    )
    assert logs_res.status_code == 200
    events = logs_res.json()["logs"]
    assert len(events) >= 1
    fc_event = events[0]
    assert fc_event["action"] == "FORECAST_GENERATED"
    assert fc_event["resource_type"] == "forecast"
    assert fc_event["details"]["threat_type"] == "DDoS"
    assert fc_event["details"]["forecast_days"] == 14

def test_dataset_upload_generates_audit_event(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    csv_data = (
        "Date,Threat_Type,Severity,Source,Location,Count,Description\n"
        "2025-10-01,Phishing,High,Email,US,10,Audit verification row\n"
        "2025-10-02,Malware,Critical,EDR,EU,15,Audit verification row\n"
    )
    files = {"file": ("audit_test_dataset.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}

    upload_res = client.post("/api/datasets/upload", files=files, headers=headers_admin)
    assert upload_res.status_code == 201

    # Check audit log
    logs_res = client.get(
        "/api/admin/audit-logs?action=DATASET_UPLOADED&limit=5",
        headers=headers_admin
    )
    assert logs_res.status_code == 200
    dataset_events = logs_res.json()["logs"]
    assert len(dataset_events) >= 1
    assert dataset_events[0]["details"]["filename"] == "audit_test_dataset.csv"

# ============================================================================
# 4. REPORT GENERATION & RBAC TESTS (Feature 14, 25, 28)
# ============================================================================

def test_report_generation_and_role_access(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    headers_analyst = {"Authorization": f"Bearer {setup_users['analyst_token']}"}
    headers_viewer = {"Authorization": f"Bearer {setup_users['viewer_token']}"}

    # 1. Operational report (threat_forecast) accessible to Analyst & Admin
    fc_rep = client.post(
        "/api/reports/generate",
        json={"report_type": "threat_forecast", "parameters": {"threat_type": "Phishing", "forecast_days": 14}},
        headers=headers_analyst
    )
    assert fc_rep.status_code == 201
    rep_data = fc_rep.json()
    assert "report_id" in rep_data
    report_id = rep_data["report_id"]

    # 2. Administrative report (user_activity) forbidden for Analyst & Viewer
    act_fail_analyst = client.post(
        "/api/reports/generate",
        json={"report_type": "user_activity"},
        headers=headers_analyst
    )
    assert act_fail_analyst.status_code == 403

    act_fail_viewer = client.post(
        "/api/reports/generate",
        json={"report_type": "audit_trail"},
        headers=headers_viewer
    )
    assert act_fail_viewer.status_code == 403

    # 3. Administrative report (user_activity) SUCCESS for Admin
    act_ok_admin = client.post(
        "/api/reports/generate",
        json={"report_type": "user_activity"},
        headers=headers_admin
    )
    assert act_ok_admin.status_code == 201
    assert "total_registered_users" in act_ok_admin.json()["summary_data"]

    # 4. Export report as CSV
    export_res = client.get(
        f"/api/reports/{report_id}/export?format=csv",
        headers=headers_analyst
    )
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]

    # 5. Admin report history endpoint
    admin_reps = client.get("/api/admin/reports", headers=headers_admin)
    assert admin_reps.status_code == 200
    assert admin_reps.json()["total"] >= 1

# ============================================================================
# 5. ADMIN DASHBOARD TEST (Feature 15)
# ============================================================================

def test_admin_dashboard_metrics(client, setup_users):
    headers_admin = {"Authorization": f"Bearer {setup_users['admin_token']}"}
    res = client.get("/api/admin/dashboard", headers=headers_admin)
    assert res.status_code == 200
    data = res.json()
    assert data["registered_users"] >= 3
    assert data["active_users"] >= 1
    assert "today_logins" in data
    assert "failed_logins" in data
    assert len(data["recent_logins"]) > 0
    assert len(data["recent_audits"]) > 0
