# Cyber Threat Forecasting & SOC Intelligence System

An enterprise-grade cybersecurity analytics, threat forecasting, and SOC administration platform powered by deep learning (Bidirectional LSTM), FastAPI, MongoDB, and React 19.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |       React 19 + Vite Frontend        |
                      |   (Cyber SOC Command User Interface)  |
                      +---------------------------------------+
                                          |
                                    HTTP / REST
                                          |
                      +---------------------------------------+
                      |         FastAPI REST Backend          |
                      |   (RBAC, JWT, Audit & ML Routing)     |
                      +---------------------------------------+
                           /                             \
                          /                               \
+-----------------------------------+   +------------------------------------+
|    Motor / MongoDB Database       |   | TensorFlow / Keras 3 LSTM Engine   |
| (Users, Audit Logs, Telemetry,    |   | (Recursive multi-horizon 7/14/30d  |
|  Reports, Datasets, Models)       |   |  Forecaster, Residual CI, Scalers) |
+-----------------------------------+   +------------------------------------+
```

---

## Role-Based Access Control (RBAC) System

The platform enforces strict, multi-tiered Role-Based Access Control at both the API layer (FastAPI dependencies with JWT validation) and the user interface.

| Capability / Resource | Administrator (`admin`) | Security Analyst (`analyst`) | Intelligence Auditor (`viewer`) |
| :--- | :---: | :---: | :---: |
| **SOC Overview & Metrics** | Yes | Yes | Yes |
| **AI Threat Forecaster** | Yes | Yes | Yes (Read-Only) |
| **Threat Telemetry Viewer** | Yes | Yes | Yes |
| **Threat Event Ingestion** | Yes | Yes | No |
| **Deep Learning Models Registry**| Yes | Yes | Yes |
| **Dataset Ingestion & Validation**| Yes | Yes | No |
| **Operational Security Reports** | Yes | Yes | Yes (Approved Only) |
| **Administrative & Audit Reports**| Yes | No | No |
| **User & Identity Governance** | Yes | No | No |
| **Authentication & Login Logs** | Yes | No | No |
| **Centralized SOC Audit Trail** | Yes | No | No |
| **Provision User Accounts** | Yes | No | No |
| **Change User Roles** | Yes | No | No |
| **Enable / Disable Accounts** | Yes | No | No |

---

## ADMIN MANAGEMENT & AUDIT TRAIL

### 1. User & Identity Management
Administrators possess dedicated tools to oversee all user identities:
- **Search & Filter**: Search by callsign/name or email; filter by role (`admin`, `analyst`, `viewer`), account status (`active`, `disabled`), and sort by registration date, last login, or login volume.
- **Account Provisioning**: Admins can provision new operator accounts with specified initial roles and statuses (`POST /api/admin/users`).
- **Role Governance**: Dynamic promotion/demotion between `viewer`, `analyst`, and `admin` (`PATCH /api/admin/users/{id}/role`).
- **Last-Admin Protection**: The system automatically prevents demoting or disabling the final remaining active administrator account, mitigating accidental administrative lockout.
- **Status Toggling**: Instant activation or suspension of user accounts (`PATCH /api/admin/users/{id}/status`).
- **User Telemetry Profile**: Inspection modal displaying registration date, last login timestamp, last logout timestamp, total logins, failed logins, and a chronological security activity timeline.

### 2. Login & Session Tracking
Every authentication attempt is intercepted and recorded:
- **`LOGIN_SUCCESS`**: Updates `last_login_at`, increments `login_count`, records IP address and User-Agent client details, and returns the signed JWT token.
- **`LOGIN_FAILED`**: Increments `failed_login_count` on the targeted account, logs the diagnostic failure reason (e.g. `user_not_found`, `invalid_credentials`, or `account_disabled`), and records the IP address.
- **`LOGOUT`**: When an operator signs out, a `LOGOUT` audit record is stored and `last_logout_at` is updated before client token removal.

### 3. Centralized Audit Trail
An immutable audit log (`audit_logs` collection) records all meaningful operational and administrative actions:
- `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`
- `REGISTER` (Public self-registration)
- `USER_CREATED` (Admin-provisioned user)
- `ROLE_CHANGED` (Old role, new role, changed by admin)
- `USER_ENABLED`, `USER_DISABLED`
- `FORECAST_GENERATED` (Threat category, horizon days, risk score, risk level)
- `DATASET_UPLOADED` (Filename, record count, threat types, validation status)
- `DATASET_REJECTED` (Validation errors, filename)
- `REPORT_GENERATED` (Report ID, classification, parameters, title)

All audit events automatically sanitize and omit passwords, password hashes, JWT secrets, and bearer tokens.

### 4. SOC Intelligence Reports & Archives
Operators and Administrators can compile formal security and governance reports:
- **Operational Reports**: `threat_forecast`, `risk_assessment`, `threat_trends`, `model_performance`, `dataset_summary` (accessible to Analysts and Admins).
- **Administrative Reports**: `user_activity` and `audit_trail` (strictly restricted to Administrators).
- **Export Formats**: All reports can be downloaded in structured CSV or JSON formats.

---

## API Reference

### Authentication Endpoints
- `POST /api/auth/register` — Public self-service registration (Analyst and Viewer only; Admin registration blocked with HTTP 403).
- `POST /api/auth/login` — Authenticate operator, update login telemetry, issue JWT bearer token.
- `POST /api/auth/logout` — Close session, update `last_logout_at`, record `LOGOUT` audit log.
- `GET /api/auth/me` — Retrieve active operator profile and status.

### SOC Administration Endpoints (Admin Only)
- `GET /api/admin/dashboard` — High-level SOC metrics (registered users, active, disabled, today's logins, failed logins, today's forecasts, datasets, reports).
- `GET /api/admin/users` — Paginated, searchable, and sortable user account listing.
- `POST /api/admin/users` — Provision a new operator account.
- `GET /api/admin/users/{user_id}` — User profile telemetry and recent activity timeline.
- `PATCH /api/admin/users/{user_id}/role` — Change user role (with Last-Admin Protection).
- `PATCH /api/admin/users/{user_id}/status` — Enable or disable account (with Last-Admin Protection).
- `GET /api/admin/login-history` — Authentication and session audit stream.
- `GET /api/admin/audit-logs` — Centralized security audit log stream.
- `GET /api/admin/audit-logs/{id}` — Single audit event detail inspection.
- `GET /api/admin/activity/{user_id}` — Chronological activity stream for a designated user.
- `GET /api/admin/reports` — Administrative reports archive listing.
- `GET /api/admin/reports/{id}` — Retrieve administrative report details.

### Reports Endpoints
- `POST /api/reports/generate` — Compile and persist an operational or administrative report.
- `GET /api/reports` — List generated reports (filtered by caller's role permissions).
- `GET /api/reports/{id}` — Get report details and executive summary.
- `GET /api/reports/{id}/export` — Export report data as CSV or JSON (`?format=csv` or `?format=json`).

### Operational Threat & Forecast Endpoints
- `GET /api/threats` — List threat events with multi-criteria filtering and pagination.
- `POST /api/threats` — Record a single threat incident (Analyst and Admin).
- `GET /api/threats/summary` — Historical aggregation statistics and severity distribution.
- `POST /api/forecast` — Generate LSTM deep learning threat forecast for specified horizon (7, 14, 30 days).
- `GET /api/forecast/models/status` — Status, disk artifacts, and metrics for all 8 LSTM models.
- `GET /api/datasets` — List ingested cybersecurity datasets.
- `POST /api/datasets/upload` — Ingest and validate CSV dataset (Analyst and Admin).

---

## Database Schemas & Indexes

### Collections & Compound Indexes
- **`users`**: Indexed on `email` (unique), `role`, `status`.
- **`audit_logs`**: Indexed on `timestamp` (descending), `action + timestamp`, `user_id + timestamp`, `email + timestamp`, `status + timestamp`.
- **`reports`**: Indexed on `timestamp` (descending), `generated_by + timestamp`, `report_type + timestamp`.
- **`threat_events`**: Indexed on `date + threat_type`, `threat_type`, `severity`.
- **`forecasts`**: Indexed on `threat_type + forecast_date`.
- **`models`**: Indexed on `threat_type` (unique).

### User Schema Structure
```json
{
  "_id": "ObjectId",
  "name": "Operator Name",
  "email": "operator@soc.defense.gov",
  "password_hash": "$2b$12$...",
  "role": "analyst",
  "status": "active",
  "is_active": true,
  "created_at": "2026-10-01T00:00:00Z",
  "updated_at": "2026-10-05T00:00:00Z",
  "last_login_at": "2026-10-05T12:00:00Z",
  "last_logout_at": "2026-10-05T13:00:00Z",
  "login_count": 27,
  "failed_login_count": 1
}
```

---

## Running the Application

### 1. Start MongoDB
Ensure MongoDB is running locally on port 27017:
```bash
mongod --dbpath <data-path>
```

### 2. Start FastAPI Backend
From the project root:
```bash
.\backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start React Frontend
In a separate terminal:
```bash
cd frontend
npm run dev
```
Navigate to `http://localhost:5173/` in your browser.

### 4. Running the Test Suite
Execute the full test suite covering ML, LSTM forecasting, RBAC, Admin Management, Login Tracking, and Audit Trails:
```bash
.\backend\venv\Scripts\python.exe -m pytest backend/tests/test_phase1.py backend/tests/test_phase2.py backend/tests/test_phase3.py backend/tests/test_admin_audit_rbac.py
```
Execute the live end-to-end integration workflow:
```bash
.\backend\venv\Scripts\python.exe backend/tests/verify_admin_e2e_workflow.py
```
