from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_diagram, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_AMBER,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_03():
    story = []

    # =========================================================================
    # 8. PROGRAM-BY-PROGRAM EXPLANATION
    # =========================================================================
    story.append(Paragraph("8. PROGRAM-BY-PROGRAM ARCHITECTURAL AUDIT", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "This section details every core Python and JavaScript file across the repository. "
        "For each module, the underlying architectural purpose, exposed classes/functions, input signatures, "
        "output return types, and interaction paths are documented exactly as implemented.",
        BodyStyle
    ))

    modules = [
        ("backend/app/main.py", "FastAPI Core Application & Lifecycle Engine",
         "The central entry point of the backend. Initializes the FastAPI instance with custom OpenAPI documentation paths (`/api/docs`), configures CORS middleware for localhost:5173/3000, establishes request duration logging, and binds a global 500 error handler.",
         [
             ("lifespan(app: FastAPI)", "Async context manager. Initiates MongoDB connection pool and verifies compound indexes on startup; terminates client connection on shutdown.", "Yields execution to running app"),
             ("log_requests(request, call_next)", "HTTP middleware measuring request processing latency in seconds and streaming status logs to console.", "HTTP Response object with timing log"),
             ("global_exception_handler(request, exc)", "Catches unhandled runtime exceptions and returns formatted JSON containing error detail.", "JSONResponse (Status 500)"),
             ("health_check()", "GET /api/health endpoint verifying server runtime, timestamp, and active MongoDB connection status.", "Dict: {status, timestamp, database, version}")
         ]),
        
        ("backend/app/database.py", "MongoDB Client Manager & Compound Indexer",
         "Manages the Motor `AsyncIOMotorClient` singleton pool. Implements automatic compound indexing to accelerate time-series queries and provides collection accessors.",
         [
             ("connect_to_mongo()", "Pings MongoDB database using admin command; executes `init_db_indexes()` upon successful connection.", "None (populates db_manager.db)"),
             ("init_db_indexes()", "Creates compound indexes: (date, threat_type), (threat_type), (severity) on threat_events; (email) on users; (threat_type) on models.", "None (logs creation confirmation)"),
             ("get_database()", "Returns the active `AsyncIOMotorDatabase` instance; raises ConnectionError if uninitialized.", "AsyncIOMotorDatabase object"),
             ("get_threats_collection()", "Helper returning motor collection for `threat_events`.", "AsyncIOMotorCollection")
         ]),

        ("backend/app/api/auth.py", "Authentication & Identity Management Router",
         "Provides analyst and administrator authentication endpoints under `/api/auth` using OAuth2 and JWT bearer tokens.",
         [
             ("register(request: UserRegisterRequest)", "Checks for existing email, hashes password with bcrypt (12 rounds), stores user doc in MongoDB, returns signed JWT.", "TokenResponse: {access_token, token_type, user}"),
             ("login(request: UserLoginRequest)", "Validates plaintext password against stored bcrypt hash, issues signed 24-hour JWT.", "TokenResponse: {access_token, token_type, user}"),
             ("get_me(current_user)", "Protected endpoint extracting user payload via `get_current_user` dependency.", "UserProfileResponse: {id, name, email, role}")
         ]),

        ("backend/app/api/threats.py", "Threat Incident Telemetry Router",
         "Manages query filtering and ingestion of individual cyber threat incidents under `/api/threats`.",
         [
             ("list_threat_events(threat_type, severity, start_date, end_date, limit, skip)", "Executes paginated queries against MongoDB with compound index acceleration.", "Dict: {total, limit, skip, count, data: [events]}"),
             ("create_threat_event(event: ThreatEventCreate)", "Validates threat category, severity rating, date format (YYYY-MM-DD), and positive count before insertion.", "Created Threat Event Dict with MongoDB ObjectId string"),
             ("get_threats_summary()", "Runs aggregation pipelines calculating category totals, severity distributions, most frequent threat, and date bounds.", "ThreatSummaryResponse model")
         ]),

        ("backend/app/api/forecast.py", "Deep Learning Forecasting Router",
         "Executes LSTM forecasting inference under `/api/forecast` and caches predictions in MongoDB.",
         [
             ("create_forecast(request: ForecastRequest)", "Validates category and horizon (1-90 days); calls `forecast_service.get_forecast()`; caches points in `forecasts` collection.", "ForecastResponse schema model"),
             ("get_models_status()", "Inspects disk existence of all 8 `.keras` models, `.joblib` scalers, and test evaluation metrics.", "Dict: {count: 8, models: [status_dict]}"),
             ("get_forecast_by_category(threat_type, days)", "Path-based GET proxy routing to `create_forecast()` for rapid UI switching.", "ForecastResponse schema model")
         ]),

        ("backend/app/api/analytics.py", "SOC Operations Center Analytics Router",
         "Computes enterprise risk postures, KPI summary metrics, and threat risk matrices under `/api/analytics`.",
         [
             ("get_analytics_overview()", "Aggregates total events, 60-day daily network trend, severity breakdowns, and computes 8 risk indicators with in-memory 300s cache.", "AnalyticsOverviewResponse model"),
             ("get_risk_matrix()", "Categorizes 8 threat categories into Critical, High, Medium, Low posture buckets based on composite risk scores.", "Dict: {Critical: [], High: [], Medium: [], Low: []}")
         ]),

        ("backend/app/ml/preprocessor.py", "Data Aggregation & Sliding Window Sequence Generator",
         "Cleans raw CSV incident logs, constructs continuous daily matrices without gaps, engineers 14 time-series features, and creates scaled sequences.",
         [
             ("aggregate_daily_threats(df)", "Groups raw logs by Date and Threat_Type, unstacking into columns, reindexing over continuous date range with fill_value=0.", "Pandas DataFrame: 730 days x 8 categories"),
             ("engineer_features_for_category(daily_series, raw_df, threat)", "Derives 14 features: calendar, rolling means (7, 14, 30), rolling std (7), lags (1, 7, 14), EMA (7), daily change, severities.", "Pandas DataFrame (730, 14)"),
             ("create_sequences(series_values, train_ratio=0.8)", "Fits MinMaxScaler [0, 1], constructs sliding windows: X shape (samples, 30, 1), y shape (samples, 1), splits 80/20.", "Tuple: (X_train, y_train, X_test, y_test, scaler)"),
             ("save_scaler(scaler, threat_type)", "Serializes fitted MinMaxScaler instance to disk using `joblib.dump()`.", "Filepath string to `.joblib` file")
         ]),

        ("backend/app/ml/model.py", "Keras 3 Stacked LSTM Neural Architecture",
         "Constructs, compiles, saves, and loads the deep learning time-series forecasting network.",
         [
             ("build_lstm_model(sequence_length=30, n_features=1, lr=0.003, dropout=0.2)", "Constructs Sequential Keras model: Input(30,1) -> LSTM(64, return_seq=True) -> Dropout(0.2) -> LSTM(32) -> Dropout(0.2) -> Dense(16, relu) -> Dense(1, linear). Compiles with Adam and Huber loss.", "Compiled Keras Sequential Model"),
             ("save_lstm_model(model, threat_type)", "Serializes trained model weights and graph to `.keras` format.", "Filepath string"),
             ("load_lstm_model(threat_type)", "Loads native Keras model from disk for inference.", "Keras Model instance")
         ]),

        ("backend/app/ml/trainer.py", "End-to-End Neural Training Pipeline",
         "Coordinates data preparation, feature engineering, model training with early stopping, evaluation, and MongoDB metadata syncing.",
         [
             ("train_category(threat_type, epochs=30, batch_size=16)", "Trains category LSTM with EarlyStopping (patience=7 on val_loss), evaluates on test split, saves weights and scaler.", "Dict: {threat_type, metrics, metadata, model_path}"),
             ("train_all_categories(epochs=30, batch_size=16)", "Iterates sequentially through all 8 supported threat vectors to produce complete model artifact sets.", "Dict of results for all 8 categories"),
             ("sync_model_metadata_to_mongodb(metadata)", "Upserts training records, test MAE/RMSE/R2, and architecture details into MongoDB `models` collection.", "None")
         ]),

        ("backend/app/ml/evaluator.py", "Forecasting Metrics & Confidence Bounds Engine",
         "Calculates academic forecasting error metrics and statistical uncertainty bands.",
         [
             ("calculate_evaluation_metrics(y_true, y_pred)", "Computes MAE, RMSE, safe MAPE (denom >= 1.0), R2 score, residual standard deviation, and mean actuals.", "Dict: {mae, rmse, mape, r2_score, residual_std, ...}"),
             ("calculate_forecast_confidence_intervals(preds, residual_std, level=0.95)", "Calculates dynamic bounds: pred +/- 1.96 * residual_std * sqrt(1 + t/30), clipping lower bound at 0.", "Tuple: (lower_bounds_array, upper_bounds_array)")
         ]),

        ("backend/app/ml/forecast.py", "Recursive Autoregressive Forecaster & Risk Engine",
         "The runtime inference engine executing multi-step forward rollouts and composite risk scoring.",
         [
             ("forecast(threat_type, forecast_days=30)", "Retrieves latest 30-day window, scales input, loops recursively predicting next day and sliding window, inverts scale, derives bounds and risk.", "Dict matching ForecastResponse schema"),
             ("calculate_risk_profile(threat_type, avg_hist, avg_pred, peak_pred)", "Computes velocity shift %, evaluates volume/trend/burst scores, applies threat severity weight, clips score [5, 98].", "Dict: {risk_score, risk_level, trend_direction, pct_change}")
         ]),

        ("frontend/src/api.js", "Centralized Fetch API Client",
         "Provides client-side HTTP bindings to FastAPI. Automatically extracts and injects JWT Bearer tokens from localStorage, serializes JSON bodies, handles multipart FormData for CSV uploads, and parses HTTP errors.",
         [
             ("generateForecast(threat_type, days)", "Sends POST /api/forecast request with threat category and projection horizon.", "Promise resolving to ForecastResponse JSON"),
             ("getAnalyticsOverview()", "Sends GET /api/analytics/overview request to populate SOC executive dashboard.", "Promise resolving to AnalyticsOverview JSON"),
             ("uploadDatasetFile(file)", "Constructs FormData and sends POST /api/datasets/upload for CSV schema validation and event ingestion.", "Promise resolving to DatasetUploadResponse JSON")
         ])
    ]

    for filename, role, desc, funcs in modules:
        story.append(Paragraph(f"<b>{filename}</b> — {role}", Heading2Style))
        story.append(Paragraph(desc, BodyStyle))
        
        f_table_data = [["Function / Method", "Parameters & Operational Logic", "Return Value"]]
        for f_name, f_logic, f_ret in funcs:
            f_table_data.append([
                Paragraph(f"<b>{f_name}</b>", BodyStyle),
                Paragraph(f_logic, BodyStyle),
                Paragraph(f"<code>{f_ret}</code>", BodyStyle)
            ])
            
        story.append(create_table(
            f_table_data[0],
            f_table_data[1:],
            col_widths=[150, 240, 146],
            custom_header_bg=SECONDARY
        ))
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # =========================================================================
    # 9. CODE EXPLANATION: DEEP ARCHITECTURAL SNIPPETS
    # =========================================================================
    story.append(Paragraph("9. CODE EXPLANATION: CRITICAL CODE SNIPPETS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "To demystify how the platform executes, eight critical code snippets are extracted below, "
        "accompanied by step-by-step explanations of their runtime behavior, inputs, outputs, and design rationale.",
        BodyStyle
    ))

    # Snippet 1: Lifespan
    snippet_1 = (
        "@asynccontextmanager\n"
        "async def lifespan(app: FastAPI):\n"
        "    # Startup: Connect to MongoDB and verify compound indexes\n"
        "    logger.info('Starting up Cyber Threat Forecasting System Backend...')\n"
        "    await connect_to_mongo()\n"
        "    yield\n"
        "    # Shutdown: Close database pool cleanly\n"
        "    logger.info('Shutting down Cyber Threat Forecasting System Backend...')\n"
        "    await close_mongo_connection()"
    )
    story.append(Paragraph("1. Asynchronous Application Lifespan (`backend/app/main.py`)", Heading2Style))
    story.append(create_code_block(snippet_1, caption="FastAPI Lifespan Context Manager"))
    story.append(Paragraph(
        "<b>What this code does:</b> Modern replacement for deprecated `@app.on_event('startup')`. "
        "Upon process launch, FastAPI enters the async context manager and calls `connect_to_mongo()`, which pings the "
        "database and verifies compound indexes. The `yield` statement passes control to the web server to handle requests. "
        "When the process receives a termination signal (SIGINT/SIGTERM), execution resumes after `yield`, closing all socket pools gracefully.<br/>"
        "<b>Input:</b> FastAPI application instance.<br/>"
        "<b>Output:</b> Clean startup/teardown lifecycle without dangling socket descriptors.",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    # Snippet 2: Stacked LSTM
    snippet_2 = (
        "def build_lstm_model(sequence_length=30, n_features=1, learning_rate=0.003, dropout_rate=0.2):\n"
        "    model = Sequential([\n"
        "        Input(shape=(sequence_length, n_features), name='threat_time_series_input'),\n"
        "        LSTM(units=64, return_sequences=True, name='lstm_layer_1'),\n"
        "        Dropout(rate=dropout_rate, name='dropout_1'),\n"
        "        LSTM(units=32, return_sequences=False, name='lstm_layer_2'),\n"
        "        Dropout(rate=dropout_rate, name='dropout_2'),\n"
        "        Dense(units=16, activation='relu', name='dense_hidden'),\n"
        "        Dense(units=1, activation='linear', name='threat_count_output')\n"
        "    ], name='CyberThreatLSTMForecaster')\n"
        "    optimizer = Adam(learning_rate=learning_rate)\n"
        "    loss = Huber(delta=1.0)\n"
        "    model.compile(optimizer=optimizer, loss=loss, metrics=['mae'])\n"
        "    return model"
    )
    story.append(Paragraph("2. Stacked LSTM Neural Network Architecture (`backend/app/ml/model.py`)", Heading2Style))
    story.append(create_code_block(snippet_2, caption="Keras 3 2-Layer Stacked LSTM with Huber Loss"))
    story.append(Paragraph(
        "<b>What this code does:</b> Defines the deep learning neural network. It takes a tensor of shape `(Batch, 30, 1)` "
        "representing 30 consecutive days of normalized threat counts. The first LSTM layer (64 units) has `return_sequences=True` "
        "so it outputs a 3D sequence `(Batch, 30, 64)`, passing temporal representations to the second LSTM layer (32 units). "
        "The second LSTM flattens the temporal dimension into `(Batch, 32)`. Dropout layers (0.20) randomly deactivate 20% of recurrent units "
        "during training to prevent overfitting on rare attack bursts. The Dense(16, relu) layer learns non-linear feature combinations, "
        "and Dense(1, linear) outputs the next day's scaled threat prediction.<br/>"
        "<b>Why Huber Loss:</b> Huber loss acts as quadratic L2 loss for small errors (|error| <= 1.0) and linear L1 loss for large errors. "
        "This prevents explosive gradient updates when extreme cyber attack bursts occur.<br/>"
        "<b>Input:</b> Sequence tensor `(Batch, 30, 1)`. <b>Output:</b> Next-day scalar prediction `(Batch, 1)`.",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    # Snippet 3: Autoregressive Rollout
    snippet_3 = (
        "# 3. Recursive multi-step rollout\n"
        "predicted_scaled = []\n"
        "rolling_input = current_scaled_window.copy()  # Shape: (30, 1)\n"
        "\n"
        "for _ in range(forecast_days):\n"
        "    inp = rolling_input.reshape(1, seq_len, 1)\n"
        "    pred_val = model.predict(inp, verbose=0)[0, 0]\n"
        "    predicted_scaled.append(pred_val)\n"
        "    \n"
        "    # Slide window: drop oldest day, append new prediction\n"
        "    rolling_input = np.vstack([rolling_input[1:], [[pred_val]]])"
    )
    story.append(Paragraph("3. Autoregressive Recursive Rollout (`backend/app/ml/forecast.py`)", Heading2Style))
    story.append(create_code_block(snippet_3, caption="Recursive Sliding Window Inference Loop"))
    story.append(Paragraph(
        "<b>What this code does:</b> Implements multi-step forecasting without requiring multi-output neural heads. "
        "To predict day t+1, the model evaluates the observed window `[t-29 ... t]`. To predict day t+2, the model drops day t-29, "
        "shifts the window forward, and appends the newly predicted `pred_val` at the end. This loop iterates 7, 14, or 30 times. "
        "Once complete, `scaler.inverse_transform()` maps normalized floats back into real incident count numbers.<br/>"
        "<b>Input:</b> Initial observed 30-day scaled array. <b>Output:</b> Array of `forecast_days` future predictions.",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    # Snippet 4: Confidence Cone
    snippet_4 = (
        "for step_idx, pred in enumerate(predictions):\n"
        "    # Uncertainty cone expands into the future: sqrt(1 + t/30)\n"
        "    horizon_factor = np.sqrt(1.0 + (step_idx / 30.0))\n"
        "    margin = z_score * residual_std * horizon_factor\n"
        "    \n"
        "    lower = max(0.0, float(pred - margin))\n"
        "    upper = max(lower, float(pred + margin))\n"
        "    lower_bounds.append(round(lower, 2))\n"
        "    upper_bounds.append(round(upper, 2))"
    )
    story.append(Paragraph("4. Statistical Confidence Interval Calculation (`backend/app/ml/evaluator.py`)", Heading2Style))
    story.append(create_code_block(snippet_4, caption="Expanding Uncertainty Cone Formula"))
    story.append(Paragraph(
        "<b>What this code does:</b> In recursive forecasting, error accumulates over time because each future step feeds on previous "
        "predictions. To represent this mathematically, the confidence margin scales by `horizon_factor = sqrt(1.0 + step/30)`. "
        "The z-score for a 95% two-tailed Gaussian distribution is 1.96. The baseline variance is derived from `residual_std` "
        "(the standard deviation of test set residuals). `lower` is clipped at 0.0 because negative incident counts are physically impossible in cybersecurity.<br/>"
        "<b>Input:</b> Predicted counts array, test set residual standard deviation. <b>Output:</b> Lower and upper bound arrays.",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    # Snippet 5: Risk Scoring Formula
    snippet_5 = (
        "category_weight = THREAT_SEVERITY_WEIGHTS.get(threat_type, 1.0)\n"
        "base_volume_score = min(50.0, (avg_predicted / 2.5))\n"
        "trend_score = min(25.0, max(-15.0, pct_change * 0.5))\n"
        "burst_score = min(25.0, ((peak_predicted - avg_predicted) / max(avg_predicted, 1.0)) * 20.0)\n"
        "\n"
        "raw_score = (base_volume_score + trend_score + burst_score) * category_weight\n"
        "risk_score = round(float(np.clip(raw_score, 5.0, 98.0)), 1)"
    )
    story.append(Paragraph("5. Composite Cyber Risk Scoring Algorithm (`backend/app/ml/forecast.py`)", Heading2Style))
    story.append(create_code_block(snippet_5, caption="Multi-Factor Risk Synthesis Formula"))
    story.append(Paragraph(
        "<b>What this code does:</b> Converts abstract time-series predictions into an actionable SOC decision metric from 0 to 100. "
        "It evaluates three operational dynamics: (1) <b>Base Volume:</b> scales expected attack frequency up to 50 points, "
        "(2) <b>Trend Shift:</b> rewards downward velocity (-15) or penalizes surging volume (+25), and (3) <b>Burst Spike:</b> "
        "penalizes sudden single-day volumetric anomalies (+25). The sum is multiplied by `category_weight` (e.g., Ransomware is 1.4, "
        "DDoS is 1.25, Phishing is 0.95), reflecting organizational impact severity. The final score is clipped between 5.0 and 98.0.",
        BodyStyle
    ))

    story.append(PageBreak())

    # =========================================================================
    # 10. END-TO-END WORKFLOW
    # =========================================================================
    story.append(Paragraph("10. END-TO-END SYSTEM WORKFLOW", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The following diagram and sequential trace illustrate the complete lifecycle of data through the platform—from "
        "initial raw incident ingestion to real-time interactive chart rendering in the SOC analyst browser:",
        BodyStyle
    ))

    # Embed Workflow Diagram
    story.append(create_diagram(
        "workflow_diagram.png",
        "Complete End-to-End Processing, Model Training, Recursive Forecasting, and Visualization Lifecycle",
        width=520,
        height=280
    ))

    workflow_stages = [
        ("Phase 1: Sensory Ingestion", "Raw incident records (Date, Threat_Type, Severity, Count, Source, Location) are ingested via batch CSV upload (`/api/datasets/upload`) or individual REST ingestion (`POST /api/threats`)."),
        ("Phase 2: Validation & Normalization", "`validate_csv_dataset()` inspects mandatory column headers, coerces dates into ISO-8601 strings, verifies recognized threat categories, and writes documents to MongoDB `threat_events`."),
        ("Phase 3: Continuous Daily Aggregation", "`ThreatDataPreprocessor` aggregates log counts by calendar day and threat type. It executes a full date reindexing across the entire 730-day timeline, replacing missing dates with zero counts to guarantee continuous sequence integrity."),
        ("Phase 4: Time-Series Feature Engineering", "The preprocessor calculates 14 engineered features (calendar markers, rolling means over 7/14/30 days, rolling standard deviations, lag features at 1/7/14 days, 7-day EMA, daily delta change, and severity counts) and saves processed category CSVs (`backend/data/processed/daily_[category].csv`)."),
        ("Phase 5: Sliding Window Sequence Generation", "For each threat vector, `create_sequences()` scales daily counts to [0, 1] using MinMaxScaler and constructs sliding windows: input X has shape `(samples, 30, 1)`, target y has shape `(samples, 1)`. Data is split chronologically (80% train = 560 days, 20% test = 140 days)."),
        ("Phase 6: Stacked LSTM Model Training", "`LSTMTrainer` compiles the 2-layer stacked LSTM network (64 units -> 32 units) with Huber loss and Adam optimizer (lr=0.003). It fits the model using EarlyStopping (patience=7 on validation loss) and serializes the best weights (`.keras`) and scaler (`.joblib`)."),
        ("Phase 7: Test Set Performance Evaluation", "The model predicts across the held-out 140 test days. `evaluator.py` calculates MAE, RMSE, MAPE, R2 score, and residual standard deviation, persisting metrics to disk (`.json`) and MongoDB `models`."),
        ("Phase 8: Real-Time Forecast Request", "An analyst on the React dashboard selects a category (e.g., 'DDoS') and horizon (14 days). The client dispatches a POST request to `/api/forecast`."),
        ("Phase 9: Recursive Multi-Step Rollout", "`ThreatForecaster` loads the DDoS model, pulls the latest 30-day historical window from disk/database, scales it, and executes 14 recursive feed-forward passes, dynamically sliding the window at each step."),
        ("Phase 10: Statistical Bounds & Risk Scoring", "Predictions are inverse-transformed. The 95% confidence bounds are generated via `1.96 * residual_std * sqrt(1 + t/30)`. Composite risk score is calculated (e.g., 78.5 -> CRITICAL). Forecast points are cached in MongoDB `forecasts`."),
        ("Phase 11: JSON API Response Delivery", "FastAPI returns structured JSON containing 30 historical points, 14 forecast points with upper/lower bounds, model accuracy metrics, peak projected date, and risk indicators."),
        ("Phase 12: Interactive Canvas Charting", "The React `ForecastView` component receives the payload. Chart.js binds historical points with a solid cyan line, forecast points with a dashed purple line, and the confidence interval with a semi-transparent purple fill band.")
    ]

    for w_stage, w_desc in workflow_stages:
        story.append(Paragraph(f"• <b>{w_stage}:</b> {w_desc}", BulletStyle))
        story.append(Spacer(1, 1.5))

    story.append(PageBreak())
    return story
