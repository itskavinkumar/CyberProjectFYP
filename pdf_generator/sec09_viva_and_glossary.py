from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_qa,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_AMBER, ACCENT_ROSE,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_09():
    story = []

    # =========================================================================
    # 31. PLAIN-LANGUAGE EXPLANATION FOR BEGINNERS
    # =========================================================================
    story.append(Paragraph("31. PLAIN-LANGUAGE EXPLANATION FOR BEGINNERS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>Explain this project like I am a beginner:</b><br/>"
        "Imagine running an emergency hospital or airport security checkpoint. If you only react when hundreds of people "
        "suddenly arrive at your doors at the same minute, your staff gets overwhelmed, lines back up, and chaos ensues. "
        "That is how most cybersecurity systems work today—they only sound an alarm when an attack is already hitting the server.<br/><br/>"
        "Now imagine you have a smart weather forecasting system for cyber attacks. You give this system two years of past daily records "
        "showing how many attacks happened every day. The computer looks at these records using a special type of artificial intelligence "
        "called an <b>LSTM neural network</b>. The AI learns the hidden patterns—for example, that phishing attacks spike on Tuesday mornings "
        "when people open work emails, or that DDoS bot attacks surge on weekends when gaming and commercial web traffic peaks.<br/><br/>"
        "Once it learns these rhythms, you ask the system: <i>'How many DDoS attacks should we expect over the next 14 days?'</i> "
        "The system looks at the last 30 days and projects day-by-day into the future. It draws a line showing the expected attack count, "
        "shades an uncertainty band (like a hurricane prediction cone), and gives a clear Risk Score from 0 to 100. "
        "This gives security teams days of advance notice to prepare extra staff and tighten firewalls before the storm hits.",
        BodyStyle
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 32. VIVA ELEVATOR PITCHES
    # =========================================================================
    story.append(Paragraph("32. VIVA ELEVATOR PITCHES (30s, 1m, 3m)", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))

    pitches = [
        ("The 30-Second Elevator Pitch", 
         "\"My project is the Cyber Threat Forecasting System, a deep learning platform that transforms cybersecurity from reactive alerting into proactive forecasting. Traditional SIEMs only detect attacks underway. Our system uses stacked LSTM recurrent neural networks trained on historical threat telemetry to predict daily attack counts across 8 distinct threat vectors for 7, 14, and 30-day horizons. It pairs predictions with 95% confidence intervals and composite risk scores to help enterprise SOC teams allocate resources before cyber attacks peak.\""),
        
        ("The 1-Minute Executive Pitch",
         "\"Good morning. In modern cybersecurity, Security Operations Centers face severe alert fatigue and resource mismatch because tools are entirely reactive. To solve this, I developed the Cyber Threat Forecasting System. Our architecture is powered by a FastAPI asynchronous backend, a MongoDB document store, and a React 19 operational dashboard. The intelligence core consists of 8 specialized Keras LSTM neural networks trained with Huber loss to resist burst outliers. The system takes a 30-day sliding window of incident telemetry and performs recursive multi-step forecasting across 8 threat vectors—including DDoS, Ransomware, and Phishing. Along with predicted volumes, it dynamically computes 95% confidence cones and a composite risk score (0 to 100) factoring in volume, velocity, burst spikes, and threat severity weights. This provides SOC directors with actionable foresight for proactive staffing and defense configuration.\""),
        
        ("The 3-Minute Comprehensive Technical Defense Pitch",
         "\"Respected committee members, my final year project is titled the 'Cyber Threat Forecasting System'. Modern enterprises invest millions in reactive detection tools like Firewalls and SIEMs, yet breaches remain widespread because reactive tools give zero forward warning. Our project introduces a predictive cybersecurity operations paradigm.<br/><br/>"
         "The technical implementation spans four interconnected layers: First, our data pipeline in Python and Pandas ingests incident logs, enforces time-series continuity across 730 consecutive days, and engineers 14 time-series features. Second, we deploy 8 dedicated stacked LSTM neural networks built in Keras 3. Each network uses an Input layer of shape (30, 1), an LSTM layer of 64 units with return sequences, 20% dropout, a second LSTM of 32 units, 20% dropout, Dense-16 ReLU, and a linear Dense-1 output. We compile with Adam and Huber loss to handle non-linear attack bursts, using EarlyStopping to restore best weights.<br/><br/>"
         "Third, our forecasting service implements recursive multi-step rollout across 7, 14, and 30-day horizons, deriving expanding 95% confidence intervals based on test residual standard deviation and calculating a multi-factor risk score from 0 to 100. Our test evaluations show strong predictive performance—for example, Malware achieved an MAE of 24.25 and R2 of 0.576, and SQL Injection achieved an MAE of 13.66 and R2 of 0.566. For Phishing, we observed a negative R2 due to extreme quarterly blitz variance, highlighting real-world burst dynamics.<br/><br/>"
         "Finally, our backend is built on FastAPI with Motor and MongoDB, providing compound-indexed queries, JWT authentication, and automated OpenAPI documentation, connected to a responsive React 19 and Chart.js SOC dashboard. In summary, this project delivers an end-to-end, mathematically grounded platform for proactive cybersecurity intelligence.\"")
    ]

    for p_title, p_text in pitches:
        story.append(Paragraph(f"<b>{p_title}</b>", Heading2Style))
        story.append(Paragraph(p_text, BodyStyle))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 33. COMPREHENSIVE VIVA QUESTIONS & MODEL ANSWERS (55+ Q&As)
    # =========================================================================
    story.append(Paragraph("33. COMPREHENSIVE VIVA QUESTIONS & MODEL ANSWERS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Below are 55 rigorous technical questions categorized across all aspects of the project, "
        "complete with precise model answers verified against the repository codebase:",
        BodyStyle
    ))

    qa_list = [
        # Category A: Basic Project (1-5)
        (1, "Basic", "What is the primary objective of this project?",
         "To forecast future daily incident volumes across 8 distinct cyber threat categories over 7, 14, and 30-day horizons using stacked LSTM neural networks, transforming reactive SOC operations into proactive risk management."),
        (2, "Basic", "What are the 8 threat categories supported by the system?",
         "Phishing, Malware, Brute Force, DDoS, Botnet, SQL Injection, Ransomware, and Data Breach, defined in `backend/app/config.py:SUPPORTED_THREAT_TYPES`."),
        (3, "Basic", "What is the difference between reactive and predictive cybersecurity?",
         "Reactive cybersecurity detects attacks after they enter the network or while occurring (t = 0). Predictive cybersecurity uses historical time-series patterns to anticipate volume surges days or weeks in advance (t + k)."),
        (4, "Basic", "Who are the target end-users of this platform?",
         "Tier-1/Tier-2/Tier-3 SOC Analysts, Threat Intelligence Specialists, CISOs, and Network Security Engineers responsible for enterprise security monitoring."),
        (5, "Basic", "Is this system intended to replace existing SIEM/IDS appliances?",
         "No. It complements SIEM/IDS appliances. SIEM tools detect granular packet/log anomalies in real time, while this system provides macro-level capacity planning and proactive threat anticipation."),

        # Category B: Python & Backend (6-10)
        (6, "FastAPI", "Why did you choose FastAPI over Flask or Django?",
         "FastAPI provides native asynchronous ASGI performance via Starlette and Uvicorn, automatic data validation via Pydantic v2, and automatic Swagger/OpenAPI documentation generation at `/api/docs` with zero extra code."),
        (7, "FastAPI", "How is the application lifespan managed in your FastAPI code?",
         "Using `@asynccontextmanager async def lifespan(app: FastAPI)` in `main.py`. It initiates the Motor MongoDB connection pool and verifies compound indexes on startup, cleanly closing all database connections on shutdown."),
        (8, "FastAPI", "How do you handle cross-origin requests between Vite and FastAPI?",
         "Via FastAPI's `CORSMiddleware` in `main.py`, whitelisting `settings.CORS_ORIGINS` (ports 5173 and 3000), while Vite's `vite.config.js` sets up a development reverse proxy forwarding `/api` to port 8000."),
        (9, "Python", "What role does Pydantic play in this architecture?",
         "Pydantic parses, validates, and serializes all API request and response data (defined in `schemas.py`). It enforces strict data types, date formatting, and value bounds (e.g., `forecast_days` between 1 and 90)."),
        (10, "FastAPI", "How does the global exception handler work?",
         "In `main.py`, `@app.exception_handler(Exception)` intercepts unhandled exceptions, logs the full error traceback to console, and returns an HTTP 500 JSON response with a standardized error envelope."),

        # Category C: Database & MongoDB (11-15)
        (11, "MongoDB", "Why did you choose MongoDB instead of a relational database like PostgreSQL?",
         "Cyber incident telemetry is inherently semi-structured and high-volume. MongoDB's document model allows flexible incident schemas with nested metadata, while the Motor async driver integrates natively with FastAPI's event loop."),
        (12, "MongoDB", "What collections are defined in your MongoDB database?",
         "Five collections in database `cyber_threat_forecast`: `threat_events` (raw/ingested logs), `forecasts` (cached inference points), `datasets` (file metadata), `models` (metadata/metrics), and `users` (credentials)."),
        (13, "MongoDB", "What indexes did you create and why are they necessary?",
         "Compound index `(date: 1, threat_type: 1)` on `threat_events` to accelerate daily time-series aggregations, unique index on `email` in `users`, and unique index on `threat_type` in `models`. Without them, group-by queries would trigger slow full-collection scans."),
        (14, "MongoDB", "What driver connects Python to MongoDB asynchronously?",
         "Motor (`motor.motor_asyncio.AsyncIOMotorClient`), which wraps PyMongo to provide non-blocking asynchronous I/O that prevents database queries from freezing the FastAPI worker process."),
        (15, "MongoDB", "How are forecast points persisted in MongoDB?",
         "In `forecast.py`, upon generating predictions, stale records for that threat and horizon are purged, and newly generated points are inserted via `db.forecasts.insert_many()` for historical review and fast caching."),

        # Category D: Authentication & Security (16-20)
        (16, "Security", "How are user passwords secured in your database?",
         "Using direct `bcrypt` password hashing with 12 salt rounds (`bcrypt.gensalt(12)`). Plaintext passwords are truncated to 72 bytes and hashed via `bcrypt.hashpw()`; passwords are never stored in plaintext."),
        (17, "Security", "How does JSON Web Token (JWT) authentication work in your application?",
         "Upon login, `create_access_token()` creates an RFC 7519 signed JWT token using HMAC-SHA256 (`HS256`) containing user email, role, and a 24-hour expiration. The frontend stores it in `localStorage` and transmits it in the `Authorization: Bearer <token>` header."),
        (18, "Security", "How do you protect endpoints from unauthorized access?",
         "Using FastAPI's dependency injection: `get_current_user` decodes and verifies the Bearer JWT. For elevated actions, `require_role(['admin'])` verifies the user's role before allowing execution."),
        (19, "Security", "What roles are implemented in your Role-Based Access Control (RBAC)?",
         "Three roles: `analyst` (standard operational access to forecast and view telemetry), `admin` (elevated privileges to upload datasets and retrain models), and `viewer` (read-only audit access)."),
        (20, "Security", "Where are cryptographic secrets stored?",
         "In environment configuration (`.env`) loaded via `pydantic-settings` in `config.py`. Production secrets must never be committed to source control."),

        # Category E: Machine Learning & LSTM (21-30)
        (21, "ML", "What is an LSTM and how does it differ from a standard RNN?",
         "Long Short-Term Memory is a specialized recurrent neural network architecture designed by Hochreiter and Schmidhuber. It resolves the vanishing gradient problem of standard RNNs using a cell state regulated by three affine gates: Forget, Input, and Output."),
        (22, "ML", "What is the exact layer architecture of your LSTM model?",
         "Input layer `(30, 1)` -> LSTM (64 units, return_sequences=True) -> Dropout (0.20) -> LSTM (32 units, return_sequences=False) -> Dropout (0.20) -> Dense (16 units, ReLU) -> Dense (1 unit, Linear)."),
        (23, "ML", "What is the total number of trainable parameters in your model?",
         "29,857 trainable parameters (~116.6 KB in memory), which prevents memorization of noise while enabling sub-15ms inference latency on CPU."),
        (24, "ML", "Why did you use Huber loss instead of Mean Squared Error (MSE)?",
         "MSE squares errors, leading to explosive gradient updates during extreme cyber attack burst spikes (such as a 4.5x volumetric DDoS flood). Huber loss behaves quadratically for small errors (|e| <= 1.0) and linearly for large errors, providing robustness against burst outliers."),
        (25, "ML", "What is the sequence length (lookback window) and why was 30 chosen?",
         "30 days (`DEFAULT_SEQUENCE_LENGTH = 30`). This provides exactly one full calendar month of historical context, capturing four full weekly cycles and monthly business rhythms needed to prime the recurrent state."),
        (26, "ML", "How did you prevent overfitting during training?",
         "Through two mechanisms: (1) Dropout layers with rate 0.20 after each LSTM layer to prevent co-adaptation of recurrent units, and (2) Keras `EarlyStopping` monitoring validation loss with a patience of 7 epochs to restore the best weights."),
        (27, "ML", "Why did you normalize the data using MinMaxScaler?",
         "LSTM internal cell states use `tanh` (range -1 to 1) and `sigmoid` (range 0 to 1) activation functions. Unnormalized counts (e.g., 450 incidents) would saturate the activations, causing vanishing gradients. MinMaxScaler scales all inputs to `[0, 1]`."),
        (28, "ML", "How is the data split between training and testing?",
         "Chronologically: the first 80% (560 days) is used for training, and the final 20% (140 days) is held out for testing. Random shuffling is strictly prohibited to avoid lookahead data leakage."),
        (29, "ML", "What optimizer and learning rate did you select?",
         "Adam (Adaptive Moment Estimation) optimizer with a learning rate of 0.003, providing fast convergence and adaptive per-parameter learning rate adjustments."),
        (30, "ML", "What is the batch size and upper epoch limit?",
         "Batch size is 16 samples; upper epoch limit is 30 epochs, though EarlyStopping typically restores optimal weights between epochs 18 and 26."),

        # Category F: Forecasting & Uncertainty (31-35)
        (31, "Forecasting", "How does the recursive multi-step forecasting algorithm work?",
         "To forecast h days ahead, the model takes the initial 30-day window, predicts day t+1, shifts the window forward by dropping day t-29 and appending day t+1, and repeats this process h times. The predictions are then inverse-scaled back to raw incident counts."),
        (32, "Forecasting", "What are the supported forecast horizons?",
         "7 days (tactical sprint), 14 days (operational window), and 30 days (strategic horizon), verified in `backend/app/config.py:DEFAULT_FORECAST_HORIZONS`."),
        (33, "Forecasting", "How do you calculate the 95% confidence interval?",
         "Using `Margin = 1.96 * residual_std * sqrt(1 + t/30)`. The `sqrt(1 + t/30)` term causes the uncertainty cone to expand as the horizon deepens, reflecting accumulated autoregressive error. Lower bounds are clamped at 0.0."),
        (34, "Forecasting", "What is `residual_std` and where does it come from?",
         "It is the standard deviation of prediction residuals `(y_true - y_pred)` measured on the 140-day test set during model evaluation, stored in `backend/models/lstm/*_metrics.json`."),
        (35, "Forecasting", "Can predicted incident counts ever be negative?",
         "No. In `forecast.py`, `pred_counts = np.clip(np.round(pred_counts, 2), 0.0, None)` and `lower_bound = max(0.0, pred - margin)` strictly prevent negative values."),

        # Category G: Risk Scoring (36-40)
        (36, "Risk", "How does the Composite Risk Score convert predictions into a 0–100 score?",
         "By combining three operational factors: Volume Score (up to 50 pts), Trend Velocity Score (-15 to +25 pts), and Burst Spike Score (up to 25 pts), multiplied by the category severity weight and clipped between 5.0 and 98.0."),
        (37, "Risk", "What are the category severity weights and why are they unequal?",
         "Ransomware (1.40), Data Breach (1.35), DDoS (1.25), Malware (1.15), Botnet (1.05), SQL Injection (1.00), Phishing (0.95), and Brute Force (0.85). They reflect organizational impact: a ransomware outbreak is far more destructive than credential scanning."),
        (38, "Risk", "What are the four risk categories and their threshold boundaries?",
         "Critical (>= 75.0), High (50.0 to 74.9), Medium (25.0 to 49.9), and Low (< 25.0), verified in `backend/app/ml/forecast.py:calculate_risk_profile()`."),
        (39, "Risk", "What constitutes an 'Increasing' trend direction?",
         "A predicted percentage change of +4.0% or greater relative to the 60-day historical baseline. Changes <= -4.0% are 'Decreasing'; otherwise 'Stable'."),
        (40, "Risk", "How does the `/api/analytics/overview` endpoint optimize risk score delivery?",
         "It uses an in-memory dictionary cache with a 300-second (5-minute) TTL (`_risk_cache`), preventing expensive redundant neural inference on every dashboard refresh."),

        # Category H: Dataset & Preprocessing (41-45)
        (41, "Dataset", "Is your historical dataset real or synthetic?",
         "Synthetic. It was generated via `backend/scripts/generate_demo_data.py` to simulate realistic cyber attack dynamics (trends, weekly cycles, quarterly blitzes, multi-day bursts, and noise) across 730 continuous days (17,678 records)."),
        (42, "Dataset", "What happens if there are missing dates in the raw logs?",
         "The preprocessor executes `grouped.reindex(continuous_idx, fill_value=0)`, creating a continuous daily date index and filling missing dates with zero counts so the LSTM sequence integrity is never broken."),
        (43, "Dataset", "What are the 14 engineered features in the preprocessor?",
         "Count, day_of_week, day_of_month, month, is_weekend, rolling_mean_7, rolling_std_7, rolling_mean_14, rolling_mean_30, lag_1, lag_7, lag_14, ema_7, and daily_change."),
        (44, "Dataset", "Does the deployed LSTM model use all 14 engineered features?",
         "No. The deployed model is strictly a **univariate** model taking an input shape of `(Batch, 30, 1)` (incident count). The 14 features were created for exploratory data analysis and future multivariate extensions."),
        (45, "Dataset", "How does the system handle CSV dataset uploads via the web UI?",
         "The file is sent as multipart FormData to `/api/datasets/upload`. `validate_csv_dataset()` checks for required headers (Date, Threat_Type, Severity, Count), validates date formats, ensures non-negative counts, and batch-inserts records into MongoDB."),

        # Category I: Frontend & Visualization (46-50)
        (46, "Frontend", "What library is used for charting and why?",
         "Chart.js (via `react-chartjs-2`), utilizing HTML5 canvas rendering for smooth rendering of 90+ point continuous dual-axis lines, filled confidence cones, and responsive tooltips."),
        (47, "Frontend", "How does the frontend bridge historical and forecast data on the chart?",
         "In `ForecastView.jsx`, the historical array is rendered with a solid cyan line, and the forecast array is rendered with a dashed purple line. A shared bridge point connects them seamlessly without visual gaps."),
        (48, "Frontend", "How does the frontend communicate with the backend?",
         "Through `frontend/src/api.js` using native `fetch()`. It proxies requests to `http://127.0.0.1:8000` via Vite, automatically attaching JWT Bearer tokens from `localStorage`."),
        (49, "Frontend", "What state management is used in the React application?",
         "Clean React component state hooks (`useState`, `useEffect`) managed at the `App.jsx` root level, lifting state where needed without the boilerplate of Redux."),
        (50, "Frontend", "How does the live heartbeat telemetry dot work?",
         "`App.jsx` runs an automated `setInterval` hook every 30 seconds querying `/api/health`. If the database is connected, the pulse dot turns glowing green (`LIVE TELEMETRY`); otherwise orange (`CONNECTING`)."),

        # Category J: Testing & Difficult Viva (51-55)
        (51, "Testing", "What automated tests exist in the project?",
         "A Pytest suite across three phases: `test_phase1.py` (configuration, dataset, MongoDB connection), `test_phase2.py` (preprocessing, sequence shape, LSTM architecture, 8 models existence), and `test_phase3.py` (API endpoints, auth, upload validation)."),
        (52, "Testing", "How do you verify frontend-backend integration?",
         "Via `backend/tests/verify_frontend_integration.py`, which uses HTTPX to execute automated end-to-end calls through the Vite proxy (port 5173) to FastAPI (port 8000)."),
        (53, "Difficult", "Why does the Phishing model have a negative R² (-0.0312)?",
         "Because the test split coincided with severe, erratic quarterly blitz bursts (reaching 342 attacks/day). The squared residual errors of the smooth LSTM predictions exceeded the total baseline variance, resulting in a negative R². It demonstrates that Phishing requires exogenous spam-volume features."),
        (54, "Difficult", "Can this system detect zero-day attacks?",
         "No. This system is a macro-level time-series volume forecaster, not an intrusion detection payload inspector. It forecasts expected incident numbers, not individual packet exploit signatures."),
        (55, "Difficult", "What is the biggest limitation of this project and how would you fix it?",
         "The univariate nature of the model and recursive error accumulation over 30 days. To fix it, I would transition to a Temporal Fusion Transformer (TFT) that ingests the 14 engineered features alongside live SIEM streaming data via Apache Kafka.")
    ]

    for q_num, q_cat, q_txt, q_ans in qa_list:
        story.append(create_qa(q_num, q_cat, q_txt, q_ans))

    story.append(PageBreak())

    # =========================================================================
    # 34. TECHNICAL GLOSSARY (30+ TERMS)
    # =========================================================================
    story.append(Paragraph("34. COMPREHENSIVE TECHNICAL GLOSSARY", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    glossary_terms = [
        ["Term / Acronym", "Technical Definition & Context in CyberGuard AI"],
        ["Autoregressive Model", "A statistical or neural model that predicts future values based on past values of the same variable via a recursive sliding window."],
        ["bcrypt", "An adaptive cryptographic password-hashing function based on the Blowfish cipher with configurable work factor (12 salt rounds in this project)."],
        ["Confidence Interval", "A statistical range around a forecast within which the true value is expected to fall with a specified probability (95% in this system)."],
        ["CORS", "Cross-Origin Resource Sharing; security mechanism allowing the React frontend (port 5173) to access the FastAPI backend (port 8000)."],
        ["Cosine / Sine Seasonality", "Mathematical harmonics used in `generate_demo_data.py` to model cyclical patterns like quarterly campaigns."],
        ["Data Leakage", "Accidentally sharing information between training and test sets. Prevented here by strict chronological 80/20 train/test splitting."],
        ["DDoS", "Distributed Denial of Service; volumetric cyber attack attempting to overwhelm network capacity, modeled here with 1.25x severity weight."],
        ["Dropout", "Regularization technique deactivating random neurons (20% in this system) during training passes to prevent overfitting."],
        ["EarlyStopping", "Callback terminating training when validation loss stops improving for a specified patience (7 epochs), restoring optimal weights."],
        ["EMA", "Exponential Moving Average; a moving average giving exponential weight to recent daily observations to track short-term spikes."],
        ["FastAPI", "High-performance asynchronous Python web framework built on Starlette and Pydantic, providing automatic Swagger OpenAPI documentation."],
        ["Huber Loss", "Loss function combining the quadratic advantages of MSE for small errors with the robust linear penalty of MAE for burst outliers."],
        ["JSON Web Token (JWT)", "An open RFC 7519 standard defining a compact, self-contained method for securely transmitting claims between parties as a signed JSON object."],
        ["Keras 3", "High-level deep learning API running on top of TensorFlow, used here to build, compile, train, and serialize stacked LSTM networks."],
        ["Lag Feature", "A historical value from a fixed prior time step (e.g., lag_1 = yesterday, lag_7 = same day last week) used in autoregression."],
        ["Lifespan Context", "FastAPI's modern async context manager managing resource startup (MongoDB connection pool) and shutdown cleanup."],
        ["LSTM", "Long Short-Term Memory; a specialized recurrent neural network capable of learning long-term sequential dependencies via gating mechanisms."],
        ["MAE", "Mean Absolute Error; average magnitude of forecast errors in incident count units without penalizing outliers quadratically."],
        ["MAPE", "Mean Absolute Percentage Error; average percentage discrepancy between predicted and actual attack counts."],
        ["MinMaxScaler", "Feature scaling algorithm transforming raw counts into the range [0, 1] to prevent recurrent neuron saturation."],
        ["MongoDB", "NoSQL document database storing unstructured threat logs, cached forecasts, model registry documents, and user accounts."],
        ["Motor", "Official asynchronous, non-blocking Python driver for MongoDB integrating directly into FastAPI's asyncio event loop."],
        ["OAuth2 Bearer Token", "Authentication standard where the client proves authorization by providing an issued JWT in the HTTP Authorization header."],
        ["Pydantic v2", "Data validation and settings library using Python type hints, rewritten in Rust for high-speed serialization and parsing."],
        ["R² Score", "Coefficient of determination; measures the proportion of variance in target attack volume explained by the LSTM model."],
        ["RBAC", "Role-Based Access Control; authorizing permissions based on assigned user roles (analyst, admin, viewer)."],
        ["Residual Standard Deviation", "Standard deviation of prediction errors on the test set, used as the baseline multiplier for dynamic confidence intervals."],
        ["RMSE", "Root Mean Squared Error; square root of average squared errors, heavily penalizing large attack surge prediction misses."],
        ["SIEM", "Security Information and Event Management; enterprise software aggregating logs from firewalls, servers, and network devices."],
        ["SOC", "Security Operations Center; centralized facility where cybersecurity staff monitor, detect, analyze, and investigate security incidents."],
        ["Time-Series Continuity", "Ensuring no missing dates exist in the timeline; enforced via `grouped.reindex()` filling missing days with zero counts."],
        ["Uvicorn", "Lightning-fast ASGI web server implementation for Python, powering the concurrent execution of the FastAPI application."],
        ["Vite", "Modern frontend build tool offering instant development server start, rapid Hot Module Replacement, and optimized Rollup bundling."]
    ]
    story.append(create_table(
        glossary_terms[0],
        glossary_terms[1:],
        col_widths=[140, 396],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 35. FINAL PROJECT SUMMARY & CONCLUSIONS
    # =========================================================================
    story.append(Paragraph("35. FINAL PROJECT SUMMARY & CONCLUSIONS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>What This Project Actually Accomplishes:</b><br/>"
        "The Cyber Threat Forecasting System represents an operational, fully audited academic final year project. "
        "It successfully proves that recurrent neural architectures (specifically 2-layer stacked LSTMs trained with Huber loss) "
        "can capture complex non-linear patterns within cyber attack telemetry. By deploying 8 dedicated models across 8 distinct "
        "threat vectors, the platform respects the distinct behavioral characteristics of diverse cyber attacks—from work-hour "
        "phishing blitzes to weekend volumetric DDoS floods.<br/><br/>"
        "<b>Architectural Takeaways:</b><br/>"
        "• <b>Backend:</b> FastAPI and Motor provide high-concurrency, asynchronous non-blocking performance with automated Swagger self-documentation.<br/>"
        "• <b>Database:</b> MongoDB maintains 5 compound-indexed collections for high-speed time-series filtering and instant forecast caching.<br/>"
        "• <b>Security:</b> Cryptographically sound bcrypt (12 rounds) password storage and signed HS256 JWT tokens enforce role-based access.<br/>"
        "• <b>Frontend:</b> React 19 and Chart.js deliver an intuitive, glassmorphism-styled SOC workstation with interactive dual-axis charts and risk meters.<br/>"
        "• <b>Machine Learning:</b> Compact 29,857-parameter LSTM networks deliver sub-15ms predictions, 95% expanding confidence cones, and a 0–100 composite risk matrix.<br/><br/>"
        "Armed with this complete technical documentation, the project candidate possesses the verified facts, architectural diagrams, "
        "exact metrics, and critical code explanations needed to defend this project confidently before university evaluators, "
        "external examiners, and enterprise technical interviewers.",
        BodyStyle
    ))

    return story
