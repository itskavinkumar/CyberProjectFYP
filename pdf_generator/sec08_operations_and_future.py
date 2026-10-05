from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_diagram, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_AMBER, ACCENT_ROSE, ACCENT_GREEN,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_08():
    story = []

    # =========================================================================
    # 25. STEP-BY-STEP OPERATIONAL GUIDE (WINDOWS)
    # =========================================================================
    story.append(Paragraph("25. STEP-BY-STEP RUN & DEPLOYMENT GUIDE (WINDOWS)", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "This section provides an exact, step-by-step setup procedure for running the entire "
        "Cyber Threat Forecasting System locally on Microsoft Windows:",
        BodyStyle
    ))

    setup_steps = [
        ("Step 1: Environmental Prerequisites", 
         "Ensure the following runtimes are installed on Windows:<br/>"
         "• <b>Python 3.11.x:</b> Verify with <code>python --version</code><br/>"
         "• <b>Node.js 18.x or 20.x:</b> Verify with <code>node -v</code> and <code>npm -v</code><br/>"
         "• <b>MongoDB Community Server 7.0:</b> Ensure MongoDB Windows Service is running on <code>localhost:27017</code>"),
        
        ("Step 2: Backend Virtual Environment Setup",
         "Open PowerShell in the workspace root directory and execute:<br/>"
         "<code>cd backend</code><br/>"
         "<code>python -m venv venv</code><br/>"
         "<code>.\\venv\\Scripts\\Activate.ps1</code><br/>"
         "<code>pip install --upgrade pip</code><br/>"
         "<code>pip install -r requirements.txt</code>"),
        
        ("Step 3: Environment Configuration",
         "Create the environment file in the backend root directory:<br/>"
         "<code>copy .env.example .env</code><br/>"
         "Review settings: confirm <code>MONGODB_URI=mongodb://localhost:27017</code> and <code>DATABASE_NAME=cyber_threat_forecast</code>."),
        
        ("Step 4: Synthetic Data Generation & Database Seeding",
         "Execute the automated seeding script to generate the 17,678-record dataset and seed MongoDB collections:<br/>"
         "<code>python scripts\\generate_demo_data.py</code><br/>"
         "Then seed authorized demo analyst and administrator credentials:<br/>"
         "<code>python scripts\\seed_users.py</code>"),
        
        ("Step 5: Machine Learning Model Training (Phase 2)",
         "Train and persist the 8 specialized LSTM models and scalers:<br/>"
         "<code>python scripts\\train_lstm_models.py</code><br/>"
         "This script verifies that all 8 <code>.keras</code> models and <code>.joblib</code> scalers are serialized to <code>backend\\models\\lstm\\</code>."),
        
        ("Step 6: Launch FastAPI Backend Server",
         "From the workspace root or backend directory, start Uvicorn:<br/>"
         "<code>python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000</code><br/>"
         "Verify health: navigate to <code>http://127.0.0.1:8000/api/health</code> or view interactive documentation at <code>http://127.0.0.1:8000/api/docs</code>."),
        
        ("Step 7: Frontend Dependencies & Dev Server",
         "Open a second PowerShell terminal in the workspace root:<br/>"
         "<code>cd frontend</code><br/>"
         "<code>npm install</code><br/>"
         "<code>npm run dev</code><br/>"
         "Vite will launch the SOC Analyst terminal at <code>http://localhost:5173</code> with hot module replacement.")
    ]

    for s_num, s_content in setup_steps:
        story.append(Paragraph(f"<b>{s_num}</b>", Heading3Style))
        story.append(Paragraph(s_content, BodyStyle))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 26. ENVIRONMENT VARIABLES SPECIFICATION
    # =========================================================================
    story.append(Paragraph("26. ENVIRONMENT VARIABLES SPECIFICATION", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Below is the complete inventory of runtime environment variables managed by `backend/app/config.py`. "
        "Sensitive production keys are shown with secure placeholder notation:",
        BodyStyle
    ))

    env_table = [
        ["Variable Name", "Default / Development Value", "Production Recommended Placeholder", "Purpose & Architectural Role"],
        ["PROJECT_NAME", "Cyber Threat Forecasting System", "Cyber Threat Forecasting System", "Application title exposed in OpenAPI docs and headers."],
        ["VERSION", "1.0.0", "1.0.0", "Semantic versioning identifier."],
        ["MONGODB_URI", "mongodb://localhost:27017", "mongodb+srv://<USER>:<PASS>@cluster.mongodb.net", "Connection URI for MongoDB community or Atlas cluster."],
        ["DATABASE_NAME", "cyber_threat_forecast", "cyber_threat_forecast_prod", "Logical target database name in MongoDB instance."],
        ["JWT_SECRET", "cyber_forecast_super_secret_jwt_key_academic_fyp_2026", "YOUR_CRYPTOGRAPHIC_JWT_SECRET_HERE", "256-bit secret used to sign and verify HMAC-SHA256 JWT tokens."],
        ["JWT_ALGORITHM", "HS256", "HS256", "Cryptographic signature algorithm for access tokens."],
        ["ACCESS_TOKEN_EXPIRE_MINUTES", "1440 (24 hours)", "1440", "Lifespan of issued Bearer JWT access tokens before expiration."],
        ["CORS_ORIGINS", "['http://localhost:5173', 'http://localhost:3000']", "['https://soc.enterprise.domain']", "Whitelisted frontend client origins allowed to access API resources."]
    ]
    story.append(create_table(
        env_table[0],
        env_table[1:],
        col_widths=[130, 115, 135, 156],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 27. ERROR HANDLING & SYSTEM RESILIENCE
    # =========================================================================
    story.append(Paragraph("27. ERROR HANDLING & FAULT TOLERANCE", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The application implements proactive defensive programming across all tiers to maintain uptime during anomalies:",
        BodyStyle
    ))

    error_patterns = [
        ("Input Validation Errors (HTTP 400 Bad Request):", 
         "Handled via `backend/app/utils/validation.py`. Inbound requests with unsupported threat vectors, invalid dates, "
         "or out-of-bounds forecast horizons (> 90 days) trigger immediate HTTP 400 responses with descriptive error details "
         "before consuming neural inference resources."),
        
        ("Missing Model Artifacts (HTTP 503 Service Unavailable):",
         "If a requested model or scaler file is deleted from disk, `backend/app/api/forecast.py` intercepts `FileNotFoundError` "
         "and returns HTTP 503: `'Model artifacts not found for [threat]. Please run training pipeline first.'`"),
        
        ("Database Disconnection Graceful Degradation:",
         "In `backend/app/main.py:health_check()`, if MongoDB goes offline, the health check does not crash; it reports "
         "`{'database': 'disconnected'}`. Similarly, in `analytics.py`, if the forecast service is unreachable, risk indicators "
         "fall back to safe baseline estimates (`Medium`, 50.0 risk score) so the SOC dashboard remains renderable."),
        
        ("Dataset Upload Schema Rejection:",
         "When an invalid CSV is uploaded via `/api/datasets/upload`, `validate_csv_dataset()` checks for missing headers, "
         "corrupt date strings, and negative incident counts, returning a structured validation error report without corrupting MongoDB.")
    ]
    for e_name, e_desc in error_patterns:
        story.append(Paragraph(f"• <b>{e_name}</b> {e_desc}", BulletStyle))
        story.append(Spacer(1, 1.5))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 28. LIMITATIONS & ARCHITECTURAL WEAKNESSES
    # =========================================================================
    story.append(Paragraph("28. HONEST ASSESSMENT: SYSTEM LIMITATIONS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Academic and engineering credibility requires an honest examination of project constraints. "
        "The following genuine architectural limitations exist in the current implementation:",
        BodyStyle
    ))

    limitations = [
        ("1. Synthetic Historical Telemetry", 
         "The platform is trained on synthetic data generated via mathematical sine/trend formulas. While it faithfully models "
         "cyclical seasonality and burst states, it lacks the chaotic sensor dropouts, truncated payloads, and misclassified vendor tags "
         "characteristic of live enterprise SIEM streaming data."),
        
        ("2. Univariate Sequential Modeling",
         "The deployed LSTM takes only a 30×1 count tensor. It does not ingest exogenous contextual variables such as zero-day CVE vulnerability "
         "disclosures, Dark Web chatter volume, or enterprise software patching cycles, which strongly influence real-world attack spikes."),
        
        ("3. Error Compounding in Recursive Forecasting",
         "Autoregressive multi-step rollout uses predicted values as inputs for subsequent days. While highly effective for 7-day tactical forecasts, "
         "prediction error compounds exponentially toward day 30, tending to regress toward a smoothed conditional mean."),
        
        ("4. High Outlier Burst Sensitivity (Phishing Negative R²)",
         "The negative R² (-0.031) observed in the Phishing model proves that univariate LSTMs struggle with extreme, highly erratic quarterly "
         "burst blitzes. A hybrid model combining Extreme Value Theory (EVT) or Transformer attention is necessary to capture sudden spikes."),
        
        ("5. Approximate Gaussian Uncertainty Cones",
         "The confidence intervals assume a normal distribution of residuals `(z = 1.96)`. Cyber attack frequencies often exhibit "
         "heavy-tailed (Pareto) distributions, meaning extreme 4x black swan attack bursts may breach the 95% upper bound.")
    ]
    for l_title, l_desc in limitations:
        story.append(Paragraph(f"<b>{l_title}:</b> {l_desc}", BulletStyle))
        story.append(Spacer(1, 1.5))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 29. FUTURE ENHANCEMENTS & ROADMAP
    # =========================================================================
    story.append(Paragraph("29. FUTURE ENHANCEMENTS & RESEARCH ROADMAP", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "To transition this academic platform into a Tier-1 enterprise SOC intelligence solution, "
        "the following engineering roadmap is recommended:",
        BodyStyle
    ))

    roadmap_items = [
        ("Multivariate Temporal Fusion Transformers (TFT):", "Upgrade the neural backbone from univariate LSTM to Temporal Fusion Transformers, incorporating the 14 engineered features alongside external threat intelligence feeds (AlienVault OTX, MITRE ATT&CK)."),
        ("Live SIEM Streaming Connectors:", "Build native real-time ingestion adapters for Splunk HTTP Event Collector (HEC), Elastic Logstash, and Microsoft Sentinel via an Apache Kafka distributed message bus."),
        ("Automated Model Retraining & Concept Drift Detection:", "Deploy an automated MLOps pipeline using Evidently AI to monitor feature drift and trigger weekly retraining when Kolmogorov-Smirnov distribution shifts occur."),
        ("Automated Incident Response & SOAR Integration:", "Connect high-risk forecast escalations directly to Security Orchestration, Automation, and Response (SOAR) playbooks to automatically update perimeter firewall ACLs when risk scores exceed 75."),
        ("Multi-Modal Threat Context:", "Integrate natural language threat intelligence reports using LLM embeddings to modulate LSTM forecasts when geopolitical tensions elevate regional attack probabilities.")
    ]
    for r_name, r_desc in roadmap_items:
        story.append(Paragraph(f"• <b>{r_name}</b> {r_desc}", BulletStyle))
        story.append(Spacer(1, 1.5))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 30. DATA FLOW DIAGRAM (DFD LEVEL 1)
    # =========================================================================
    story.append(Paragraph("30. DATA FLOW DIAGRAM (DFD LEVEL 1)", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The following diagram illustrates the formal Level 1 Data Flow Diagram (DFD), displaying external entities, "
        "processes P1 through P4, and data stores D1 through D4:",
        BodyStyle
    ))

    story.append(create_diagram(
        "data_flow_diagram.png",
        "Level 1 Data Flow Diagram (DFD) showing Process Interactions and MongoDB Data Stores",
        width=520,
        height=280
    ))

    story.append(PageBreak())
    return story
