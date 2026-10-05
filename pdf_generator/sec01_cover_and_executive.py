from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.colors import HexColor
from pdf_generator.styles import (
    TitleStyle, SubtitleStyle, Heading1Style, Heading2Style, Heading3Style,
    BodyStyle, BodyBold, BulletStyle, create_callout, create_table,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_ROSE, ACCENT_AMBER,
    BG_LIGHT, BG_PANEL, BORDER_COLOR, TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_01():
    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("FINAL YEAR PROJECT TECHNICAL REPORT & VIVA GUIDE", SubtitleStyle))
    story.append(Spacer(1, 10))
    story.append(Paragraph("CYBER THREAT FORECASTING SYSTEM", TitleStyle))
    story.append(Paragraph("A Deep Learning Time-Series Intelligence Platform for Predictive Cybersecurity Operations", SubtitleStyle))
    
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="90%", thickness=2, color=ACCENT_BLUE, spaceBefore=10, spaceAfter=25))
    
    # Metadata Box
    meta_data = [
        [Paragraph("<b>Document Type:</b>", BodyBold), Paragraph("Complete Technical and Functional Project Documentation", BodyStyle)],
        [Paragraph("<b>Project Domain:</b>", BodyBold), Paragraph("Cybersecurity Operations Center (SOC) & Deep Learning Time-Series", BodyStyle)],
        [Paragraph("<b>Student Name:</b>", BodyBold), Paragraph("[Candidate Name / Student Name Placeholder]", BodyStyle)],
        [Paragraph("<b>Register / Roll Number:</b>", BodyBold), Paragraph("[Register Number / Student ID Placeholder]", BodyStyle)],
        [Paragraph("<b>Department:</b>", BodyBold), Paragraph("[Department of Computer Science & Engineering / Information Security]", BodyStyle)],
        [Paragraph("<b>Institution / College:</b>", BodyBold), Paragraph("[College / University Name Placeholder]", BodyStyle)],
        [Paragraph("<b>Academic Year:</b>", BodyBold), Paragraph("2025 – 2026", BodyStyle)],
        [Paragraph("<b>Project Guide / Supervisor:</b>", BodyBold), Paragraph("[Internal Guide / Faculty Advisor Name Placeholder]", BodyStyle)],
        [Paragraph("<b>Core Stack Verified:</b>", BodyBold), Paragraph("FastAPI, React 19, Vite, TensorFlow/Keras 3 (LSTM), MongoDB, Motor", BodyStyle)],
        [Paragraph("<b>Documentation Status:</b>", BodyBold), Paragraph("Audited directly against repository source code (Code as Ground Truth)", BodyStyle)]
    ]
    t_meta = Table(meta_data, colWidths=[150, 360])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#ffffff")),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.4, HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('LINELEFT', (0,0), (0,-1), 3.5, ACCENT_BLUE),
    ]))
    story.append(t_meta)
    
    story.append(Spacer(1, 35))
    story.append(create_callout(
        "<b>ACADEMIC INTEGRITY & CODE VERIFICATION STATEMENT:</b><br/>"
        "This document was constructed through an exhaustive, automated and manual line-by-line audit of the entire "
        "Cyber Threat Forecasting System codebase. Every architectural assertion, machine learning hyperparameter, "
        "REST endpoint schema, database collection definition, and evaluation metric reported herein has been verified "
        "directly against active source code files (main.py, model.py, trainer.py, evaluator.py, forecast.py, and React JSX views). "
        "Discrepancies between generic documentation and actual implementations are explicitly highlighted.",
        title="AUDIT STANDARD: CODE AS GROUND TRUTH",
        color=ACCENT_CYAN
    ))
    
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS OVERVIEW
    # =========================================================================
    story.append(Paragraph("COMPREHENSIVE TABLE OF CONTENTS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=4, spaceAfter=12))
    
    toc_data = [
        [Paragraph("<b>Section</b>", BodyBold), Paragraph("<b>Topic / Functional Dimension</b>", BodyBold), Paragraph("<b>Key Contents & Focus</b>", BodyBold)],
        ["Section 1", "Executive Summary & Core Foundations", "Problem statement, objectives, reactive vs. predictive paradigm, use case"],
        ["Section 2", "Technology Stack & System Architecture", "Frontend, backend, ML libraries, MongoDB, multi-tier system diagrams"],
        ["Section 3", "Project Structure & Codebase Audit", "File tree, program-by-program review, line-by-line critical code explanations"],
        ["Section 4", "Dataset Analysis & Feature Engineering", "Synthetic event log schema, 14 engineered features vs. univariate 30x1 input"],
        ["Section 5", "Deep Learning ML Engine & LSTM Architecture", "Stacked LSTM (64-32), Huber loss, EarlyStopping, recursive forecasting"],
        ["Section 6", "Model Performance & 8 Threat Models", "MAE, RMSE, MAPE, R2, Residual STD, Phishing negative R2 analysis"],
        ["Section 7", "Uncertainty Bounds & Composite Risk Scoring", "95% confidence interval formula, volume/trend/burst risk matrix"],
        ["Section 8", "Backend Architecture & REST API Documentation", "FastAPI routers, lifespan, CORS, middleware, full endpoint catalog"],
        ["Section 9", "Database Architecture & Security", "MongoDB collections, compound indexes, bcrypt password hashing, JWT RBAC"],
        ["Section 10", "Frontend Architecture & Operational UI", "React 19, Chart.js visualization, 5 view tabs, state & auth lifecycle"],
        ["Section 11", "End-to-End Traces & Lifecycle Walks", "DDoS 14-day walkthrough, sequence diagram, data flow diagrams (DFD)"],
        ["Section 12", "Installation, Execution & Testing Guide", "Step-by-step Windows setup, environment variables, pytest suite review"],
        ["Section 13", "Limitations, Future Enhancements & Defense", "Weaknesses, roadmap, beginner explanation, 30s/1m/3m elevator pitches"],
        ["Section 14", "Comprehensive Viva Q&A & Technical Defense", "55 categorized viva questions + 30 difficult technical viva inquiries"],
        ["Section 15", "Technical Glossary & Final Synthesis", "Exhaustive cybersecurity/AI terms dictionary and architectural summary"]
    ]
    story.append(create_table(
        ["Section", "Topic / Functional Dimension", "Key Contents & Focus"],
        toc_data[1:],
        col_widths=[60, 200, 276],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # 1. EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. EXECUTIVE SUMMARY", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The <b>Cyber Threat Forecasting System</b> (internally styled as <i>CyberGuard AI</i>) is an enterprise-grade "
        "cybersecurity intelligence and predictive operations platform designed to forecast future daily incident volumes "
        "across eight specialized cyber threat categories. Developed as an academic Final Year Project (FYP), the system "
        "bridges the critical operational gap between traditional reactive security monitoring and forward-looking, "
        "predictive risk management.",
        BodyStyle
    ))
    
    story.append(Paragraph(
        "Conventional Security Operations Center (SOC) tooling—such as Security Information and Event Management (SIEM) systems, "
        "Intrusion Detection Systems (IDS), and Next-Generation Firewalls (NGFW)—operates on a <b>reactive detection paradigm</b>. "
        "These tools alert analysts only after malicious packets have crossed network boundaries or while malicious execution is underway. "
        "In contrast, the Cyber Threat Forecasting System operates on a <b>predictive cybersecurity paradigm</b>. By analyzing historical "
        "attack telemetry, identifying complex multi-week seasonal trends, and capturing autoregressive temporal dynamics, the system "
        "forecasts upcoming attack volumes 7, 14, and 30 days into the future.",
        BodyStyle
    ))

    # Reactive vs Predictive Comparison Box
    rvp_data = [
        [Paragraph("<b>Architectural Dimension</b>", BodyBold), Paragraph("<b>Reactive Cybersecurity (Traditional SOC)</b>", BodyBold), Paragraph("<b>Predictive Cybersecurity (This Project)</b>", BodyBold)],
        ["Primary Operational Goal", "Detect attacks currently occurring or recently breached.", "Anticipate attack surges days or weeks in advance."],
        ["Data Utilization", "Real-time streaming packets, immediate rule triggers.", "Continuous multi-year daily aggregated time-series telemetry."],
        ["Analytical Core", "Signature matching, static thresholds, heuristic alerts.", "Deep Learning Recurrent Networks (Stacked LSTM with Huber loss)."],
        ["Temporal Horizon", "t = 0 (Present moment anomaly / alert).", "t + 7, t + 14, t + 30 days into the future."],
        ["SOC Impact", "Ad-hoc fire-fighting, analyst burnout, alert fatigue.", "Proactive SOC shift staffing, preemptive firewall hardening."],
        ["Uncertainty Handling", "Binary detection flags (True Positive vs. False Alarm).", "95% statistical confidence cones based on model residual STD."],
        ["Output Artifact", "Security alert tickets and incident response logs.", "Forecast curves, expected incident counts, and composite risk scores."]
    ]
    story.append(create_table(
        ["Architectural Dimension", "Reactive Cybersecurity (Traditional SOC)", "Predictive Cybersecurity (This Project)"],
        rvp_data[1:],
        col_widths=[110, 210, 216],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 10))

    # Core Answers
    story.append(Paragraph("Core Questions Addressed by the Platform", Heading2Style))
    
    q_answers = [
        ("What is this project?", "An end-to-end full-stack cybersecurity web application consisting of a React 19 frontend, a FastAPI asynchronous backend, a Motor-driven MongoDB document store, and a deep learning inference engine utilizing 8 separate TensorFlow/Keras Long Short-Term Memory (LSTM) neural networks."),
        ("What problem does it solve?", "It eliminates the vulnerability window of reactive security operations by giving SOC leaders mathematical foresight into upcoming attack surges, enabling tactical resource allocation and infrastructure readiness before attacks peak."),
        ("Why is cyber threat forecasting needed?", "Modern cyber warfare and automated botnet campaigns exhibit cyclical rhythms, seasonal bursts, and weekday/weekend patterns. Threat actors scan systems and execute ransomware strategically. Forecasting transforms historical log noise into actionable defense planning."),
        ("Who uses this system?", "Tier-1 to Tier-3 SOC Analysts, Threat Intelligence Specialists, Chief Information Security Officers (CISOs), and IT Infrastructure Directors responsible for enterprise perimeter security."),
        ("What does the system predict?", "The precise expected count of cyber attack incidents for 8 threat categories (Phishing, Malware, Brute Force, DDoS, Botnet, SQL Injection, Ransomware, Data Breach) across 7, 14, and 30-day forecast horizons, bounded by upper and lower 95% confidence intervals."),
        ("What technologies are used?", "React 19, Vite, Chart.js, Lucide Icons, Python 3.11, FastAPI, Uvicorn, Pydantic v2, Motor, MongoDB, TensorFlow 2.15 (Keras 3), scikit-learn, Joblib, passlib/bcrypt, and python-jose (JWT)."),
        ("What is the final output?", "An interactive dashboard visualizing historical timelines alongside projected forecast curves, confidence cones, peak attack dates, velocity shift percentages, and a composite risk score (0 to 100) with SOC escalation levels.")
    ]
    for q, a in q_answers:
        story.append(Paragraph(f"• <b>{q}</b> {a}", BulletStyle))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 2. PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("2. PROBLEM STATEMENT", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Modern enterprise networks generate millions of security logs every twenty-four hours. Despite heavy capital "
        "investments in SIEM appliances and intrusion detection frameworks, organizations continue to suffer from catastrophic breaches "
        "and debilitating ransomware lockouts. The fundamental systemic deficiencies in current cybersecurity operations include:",
        BodyStyle
    ))
    
    problems = [
        ("Inherent Latency of Reactive Monitoring:", "Security telemetry is predominantly analyzed retroactively. An incident is investigated only after an alert fires, which frequently occurs after sensitive data has been staged for exfiltration or host storage has been encrypted."),
        ("SOC Fatigue and Resource Mismatch:", "SOC operations struggle with static staffing schedules. Threat surges (e.g., weekend brute-force password spraying or holiday ransomware deployments) frequently coincide with minimal analyst coverage, resulting in missed critical alerts."),
        ("Failure to Exploit Time-Series Dynamics:", "Firewall and IDS logs contain rich temporal signatures—such as weekly rhythms, seasonal blitzes, and autoregressive clustering. Traditional monitoring systems treat each day's logs in isolation, completely ignoring the macro-temporal signals that predict future volume surges."),
        ("Bursty Non-Linear Threat Trajectories:", "Cyber attacks do not follow simple linear trends. A distributed denial-of-service (DDoS) reflection flood or automated SQLMap sweep causes exponential, multi-day spikes. Standard linear regression and classical statistical models (such as ARIMA) struggle to capture these non-linear temporal dependencies."),
        ("Lack of Unified Predictive Risk Scoring:", "Raw log metrics fail to communicate operational urgency. SOC decision-makers require an automated bridge connecting raw incident predictions with quantifiable risk indicators (Low, Medium, High, Critical) to trigger preventive counter-measures.")
    ]
    for p_title, p_desc in problems:
        story.append(Paragraph(f"<b>{p_title}</b> {p_desc}", BulletStyle))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. VERIFIED PROJECT OBJECTIVES
    # =========================================================================
    story.append(Paragraph("3. VERIFIED PROJECT OBJECTIVES", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "To resolve the stated problem, the project established twelve functional objectives. "
        "Each objective has been audited and confirmed directly within the codebase:",
        BodyStyle
    ))

    objectives = [
        ("1. Ingest Structured Threat Telemetry", "Verified in `app/api/threats.py` and `app/api/datasets.py` through multi-source event logging and CSV dataset ingestion pipelines."),
        ("2. Enforce Time-Series Continuity", "Verified in `app/ml/preprocessor.py:aggregate_daily_threats()`, which guarantees zero date gaps by reindexing daily matrices across a continuous 730-day timeline."),
        ("3. Engineer Domain-Specific Features", "Verified in `app/ml/preprocessor.py:engineer_features_for_category()`, generating 14 temporal, rolling statistical, lag, and exponential moving average metrics."),
        ("4. Construct Specialized LSTM Architectures", "Verified in `app/ml/model.py:build_lstm_model()`, deploying a 2-layer stacked LSTM network (64 units -> 32 units) with dropout regularization (0.20) and Huber loss."),
        ("5. Maintain 8 Dedicated Category Models", "Verified in `models/lstm/`, maintaining independent weights and scalers for Phishing, Malware, Brute Force, DDoS, Botnet, SQL Injection, Ransomware, and Data Breach."),
        ("6. Autoregressive Multi-Step Rollout", "Verified in `app/ml/forecast.py:forecast()`, executing recursive multi-step forecasting across 7, 14, and 30-day operational horizons."),
        ("7. Calculate Dynamic Confidence Cones", "Verified in `app/ml/evaluator.py:calculate_forecast_confidence_intervals()`, expanding uncertainty margins with horizon depth via residual standard deviation scaling."),
        ("8. Compute Composite Risk Scores", "Verified in `app/ml/forecast.py:calculate_risk_profile()`, synthesizing predicted incident volume, velocity shift, burst magnitude, and category weights into a 0–100 score."),
        ("9. Deliver Interactive Web Dashboard", "Verified in `frontend/src/`, providing an operator UI with Chart.js dual-axis trendlines, risk badges, and telemetry inspection tables."),
        ("10. Implement Robust JWT Security & RBAC", "Verified in `app/utils/security.py` and `app/api/auth.py`, enforcing bcrypt (12 rounds) password hashing, signed HS256 JWT tokens, and role-based permissions."),
        ("11. Asynchronous Document Persistence", "Verified in `app/database.py`, connecting to MongoDB using Motor, managing automated compound indexes across 5 enterprise collections."),
        ("12. Automated Self-Documentation", "Verified in `app/main.py`, providing interactive Swagger/OpenAPI documentation at `/api/docs` and Redoc at `/api/redoc`.")
    ]
    for o_name, o_code in objectives:
        story.append(Paragraph(f"• <b>{o_name}:</b> {o_code}", BulletStyle))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 4. REAL-WORLD USE CASE & SOC WORKFLOW
    # =========================================================================
    story.append(Paragraph("4. REAL-WORLD USE CASE: PROACTIVE SOC OPERATIONS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "To understand the practical deployment of this platform, consider a realistic enterprise scenario at a "
        "Global Financial Institution monitored by a 24/7 Security Operations Center:",
        BodyStyle
    ))

    use_case_steps = [
        ("Step 1: Ingestion of Sensory Logs", "Firewall, Email Gateway, Web Application Firewall (WAF), and Endpoint Detection and Response (EDR) sensors stream incident records into the FastAPI `/api/threats` ingestion pipeline."),
        ("Step 2: Database Consolidation & Aggregation", "The Motor asynchronous database driver indexes incoming incidents in MongoDB. The ML preprocessing pipeline aggregates events into daily count series per threat vector."),
        ("Step 3: Neural Model Inference Execution", "Every morning at 00:00 UTC, or on-demand via the SOC Analyst dashboard, the `ThreatForecaster` engine loads the latest 30-day observed incident window into the category-specific LSTM network."),
        ("Step 4: Multi-Step Autoregressive Projection", "The LSTM model iteratively predicts day t+1, re-injects the predicted count into the sliding input window, and projects 14 days forward. The model forecasts a 64% surge in DDoS UDP amplification attacks peaking on Saturday."),
        ("Step 5: Statistical Confidence & Risk Escalation", "The evaluator calculates a 95% confidence interval (e.g., 280 ± 38 attacks) and computes a Composite Risk Score of 88.4/100, automatically categorizing the threat vector as <b>CRITICAL</b>."),
        ("Step 6: Dashboard Presentation & Alerting", "The React 19 SOC Overview highlights the upcoming DDoS surge in the Threat Risk Matrix, displaying the peak date, velocity percentage, and underlying contributing factors."),
        ("Step 7: Proactive Defensive Interventions", "Armed with 5 days of advance warning, the SOC Director takes preventive action: (a) contacts upstream ISP cloud scrubbing centers to prime BGP flow-redirection rules, (b) schedules double-shift senior Tier-2 network engineers for Saturday, and (c) rate-limits peripheral external API gateways.")
    ]
    for s_title, s_desc in use_case_steps:
        story.append(Paragraph(f"<b>{s_title}:</b> {s_desc}", BulletStyle))
    story.append(Spacer(1, 8))

    story.append(create_callout(
        "<b>DATASET DISCLOSURE & SOURCE TRUTH:</b><br/>"
        "The current codebase uses a <b>synthetically generated historical dataset</b> (`synthetic_threat_events.csv`) containing "
        "17,678 records spanning 730 continuous days (2024-01-01 to 2025-12-30). Generated via `backend/scripts/generate_demo_data.py`, "
        "it models realistic cyber attack dynamics including linear macro trends, weekday work-hour boosts, weekend vulnerability scans, "
        "quarterly blitz seasonality, random stochastic noise, and multi-day attack burst states. While the data is synthetic, the entire "
        "FastAPI pipeline, preprocessing logic, LSTM architectures, and MongoDB schemas are 100% production-ready and fully compatible "
        "with real-world SIEM exports (Splunk, Elastic, Sentinel).",
        title="DATASET PROVENANCE AUDIT FINDING",
        color=ACCENT_AMBER
    ))

    story.append(PageBreak())
    return story
