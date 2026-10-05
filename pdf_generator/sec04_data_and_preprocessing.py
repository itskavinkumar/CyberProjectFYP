from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_AMBER, ACCENT_ROSE,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_04():
    story = []

    # =========================================================================
    # 11. DATASET EXPLANATION & AUDIT
    # =========================================================================
    story.append(Paragraph("11. DATASET EXPLANATION & ARCHITECTURAL AUDIT", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "A rigorous inspection of `backend/data/raw/synthetic_threat_events.csv` was performed. "
        "The file occupies approximately 2.4 MB on disk and contains 17,678 structured rows. "
        "Below is the complete dataset specification:",
        BodyStyle
    ))

    dataset_summary = [
        [Paragraph("<b>Dataset Attribute</b>", BodyBold), Paragraph("<b>Repository Source Verification</b>", BodyBold)],
        ["Canonical File Location", "`backend/data/raw/synthetic_threat_events.csv`"],
        ["Total Recorded Observations", "17,678 incident records"],
        ["Calendar Timeline Range", "2024-01-01 to 2025-12-30 (730 continuous calendar days = 2 full years)"],
        ["Number of Monitored Threat Vectors", "8 distinct categories (Phishing, Malware, Brute Force, DDoS, Botnet, SQLi, Ransomware, Breach)"],
        ["Severity Granularity", "4 standardized levels: Low, Medium, High, Critical"],
        ["Average Records per Day", "~24.2 sub-event logs across all categories (1 to 4 granular reports per category/day)"],
        ["Missing / Null Values", "0 null values across all 7 columns (100% complete)"],
        ["Provenance / Nature", "<b>Synthetic / Generated Data</b> (created via `backend/scripts/generate_demo_data.py`)"]
    ]
    story.append(create_table(
        ["Dataset Attribute", "Repository Source Verification"],
        dataset_summary[1:],
        col_widths=[180, 356],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 10))

    # Dataset Columns Table
    story.append(Paragraph("Dataset Column Schema & Semantic Mapping", Heading2Style))
    
    col_schema = [
        ["Column Name", "Semantic Meaning", "Data Type", "Example Value", "Ingestion Validation Constraint"],
        ["Date", "Calendar day of incident", "ISO String", "2024-05-14", "Must parse as valid YYYY-MM-DD string"],
        ["Threat_Type", "Cyber attack taxonomy category", "String", "Phishing", "Must match one of 8 supported categories"],
        ["Severity", "Assessed organizational impact", "String", "Critical", "Must be Low, Medium, High, or Critical"],
        ["Source", "Reporting sensory appliance", "String", "Email-Gateway", "Defaults to 'Sensor' if omitted"],
        ["Location", "Geographic target / origin", "String", "North America", "Defaults to 'Global' if omitted"],
        ["Count", "Recorded attack volume", "Integer", "42", "Must be positive integer (>= 1)"],
        ["Description", "Telemetry context / signature", "String", "Credential harvesting surge", "Optional narrative text string"]
    ]
    story.append(create_table(
        col_schema[0],
        col_schema[1:],
        col_widths=[75, 125, 60, 110, 166],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 10))

    # Category breakdown table
    story.append(Paragraph("Distribution of Records Across 8 Threat Categories", Heading2Style))
    
    cat_counts = [
        ["Threat Category", "Total Raw Records", "Share of Total", "Historical Mean/Day", "Peak Recorded Day", "Dominant Severity Profile"],
        ["Phishing", "2,245", "12.70%", "159.41", "342 incidents", "Medium (50%), High (25%)"],
        ["Ransomware", "2,244", "12.69%", "117.57", "285 incidents", "Critical (50%), High (40%)"],
        ["Data Breach", "2,228", "12.60%", "67.41", "184 incidents", "High (45%), Critical (40%)"],
        ["SQL Injection", "2,203", "12.46%", "72.45", "168 incidents", "Medium (45%), Low (30%)"],
        ["Brute Force", "2,200", "12.44%", "171.21", "390 incidents", "Low (45%), Medium (40%)"],
        ["Malware", "2,194", "12.41%", "117.66", "264 incidents", "High (40%), Medium (35%)"],
        ["Botnet", "2,189", "12.38%", "134.51", "295 incidents", "Medium (45%), Low (25%)"],
        ["DDoS", "2,175", "12.30%", "137.97", "450 incidents", "High (50%), Critical (25%)"]
    ]
    story.append(create_table(
        cat_counts[0],
        cat_counts[1:],
        col_widths=[85, 80, 70, 95, 95, 111],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 10))

    # How data was generated
    story.append(Paragraph("Mathematical Generation Model in `generate_demo_data.py`", Heading2Style))
    story.append(Paragraph(
        "To ensure the synthetic dataset provided realistic challenges for neural networks, each threat category was simulated "
        "using a multi-component mathematical generator incorporating 5 real-world temporal dynamics:",
        BodyStyle
    ))

    gen_eq = (
        "Total_Daily_Count(t) = [ (Base + Slope × t) × Weekday_Factor + Seasonal_Factor ] × Burst_Factor + Gaussian_Noise\n"
        "\n"
        "Where:\n"
        "1. Base + Slope × t:        Linear macro-trend over the 730-day timeline (e.g., Ransomware slope = +0.07/day)\n"
        "2. Weekday_Factor:          Workweek vs weekend multiplier (e.g., Phishing = 1.45 on weekdays, 0.40 on weekends)\n"
        "3. Seasonal_Factor:         Cyclical sine wave: Amplitude × sin(2π × t / Frequency) (e.g., 90-day quarterly blitzes)\n"
        "4. Burst_Factor:            Markovian multi-day surge state (probability 0.02 - 0.08, duration 2 - 4 days, mult 2.2x - 4.5x)\n"
        "5. Gaussian_Noise:          Stochastic standard normal noise: N(0, Base × 0.12)"
    )
    story.append(create_code_block(gen_eq, caption="Synthetic Telemetry Generator Formula"))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 12. DATA PREPROCESSING & THE 14-FEATURE DISTINCTION
    # =========================================================================
    story.append(Paragraph("12. DATA PREPROCESSING & FEATURE ENGINEERING PIPELINE", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The data preprocessing pipeline (`backend/app/ml/preprocessor.py`) transforms irregular raw logs into structured "
        "training tensors. It executes three fundamental stages: daily aggregation, feature engineering, and sequence generation.",
        BodyStyle
    ))

    story.append(Paragraph("The 14 Domain-Engineered Time-Series Features", Heading2Style))
    story.append(Paragraph(
        "For each threat vector, `engineer_features_for_category()` computes 14 time-series metrics. "
        "These are serialized to `backend/data/processed/daily_[threat].csv`:",
        BodyStyle
    ))

    features_table = [
        ["#", "Feature Column", "Mathematical Logic / Formula", "Domain Meaning & Operational Significance"],
        ["1", "Count", "y(t) = sum(incident counts on day t)", "Target dependent variable; total attack volume recorded across all sensors."],
        ["2", "day_of_week", "t.dayofweek (Integer: 0=Mon, 6=Sun)", "Captures human behavioral cycles (e.g., work-hour spear phishing)."],
        ["3", "day_of_month", "t.day (Integer: 1 to 31)", "Captures monthly accounting and billing cycles targeted by financial fraud."],
        ["4", "month", "t.month (Integer: 1 to 12)", "Captures macro annual seasonality (holiday shopping, fiscal year ends)."],
        ["5", "is_weekend", "int(day_of_week >= 5) (Binary: 0 or 1)", "Isolates automated off-hour bot scans and weekend ransomware execution."],
        ["6", "rolling_mean_7", "(1/7) * sum(Count(t-i) for i=0..6)", "7-day moving average smoothing daily variance to establish baseline."],
        ["7", "rolling_std_7", "sqrt((1/6) * sum((Count(t-i) - mean7)^2))", "Measures short-term volatility; high std flags impending attack burst."],
        ["8", "rolling_mean_14", "(1/14) * sum(Count(t-i) for i=0..13)", "Bi-weekly smoothed trend reflecting sustained campaign persistence."],
        ["9", "rolling_mean_30", "(1/30) * sum(Count(t-i) for i=0..29)", "Monthly operational baseline; serves as reference for velocity change."],
        ["10", "lag_1", "Count(t - 1) (Backward filled at t=0)", "Immediate yesterday volume; fundamental input for autoregression."],
        ["11", "lag_7", "Count(t - 7) (Backward filled)", "Same-day previous week volume; captures weekly periodic autocorrelation."],
        ["12", "lag_14", "Count(t - 14) (Backward filled)", "Two-week cyclical lag tracking recurring reconnaissance sweeps."],
        ["13", "ema_7", "EMA(t) = α * Count(t) + (1-α) * EMA(t-1)", "7-day exponential moving average (α = 2/8); weights recent spikes."],
        ["14", "daily_change", "Count(t) - Count(t - 1)", "First-order difference; captures attack acceleration or deceleration velocity."]
    ]
    story.append(create_table(
        features_table[0],
        features_table[1:],
        col_widths=[20, 95, 175, 246],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 10))

    # CRITICAL AUDIT DISTINCTION: 14 Features vs Univariate LSTM
    story.append(create_callout(
        "<b>CRITICAL SOURCE-CODE AUDIT DISTINCTION — UNIVARIATE VS. MULTIVARIATE:</b><br/>"
        "Although the preprocessing script calculates and persists <b>14 engineered features</b> in `backend/data/processed/`, "
        "inspection of `create_sequences()` in `backend/app/ml/preprocessor.py` (lines 175–187) and `build_lstm_model()` in "
        "`backend/app/ml/model.py` (lines 13–24) proves conclusively that the <b>currently deployed LSTM model is strictly UNIVARIATE</b>.<br/><br/>"
        "• <b>Actual Input Shape:</b> <code>(Batch_Size, 30, 1)</code> — representing precisely 30 consecutive historical days of a single feature: <b>Count</b>.<br/>"
        "• <b>Actual Scaler:</b> A single 1D <code>MinMaxScaler(feature_range=(0, 1))</code> fitted exclusively on incident count.<br/>"
        "• <b>Why this exists:</b> The 14 engineered features were created for exploratory data analysis, visual correlation, and future "
        "multivariate extension, but the active recursive forecasting engine relies exclusively on the univariate time-series sequence. "
        "<b>Never claim in a project viva that the LSTM takes 14 features</b>; state clearly that the deployed model is a univariate 30×1 network.",
        title="IMPORTANT ARCHITECTURAL FINDING: UNIVARIATE MODEL DEPLOYED",
        color=ACCENT_ROSE
    ))

    story.append(PageBreak())
    return story
