from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_GREEN,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_06():
    story = []

    # =========================================================================
    # 18. BACKEND ARCHITECTURE & FASTAPI ENGINE
    # =========================================================================
    story.append(Paragraph("18. BACKEND ARCHITECTURE & FASTAPI ENGINE", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The backend is constructed as a modern, high-concurrency asynchronous API utilizing Python 3.11, "
        "FastAPI 0.109, and Uvicorn 0.27. The architecture strictly follows a layered service pattern, separating "
        "HTTP serialization, business routing, domain services, machine learning inference, and database persistence:",
        BodyStyle
    ))

    backend_layers = [
        ("API Gateway & Lifespan Layer (`main.py`):", 
         "Manages the application lifecycle via `@asynccontextmanager def lifespan(app)`. Initiates the Motor client "
         "connection pool to MongoDB and creates compound indexes before accepting inbound traffic. "
         "Guarantees that on process termination, all database connections close gracefully without leaking sockets."),
        
        ("CORS & Request Timing Middleware:",
         "Enforces cross-origin resource sharing policies via `CORSMiddleware`, permitting requests from localhost:5173 (Vite) "
         "and localhost:3000. Custom HTTP middleware measures precise request duration and outputs standardized logs: "
         "`POST /api/forecast -> Status 200 (0.018s)`."),
        
        ("Global Exception Handling:",
         "Binds `@app.exception_handler(Exception)` to catch unexpected runtime errors (e.g., missing model files or database dropouts), "
         "logging full stack traces while returning sanitized JSON responses to clients: `{success: false, error: '...', detail: '...'}`."),
        
        ("Schema Validation via Pydantic v2 (`schemas.py`):",
         "Strictly parses every incoming HTTP request payload. Type coercion, boundary checks (e.g., `forecast_days` between 1 and 90), "
         "and email syntax enforcement are executed at the C/Rust extension speed of Pydantic v2 before router code executes."),
        
        ("Dependency Injection & Security (`security.py`):",
         "Implements reusable FastAPI dependencies: `get_current_user` extracts and decodes signed JWT Bearer tokens from request headers; "
         "`require_role(['admin'])` provides declarative role-based access control (RBAC) across protected endpoints.")
    ]
    for b_title, b_desc in backend_layers:
        story.append(Paragraph(f"• <b>{b_title}</b> {b_desc}", BulletStyle))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 19. COMPLETE REST API CATALOGUE & SPECIFICATION
    # =========================================================================
    story.append(Paragraph("19. COMPLETE REST API SPECIFICATION", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Every endpoint in the system was verified directly against the router source code files "
        "(`auth.py`, `threats.py`, `forecast.py`, `datasets.py`, `analytics.py`, `main.py`). "
        "The complete 18-route API catalogue is detailed below:",
        BodyStyle
    ))

    api_catalog = [
        ["Method", "Endpoint Route", "Auth Required", "Request Body / Parameters", "HTTP Response Summary & Status"],
        ["GET", "/", "Public", "None", "200: {project, version, status, docs: '/api/docs'}"],
        ["GET", "/api/health", "Public", "None", "200: {status: 'healthy', database: 'connected', version}"],
        ["GET", "/docs, /redoc", "Public", "None", "307: Redirects to /api/docs or /api/redoc"],
        ["POST", "/api/auth/register", "Public", "JSON: {name, email, password, role}", "201: {access_token, token_type, user: {id, email, role}}"],
        ["POST", "/api/auth/login", "Public", "JSON: {email, password}", "200: {access_token, token_type, user: {id, email, role}}"],
        ["POST", "/api/auth/token", "Public", "Form: username, password (OAuth2)", "200: TokenResponse for Swagger UI authorization dialog"],
        ["GET", "/api/auth/me", "Bearer JWT", "Header: Authorization: Bearer <token>", "200: {id, name, email, role} of current authenticated user"],
        ["GET", "/api/threats", "Public", "Query: threat_type, severity, start, end, limit, skip", "200: {total, limit, skip, count, data: [ThreatEvent]}"],
        ["POST", "/api/threats", "Public", "JSON: {date, threat_type, severity, count, source, ...}", "201: Newly created threat event document with assigned ID"],
        ["GET", "/api/threats/summary", "Public", "None", "200: Aggregated totals, category distribution, severity breakdown"],
        ["GET", "/api/threats/categories", "Public", "None", "200: Supported categories (8), severities (4), default horizons"],
        ["POST", "/api/forecast", "Public", "JSON: {threat_type, forecast_days (1-90)}", "200: ForecastResponse with 30 hist points, forecast points, risk"],
        ["GET", "/api/forecast/{threat}", "Public", "Path: threat_type, Query: days (1-90)", "200: ForecastResponse (path proxy to POST /api/forecast)"],
        ["GET", "/api/forecast/models/status", "Public", "None", "200: Status and disk verification of all 8 LSTM models & metrics"],
        ["POST", "/api/datasets/upload", "Public", "Multipart File: .csv dataset", "201: Ingestion report, records count, detected threat types"],
        ["GET", "/api/datasets", "Public", "None", "200: List of all registered datasets in MongoDB"],
        ["GET", "/api/datasets/{id}", "Public", "Path: dataset_id, filename, or ObjectId", "200: Dataset metadata, date range, validation summary"],
        ["GET", "/api/analytics/overview", "Public", "None (300s cache)", "200: Executive SOC metrics, 60d daily timeline, 8 risk indicators"],
        ["GET", "/api/analytics/risk-matrix", "Public", "None", "200: Priority matrix grouped by Critical, High, Medium, Low"]
    ]
    story.append(create_table(
        api_catalog[0],
        api_catalog[1:],
        col_widths=[45, 125, 65, 145, 156],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 10))

    # Core JSON Payload Structure
    story.append(Paragraph("Core Forecast API Payload Structure (`POST /api/forecast`)", Heading2Style))
    
    sample_json = (
        "// Request Payload (POST /api/forecast)\n"
        "{\n"
        '  "threat_type": "DDoS",\n'
        '  "forecast_days": 14\n'
        "}\n"
        "\n"
        "// Response Envelope (HTTP 200 OK)\n"
        "{\n"
        '  "threat_type": "DDoS",\n'
        '  "forecast_days": 14,\n'
        '  "model_name": "DDoS LSTM Forecaster",\n'
        '  "model_version": "v1.0.0",\n'
        '  "evaluation_metrics": { "mae": 46.20, "rmse": 92.12, "mape": 31.16, "r2_score": 0.446 },\n'
        '  "historical_data": [\n'
        '    { "date": "2025-12-01", "count": 135.0 },\n'
        '    { "date": "2025-12-30", "count": 148.0 }\n'
        '  ],\n'
        '  "forecast_data": [\n'
        '    { "date": "2025-12-31", "predicted_count": 154.2, "lower_bound": 110.4, "upper_bound": 198.0 },\n'
        '    { "date": "2026-01-13", "predicted_count": 210.8, "lower_bound": 142.1, "upper_bound": 279.5 }\n'
        '  ],\n'
        '  "summary_stats": {\n'
        '    "avg_historical_count": 137.97, "avg_forecast_count": 182.4,\n'
        '    "predicted_change_pct": 32.2, "peak_forecast_date": "2026-01-11",\n'
        '    "peak_forecast_count": 245.0, "risk_score": 78.5\n'
        '  },\n'
        '  "risk_level": "Critical",\n'
        '  "trend_direction": "Increasing"\n'
        "}"
    )
    story.append(create_code_block(sample_json, caption="Canonical Forecast Request & Response Schema"))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 20. DATABASE ARCHITECTURE: MONGODB COLLECTIONS & INDEXES
    # =========================================================================
    story.append(Paragraph("20. DATABASE ARCHITECTURE & MONGODB COLLECTIONS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The platform utilizes MongoDB (database name: `cyber_threat_forecast`) accessed non-blockingly via Motor. "
        "Five enterprise collections are maintained, with compound indexes initialized automatically at boot time "
        "in `backend/app/database.py:init_db_indexes()`:",
        BodyStyle
    ))

    collections_spec = [
        ["Collection Name", "Primary Purpose", "Key Document Fields", "Indexes Maintained", "Read / Write Pattern"],
        ["threat_events", "Raw and ingested incident logs", "date, threat_type, severity, count, source, location, dataset_id", "Compound: (date: 1, threat_type: 1), (threat_type: 1), (severity: 1)", "High-speed paginated queries and daily group-by aggregations."],
        ["forecasts", "Inference cache and audit log", "threat_type, forecast_date, predicted_count, lower_bound, upper_bound, horizon_days", "Compound: (threat_type: 1, forecast_date: 1)", "Upserted upon forecast generation; queried for historical forecast review."],
        ["datasets", "Registry of ingested CSV datasets", "dataset_id, filename, upload_date, number_of_records, date_range, threat_types", "(None / default _id)", "Queried by DatasetsView to display file inventory and validation status."],
        ["models", "Model registry & training metrics", "threat_type, model_name, training_records, sequence_length, mae, rmse, r2, status", "Unique: (threat_type: 1)", "Updated by LSTMTrainer upon training completion; read by ModelsView."],
        ["users", "SOC operator credentials & RBAC", "name, email, password_hash, role (analyst, admin, viewer), created_at", "Unique: (email: 1)", "Queried during login/registration; validated on protected routes."]
    ]
    story.append(create_table(
        collections_spec[0],
        collections_spec[1:],
        col_widths=[75, 110, 135, 110, 106],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 21. AUTHENTICATION & SECURITY IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("21. AUTHENTICATION & CRYPTOGRAPHIC SECURITY", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The security subsystem (`backend/app/utils/security.py`) enforces strict cryptographic safeguards:",
        BodyStyle
    ))

    auth_specs = [
        ("Password Hashing via Direct bcrypt:", 
         "Passwords are never stored in plaintext. In `hash_password()`, plaintext strings are UTF-8 encoded, "
         "truncated to 72 bytes (the maximum bcrypt input boundary), salted with 12 rounds of adaptive cost (`bcrypt.gensalt(12)`), "
         "and hashed via `bcrypt.hashpw()`. Verification uses `bcrypt.checkpw()` to prevent timing attacks."),
        
        ("JSON Web Token (JWT) Generation:",
         "Upon successful authentication, `create_access_token()` creates an RFC 7519 signed JWT token using HMAC-SHA256 (`HS256`). "
         "The token payload contains: `sub` (user email), `role` (analyst/admin), and `exp` (UTC timestamp set to 24 hours via `ACCESS_TOKEN_EXPIRE_MINUTES = 1440`)."),
        
        ("Bearer Authentication Interception:",
         "The React frontend stores the issued JWT in `localStorage`. In `frontend/src/api.js`, every outgoing request checks "
         "`getAuthToken()` and automatically injects the `Authorization: Bearer <token>` header."),
        
        ("Role-Based Access Control (RBAC):",
         "The system defines three authorized roles: (1) <b>analyst:</b> standard operational access to view telemetry, generate forecasts, and log incidents, "
         "(2) <b>admin:</b> elevated privileges capable of uploading datasets and retraining models, and (3) <b>viewer:</b> read-only intelligence audit access. "
         "The `require_role(['admin'])` decorator factory enforces endpoint restrictions declarative.")
    ]
    for a_title, a_desc in auth_specs:
        story.append(Paragraph(f"• <b>{a_title}</b> {a_desc}", BulletStyle))
        story.append(Spacer(1, 2))

    story.append(PageBreak())
    return story
