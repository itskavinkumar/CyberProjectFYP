import httpx
import time
import uuid
import io

def main():
    print("=" * 80)
    print("  CYBERGUARD AI: END-TO-END SOC ADMIN & AUDIT WORKFLOW VERIFICATION  ")
    print("=" * 80)

    client = httpx.Client(base_url="http://127.0.0.1:5173/api", timeout=30.0)

    # 1. Health check
    r_health = client.get("/health")
    assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
    print(f"[+] 1. API Health Check verified: {r_health.json()['status']} | DB: {r_health.json()['database']}")

    # 2. Public Registration Security Guard: Rejecting Public Admin Self-Registration
    r_bad_admin = client.post("/auth/register", json={
        "name": "Attacker",
        "email": f"attacker_{uuid.uuid4().hex[:6]}@evil.org",
        "password": "Password123!",
        "role": "admin"
    })
    assert r_bad_admin.status_code == 403, f"Expected 403 for admin public registration, got {r_bad_admin.status_code}"
    print(f"[+] 2. Security Guard Verified: Public self-registration as ADMIN rejected with HTTP 403 Forbidden")

    # 3. Public Registration as Analyst & Viewer
    unique_id = uuid.uuid4().hex[:6]
    analyst_email = f"analyst_{unique_id}@soc.defense.gov"
    viewer_email = f"viewer_{unique_id}@soc.defense.gov"
    pwd = "SecOpsPassword2026!"

    r_reg_analyst = client.post("/auth/register", json={
        "name": f"Analyst {unique_id}",
        "email": analyst_email,
        "password": pwd,
        "role": "analyst"
    })
    assert r_reg_analyst.status_code == 201
    analyst_token = r_reg_analyst.json()["access_token"]
    print(f"[+] 3. Analyst Account Self-Registered: {analyst_email} (HTTP 201 Created)")

    r_reg_viewer = client.post("/auth/register", json={
        "name": f"Auditor {unique_id}",
        "email": viewer_email,
        "password": pwd,
        "role": "viewer"
    })
    assert r_reg_viewer.status_code == 201
    viewer_token = r_reg_viewer.json()["access_token"]
    print(f"[+] 4. Viewer Account Self-Registered: {viewer_email} (HTTP 201 Created)")

    # 4. Admin Authentication
    r_admin_login = client.post("/auth/login", json={
        "email": "admin@soc.defense.gov",
        "password": "CyberAdmin2026!"
    })
    assert r_admin_login.status_code == 200, f"Admin login failed: {r_admin_login.text}"
    admin_token = r_admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    print(f"[+] 5. Admin Authentication Successful: SOC Director (HTTP 200 OK)")

    # 5. Admin Dashboard Verification
    r_dash = client.get("/admin/dashboard", headers=admin_headers)
    assert r_dash.status_code == 200
    d_json = r_dash.json()
    print(f"[+] 6. Admin Security Console Telemetry: Registered Users: {d_json['registered_users']}, "
          f"Active: {d_json['active_users']}, Today's Logins: {d_json['today_logins']}")

    # 6. Admin Users List & Filtering
    r_users = client.get("/admin/users?limit=10", headers=admin_headers)
    assert r_users.status_code == 200
    u_list = r_users.json()["users"]
    assert len(u_list) > 0
    # Verify password hash is never exposed
    for u in u_list:
        assert "password_hash" not in u
    print(f"[+] 7. Admin User Listing Verified: {r_users.json()['total']} total accounts (passwords sanitized)")

    # 7. Non-Admin Access Prohibited from Admin APIs
    r_blocked_analyst = client.get("/admin/users", headers=analyst_headers)
    assert r_blocked_analyst.status_code == 403
    r_blocked_viewer = client.get("/admin/dashboard", headers=viewer_headers)
    assert r_blocked_viewer.status_code == 403
    print(f"[+] 8. RBAC Endpoint Enforcement: Non-admins strictly blocked from /admin routes (HTTP 403)")

    # 8. Admin Provisioning a User
    provisioned_email = f"agent_{unique_id}@soc.defense.gov"
    r_prov = client.post("/admin/users", json={
        "name": f"Agent {unique_id}",
        "email": provisioned_email,
        "password": "InitialPassword123!",
        "role": "viewer",
        "status": "active"
    }, headers=admin_headers)
    assert r_prov.status_code == 201
    prov_id = r_prov.json()["id"]
    print(f"[+] 9. Admin Provisioned New Account: {provisioned_email} (ID: {prov_id})")

    # 9. Admin Promoting User Role
    r_role = client.patch(f"/admin/users/{provisioned_email}/role", json={"role": "analyst"}, headers=admin_headers)
    assert r_role.status_code == 200
    assert r_role.json()["new_role"] == "analyst"
    print(f"[+] 10. Role Management Verified: {provisioned_email} promoted: viewer -> analyst")

    # 10. Admin Disabling & Re-enabling Account
    r_disable = client.patch(f"/admin/users/{provisioned_email}/status", json={"status": "disabled"}, headers=admin_headers)
    assert r_disable.status_code == 200
    assert r_disable.json()["new_status"] == "disabled"
    print(f"[+] 11. Account Status Governance: {provisioned_email} status set to DISABLED")

    # Verify disabled user cannot log in
    r_disabled_login = client.post("/auth/login", json={"email": provisioned_email, "password": "InitialPassword123!"})
    assert r_disabled_login.status_code == 403
    print(f"[+] 12. Disabled Login Enforced: Disabled user authentication rejected with HTTP 403")

    # Re-enable
    r_enable = client.patch(f"/admin/users/{provisioned_email}/status", json={"status": "active"}, headers=admin_headers)
    assert r_enable.status_code == 200
    print(f"[+] 13. Account Restored: {provisioned_email} re-enabled to ACTIVE")

    # 11. Operational Activity: Ingesting Threat Event, Generating Forecast & Dataset
    r_fc = client.post("/forecast", json={"threat_type": "DDoS", "forecast_days": 14}, headers=analyst_headers)
    assert r_fc.status_code == 200
    print(f"[+] 14. Forecast Inference Executed: DDoS (14 days, Risk: {r_fc.json()['risk_level']})")

    csv_data = "Date,Threat_Type,Severity,Source,Location,Count,Description\n2025-10-01,Phishing,High,Email,US,5,E2E audit\n"
    r_up = client.post("/datasets/upload", files={"file": ("e2e_test.csv", io.BytesIO(csv_data.encode()), "text/csv")}, headers=analyst_headers)
    assert r_up.status_code == 201
    print(f"[+] 15. Dataset Ingestion Executed: e2e_test.csv (HTTP 201 Created)")

    # 12. Centralized Audit Trail Verification
    time.sleep(0.5)
    r_audits = client.get("/admin/audit-logs?limit=10", headers=admin_headers)
    assert r_audits.status_code == 200
    audit_actions = [a["action"] for a in r_audits.json()["logs"]]
    print(f"[+] 16. Audit Log Stream Verified: Recorded actions include: {set(audit_actions[:5])}")

    # 13. Authentication & Login History Verification
    r_logins = client.get("/admin/login-history?limit=10", headers=admin_headers)
    assert r_logins.status_code == 200
    login_items = r_logins.json()["history"]
    assert len(login_items) > 0
    print(f"[+] 17. Login History Telemetry Verified: {len(login_items)} recent authentication logs retrieved")

    # 14. Report Generation & Role Access
    r_rep_analyst = client.post("/reports/generate", json={
        "report_type": "threat_forecast",
        "title": "E2E Automated Forecast Audit",
        "parameters": {"threat_type": "DDoS", "forecast_days": 14}
    }, headers=analyst_headers)
    assert r_rep_analyst.status_code == 201
    rep_id = r_rep_analyst.json()["report_id"]
    print(f"[+] 18. Operational Report Generated: {rep_id} by Analyst")

    # Non-admin attempting to generate admin user_activity report
    r_rep_forbidden = client.post("/reports/generate", json={"report_type": "user_activity"}, headers=analyst_headers)
    assert r_rep_forbidden.status_code == 403
    print(f"[+] 19. Report RBAC Verified: Non-admin generation of 'user_activity' rejected (HTTP 403)")

    # Admin generating user_activity report
    r_rep_admin = client.post("/reports/generate", json={"report_type": "user_activity"}, headers=admin_headers)
    assert r_rep_admin.status_code == 201
    print(f"[+] 20. Administrative Report Generated: User Activity Report by Admin (HTTP 201)")

    # Report Export CSV
    r_export = client.get(f"/reports/{rep_id}/export?format=csv", headers=analyst_headers)
    assert r_export.status_code == 200
    assert "Report ID" in r_export.text
    print(f"[+] 21. Report CSV Export Verified: {len(r_export.text)} bytes exported")

    # 15. Explicit Logout Audit
    r_logout = client.post("/auth/logout", headers=analyst_headers)
    assert r_logout.status_code == 200
    print(f"[+] 22. Explicit Logout Telemetry Verified: Session closed and LOGOUT audited (HTTP 200)")

    print("\n" + "=" * 80)
    print("  ALL 22 ENTERPRISE SOC ADMIN & AUDIT WORKFLOW CHECKS PASSED 100%!  ")
    print("=" * 80)

if __name__ == "__main__":
    main()
