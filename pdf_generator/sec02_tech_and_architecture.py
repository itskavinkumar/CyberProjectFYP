from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_diagram, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_GREEN,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_02():
    story = []

    # =========================================================================
    # 5. COMPLETE TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("5. COMPLETE TECHNOLOGY STACK", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Every library, framework, runtime environment, and data store utilized across the frontend, "
        "backend, machine learning pipeline, and database was extracted from `backend/requirements.txt` "
        "and `frontend/package.json`. No external dependencies or hypothetical frameworks are listed.",
        BodyStyle
    ))

    tech_table_data = [
        ["Layer / Tier", "Technology", "Version / Spec", "Operational Purpose", "Engineering Rationale for Selection"],
        # Frontend
        ["Frontend UI", "React", "^19.2.8", "Component-driven Single Page Application (SPA)", "Declarative DOM rendering, state encapsulation, fast reconciler."],
        ["Frontend Build", "Vite", "^8.3.0", "Next-gen frontend dev server & bundler", "Instant Hot Module Replacement (HMR), native ESM, optimized rollup build."],
        ["Visualization", "Chart.js", "^4.5.1", "HTML5 canvas charting engine", "High-performance rendering of 90+ point continuous dual-axis timelines."],
        ["Chart Wrapper", "react-chartjs-2", "^5.3.1", "React lifecycle bindings for Chart.js", "Seamless reactive state-to-chart re-rendering during user interactions."],
        ["UI Icons", "Lucide React", "^1.49.0", "Modern vector cybersecurity iconography", "Lightweight, tree-shakeable SVG icon collection matching SOC aesthetics."],
        ["Styling", "Vanilla CSS3", "Modern CSS Tokens", "Theme variables, glassmorphism, responsive grids", "Zero runtime overhead, full layout control without Tailwind bloat."],
        
        # Backend
        ["Backend Web", "FastAPI", ">=0.109.0", "High-performance asynchronous REST API framework", "Native Python type hints, automatic Swagger UI, sub-millisecond routing."],
        ["ASGI Server", "Uvicorn", ">=0.27.0", "Asynchronous Server Gateway Interface web server", "High-concurrency asyncio event loop handling simultaneous SOC requests."],
        ["Data Validation", "Pydantic v2", ">=2.6.0", "Strict request/response schema parsing & validation", "Rust-backed CPython validation, type enforcement, automatic serialization."],
        ["Config Engine", "pydantic-settings", ">=2.1.0", "Environment variable loader (.env)", "Type-safe runtime settings management with fallback default parameters."],
        ["Web Internals", "Starlette", "FastAPI Core", "Underlying lightweight ASGI toolkit", "Provides CORS middleware, request timing middleware, exception handling."],
        
        # Machine Learning
        ["Deep Learning", "TensorFlow / Keras 3", ">=2.15.0", "Recurrent neural network training & inference", "Production-tested stacked LSTM layers, GPU/CPU tensor acceleration."],
        ["Data Manipulation", "Pandas", ">=2.1.4", "DataFrame time-series manipulation & aggregation", "High-speed chronological grouping, date indexing, rolling stats, shift ops."],
        ["Numerical Core", "NumPy", ">=1.26.0,<2.0", "Multi-dimensional array mathematics & matrices", "Sliding window sequence tensor reshaping, clipping, z-score math."],
        ["Preprocessing", "scikit-learn", ">=1.3.2", "MinMaxScaler normalization & error metrics", "Bounds data strictly into [0, 1] range; computes MAE, RMSE, and R2."],
        ["Model I/O", "Joblib", ">=1.3.2", "High-efficiency disk serialization of scikit scalers", "Fast persistence and retrieval of fitted MinMaxScaler state files."],
        
        # Database & Security
        ["NoSQL Database", "MongoDB", "v7.0 Community", "Scalable document-oriented database", "Flexible BSON schema for unstructured incident logs, high write throughput."],
        ["Async DB Driver", "Motor", ">=3.3.2", "Non-blocking async Python driver for MongoDB", "Native asyncio event loop integration preventing API thread blocking."],
        ["Sync DB Driver", "PyMongo", ">=4.6.1", "Underlying MongoDB client library for Motor", "Standard database connection pooling, BSON parsing, index management."],
        ["Password Security", "bcrypt", ">=4.0.1", "Cryptographic adaptive password hashing", "Direct C implementation of blowfish cipher with 12 salt rounds."],
        ["Password Utils", "passlib", ">=1.7.4", "Password hashing security context wrapper", "Modular fallback and verification hashing routines."],
        ["Token Auth", "python-jose", ">=3.3.0", "JSON Web Token (JWT) encoding & signature check", "RFC 7519 HMAC-SHA256 (HS256) signed token creation & verification."],
        ["Testing & HTTP", "HTTPX & Pytest", ">=0.26 / >=8.0", "Asynchronous HTTP client & test runner", "Full test client simulation of API endpoints and UI integration tests."]
    ]
    
    story.append(create_table(
        tech_table_data[0],
        tech_table_data[1:],
        col_widths=[75, 95, 65, 140, 160],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # 6. COMPLETE SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("6. COMPLETE SYSTEM ARCHITECTURE", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The system is organized around a decoupled, 5-tier distributed architecture engineered for high availability, "
        "sub-second inference speed, and horizontal scalability:",
        BodyStyle
    ))

    # Embed Architecture Diagram
    story.append(create_diagram(
        "architecture_diagram.png",
        "Multi-Tier Distributed System Architecture showing Presentation, API, Service, ML, and Data Tiers",
        width=520,
        height=320
    ))

    arch_tiers = [
        ("Tier 1: Presentation Tier (Client)", 
         "Built with React 19 and bundled via Vite, the presentation layer executes entirely within the SOC analyst's browser. "
         "It communicates with the backend exclusively via asynchronous HTTP/REST calls. All telemetry and forecast charts are rendered "
         "using Chart.js onto HTML5 canvas elements. Security tokens (JWT) and authenticated user state are cached in client `localStorage`."),
        
        ("Tier 2: API Gateway & Middleware Tier",
         "Powered by FastAPI and running on Uvicorn ASGI on port 8000 (proxied via Vite on 5173). Intercepts all traffic through "
         "three critical layers: (1) CORS Middleware enforcing origin whitelisting, (2) Request Timing & Logging Middleware logging "
         "request duration and HTTP status codes, and (3) Global Exception Handler returning standardized JSON error envelopes."),
        
        ("Tier 3: Business Service & Validation Tier",
         "Coordinates high-level domain workflows. Includes: (1) `ForecastService` coordinating model loading, feature aggregation, "
         "and status polling, (2) `Security` managing bcrypt password hashing and JWT encoding/decoding, and (3) `Validation` inspecting "
         "incoming telemetry schemas, date formatting, and CSV headers."),
        
        ("Tier 4: Deep Learning Intelligence Tier",
         "Contains the core machine learning inference engine (`ThreatForecaster`). Directly interfaces with pre-trained Keras 3 "
         "models stored on disk (`.keras`) and scikit-learn scalers (`.joblib`). Implements the recursive autoregressive rollout algorithm "
         "and uncertainty cone calculations."),
        
        ("Tier 5: Data Persistence & Serialization Tier",
         "Dual storage architecture: (1) MongoDB document database holding 5 enterprise collections (`threat_events`, `forecasts`, "
         "`datasets`, `models`, `users`) accessed non-blockingly via Motor, and (2) Local filesystem storage for serialized neural weights "
         "and feature-engineered training datasets (`backend/data/processed/`).")
    ]
    for t_name, t_desc in arch_tiers:
        story.append(Paragraph(f"<b>{t_name}:</b> {t_desc}", BulletStyle))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 7. COMPLETE PROJECT FOLDER STRUCTURE
    # =========================================================================
    story.append(Paragraph("7. COMPLETE PROJECT FOLDER STRUCTURE & FILE AUDIT", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Below is the comprehensive repository folder hierarchy verified directly from the project directory. "
        "Every single file was located, verified, and mapped to its runtime role:",
        BodyStyle
    ))

    tree_text = (
        "CyberProjectFYP/\n"
        "├── .env                             # Environment configuration (DB URI, JWT secret, CORS)\n"
        "├── .env.example                     # Reference template for environment variables\n"
        "├── requirements.txt                 # Backend Python package manifest\n"
        "├── sample_threat_events_1000.csv    # Sample 1,000-record dataset for manual testing\n"
        "├── backend/\n"
        "│   ├── app/\n"
        "│   │   ├── main.py                  # FastAPI application entry point, lifespan, middleware\n"
        "│   │   ├── config.py                # Pydantic BaseSettings class & global configuration\n"
        "│   │   ├── database.py              # Motor client connection manager & compound indexer\n"
        "│   │   ├── api/\n"
        "│   │   │   ├── __init__.py          # Router package exporter\n"
        "│   │   │   ├── auth.py              # User registration, login, JWT token endpoints\n"
        "│   │   │   ├── threats.py           # Threat incident querying, filtering, manual logging\n"
        "│   │   │   ├── forecast.py          # LSTM forecast execution & model status endpoints\n"
        "│   │   │   ├── datasets.py          # CSV dataset upload, schema validation, ingestion\n"
        "│   │   │   └── analytics.py         # SOC overview metrics, risk matrix, 300s cache\n"
        "│   │   ├── ml/\n"
        "│   │   │   ├── __init__.py          # ML module package exporter\n"
        "│   │   │   ├── preprocessor.py      # Daily aggregation, 14 engineered features, sequences\n"
        "│   │   │   ├── model.py             # Stacked LSTM architecture definition (Keras 3)\n"
        "│   │   │   ├── trainer.py           # End-to-end training pipeline, EarlyStopping, split\n"
        "│   │   │   ├── evaluator.py         # MAE, RMSE, MAPE, R2, confidence cone calculations\n"
        "│   │   │   └── forecast.py          # Autoregressive multi-step forecaster, risk scoring\n"
        "│   │   ├── models/\n"
        "│   │   │   ├── database_models.py   # Pydantic BSON document representation schemas\n"
        "│   │   │   └── schemas.py           # API request and response validation models\n"
        "│   │   ├── services/\n"
        "│   │   │   └── forecast_service.py  # Service coordinator linking API router with ML engine\n"
        "│   │   └── utils/\n"
        "│   │       ├── logging.py           # Standardized stream logger configuration\n"
        "│   │       ├── security.py          # Bcrypt hashing, JWT generation, get_current_user\n"
        "│   │       └── validation.py        # Threat category, forecast horizon, CSV schema checks\n"
        "│   ├── data/\n"
        "│   │   ├── raw/\n"
        "│   │   │   └── synthetic_threat_events.csv  # Master dataset: 17,678 records across 2 years\n"
        "│   │   └── processed/               # Daily aggregated & 14-feature CSVs (botnet, ddos, etc.)\n"
        "│   ├── models/lstm/                 # 8 Keras models (.keras), scalers (.joblib), metrics (.json)\n"
        "│   ├── scripts/\n"
        "│   │   ├── generate_demo_data.py    # Generates 17,678 synthetic records and seeds MongoDB\n"
        "│   │   ├── seed_users.py            # Seeds demo analyst and admin credentials\n"
        "│   │   └── train_lstm_models.py     # Standalone CLI training script for all 8 categories\n"
        "│   └── tests/                       # Complete pytest suite (phase1, phase2, phase3)\n"
        "└── frontend/\n"
        "    ├── index.html                   # HTML5 template mount point\n"
        "    ├── vite.config.js               # Vite config with /api reverse proxy to localhost:8000\n"
        "    ├── package.json                 # Frontend dependencies (React 19, Chart.js, Lucide)\n"
        "    └── src/\n"
        "        ├── main.jsx                 # React root renderer\n"
        "        ├── App.jsx                  # Root state coordinator, tab switcher, health poller\n"
        "        ├── index.css                # Global SOC design system & CSS variables\n"
        "        ├── api.js                   # Centralized Fetch API client with JWT interception\n"
        "        └── components/\n"
        "            ├── Navbar.jsx           # Top cyber navigation bar with live telemetry pulse\n"
        "            ├── OverviewView.jsx     # SOC executive dashboard, KPI cards, trendline, matrix\n"
        "            ├── ForecastView.jsx     # Main LSTM forecasting workbench & confidence cone\n"
        "            ├── ThreatsView.jsx      # Raw telemetry table, filters, manual ingestion modal\n"
        "            ├── ModelsView.jsx       # Registry of all 8 models displaying test metrics\n"
        "            ├── DatasetsView.jsx     # CSV drag-and-drop ingestion & validation report\n"
        "            └── AuthModal.jsx        # Login & registration modal with quick demo buttons"
    )
    story.append(create_code_block(tree_text, caption="Complete Repository Architecture Directory Hierarchy"))

    story.append(PageBreak())
    return story
