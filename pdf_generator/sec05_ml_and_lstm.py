from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from pdf_generator.styles import (
    Heading1Style, Heading2Style, Heading3Style, BodyStyle, BodyBold, BulletStyle,
    create_callout, create_table, create_diagram, create_code_block,
    PRIMARY, SECONDARY, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_AMBER, ACCENT_ROSE, ACCENT_GREEN,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED
)

def build_section_05():
    story = []

    # =========================================================================
    # 13. MACHINE LEARNING & TIME-SERIES FOUNDATIONS
    # =========================================================================
    story.append(Paragraph("13. MACHINE LEARNING & TIME-SERIES FOUNDATIONS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "To establish academic rigor, this section explains the mathematical rationale behind selecting "
        "recurrent neural architectures over classical machine learning and standard statistical baselines:",
        BodyStyle
    ))

    ml_foundations = [
        ("What is Time-Series Forecasting?", 
         "Unlike cross-sectional tabular learning where samples are independent and identically distributed (i.i.d.), "
         "time-series forecasting involves sequentially ordered observations where observation y(t) depends heavily on "
         "preceding observations y(t-1), y(t-2), ..., y(t-k). The chronological order cannot be randomized."),
        
        ("Why Not Simple Linear Regression?",
         "Linear regression assumes a static linear relationship: y = Wx + b and independent residuals. "
         "Cyber threats exhibit non-linear attack surges, multi-day burst clustering, and complex holiday drops. "
         "Linear regression severely underfits cyber telemetry and cannot capture sequential memory."),
        
        ("Why Not Classical ARIMA / SARIMA?",
         "Autoregressive Integrated Moving Average (ARIMA) models require strict time-series stationarity and linear "
         "lag relationships. Cyber attack telemetry exhibits structural breaks, sudden 4x volumetric DDoS bursts, and "
         "regime changes that violate ARIMA stationarity assumptions, requiring heavy manual differencing per series."),
        
        ("Why Not Random Forest or XGBoost?",
         "Tree ensembles treat sliding window features as independent static columns, failing to capture the continuous "
         "recurrent state dynamics. Furthermore, tree-based models cannot extrapolate trends outside their training target boundaries."),
        
        ("Why Long Short-Term Memory (LSTM)?",
         "Standard Recurrent Neural Networks (RNNs) suffer from vanishing and exploding gradients when propagating errors "
         "over long time windows. LSTM introduces a constant error carousel regulated by three specialized affine gates: "
         "(1) <b>Forget Gate:</b> discards stale attack signatures, (2) <b>Input Gate:</b> encodes newly emerging surge signals, "
         "and (3) <b>Output Gate:</b> projects the updated memory state into the next day's prediction."),
        
        ("Why 8 Separate Specialized Models Instead of One Joint Model?",
         "Different cyber attack categories follow conflicting behavioral physics. DDoS attacks are volumetric weekend floods (4.5x surge); "
         "Phishing attacks peak during enterprise Tuesday–Thursday business hours (1.45x boost); Ransomware displays steady multi-month growth (+0.07/day). "
         "Training a single unified model forces shared weights to compromise across contradictory temporal signals, degrading overall accuracy. "
         "Dedicated models allow each neural network to specialize entirely in its category's unique temporal fingerprint.")
    ]
    for m_title, m_desc in ml_foundations:
        story.append(Paragraph(f"• <b>{m_title}</b> {m_desc}", BulletStyle))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 14. LSTM ARCHITECTURE & HYPERPARAMETERS
    # =========================================================================
    story.append(Paragraph("14. STACKED LSTM NEURAL NETWORK ARCHITECTURE", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The architecture defined in `backend/app/ml/model.py:build_lstm_model()` is a 2-layer stacked "
        "recurrent neural network optimized for robust generalization on noisy incident telemetry:",
        BodyStyle
    ))

    # Embed LSTM diagram
    story.append(create_diagram(
        "lstm_architecture_diagram.png",
        "Layer-by-Layer Architectural Specification of the Cyber Threat LSTM Forecaster",
        width=520,
        height=300
    ))

    layers_spec = [
        ["Layer Index & Name", "Keras Layer Type", "Output Shape", "Param Count", "Activation Function", "Architectural Role"],
        ["0. input_layer", "InputLayer", "(None, 30, 1)", "0", "None", "Receives 30 consecutive normalized incident counts."],
        ["1. lstm_layer_1", "LSTM (64 units)", "(None, 30, 64)", "16,896", "tanh (recurrent: sigmoid)", "Extracts high-level long-term temporal dependencies."],
        ["2. dropout_1", "Dropout (0.20)", "(None, 30, 64)", "0", "None", "Deactivates 20% of recurrent units to mitigate overfitting."],
        ["3. lstm_layer_2", "LSTM (32 units)", "(None, 32)", "12,416", "tanh (recurrent: sigmoid)", "Compresses sequence into compact latent representation."],
        ["4. dropout_2", "Dropout (0.20)", "(None, 32)", "0", "None", "Regularizes latent feature representations."],
        ["5. dense_hidden", "Dense (16 units)", "(None, 16)", "528", "ReLU", "Non-linear feature projection and recombination."],
        ["6. threat_count_output", "Dense (1 unit)", "(None, 1)", "17", "Linear", "Projects scalar next-day normalized forecast value."]
    ]
    story.append(create_table(
        layers_spec[0],
        layers_spec[1:],
        col_widths=[85, 90, 75, 55, 100, 131],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Total Trainable Parameters:</b> 29,857 parameters (~116.6 KB in memory). "
        "This compact parameter count prevents memorization of noise while ensuring rapid inference (~8–12ms per pass on standard CPU).",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    # Training Configuration Table
    story.append(Paragraph("Verified Training Hyperparameters (`backend/app/ml/trainer.py`)", Heading2Style))
    train_params = [
        ["Hyperparameter", "Configured Value", "Operational Function & Implementation Details"],
        ["Sequence Length (Time Window)", "30 Days", "Input lookback horizon required to prime recurrent gates (`DEFAULT_SEQUENCE_LENGTH`)."],
        ["Train / Test Chronological Split", "80% / 20%", "First 560 days for training; held-out last 140 days for final validation."],
        ["Optimization Algorithm", "Adam (lr=0.003)", "Adaptive Moment Estimation with initial learning rate 0.003 for rapid convergence."],
        ["Loss Function", "Huber Loss (delta=1.0)", "Smooth L1/L2 hybrid preventing gradient explosion on cyber attack burst spikes."],
        ["Training Epochs", "30 Epochs", "Upper bound training iterations; controlled by early termination."],
        ["Mini-Batch Size", "16 Samples", "Balances gradient noise for escaping local minima with cache efficiency."],
        ["Early Stopping Callback", "Patience = 7", "Monitors `val_loss`; halts training and restores best weights if no improvement for 7 epochs."],
        ["Feature Scaling", "MinMaxScaler(0, 1)", "Normalizes threat counts to [0, 1] range; prevents gradient saturation in tanh activation."]
    ]
    story.append(create_table(
        train_params[0],
        train_params[1:],
        col_widths=[120, 100, 316],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 15. MODEL EVALUATION METRICS & AUDIT RESULTS
    # =========================================================================
    story.append(Paragraph("15. MODEL EVALUATION METRICS & VERIFIED AUDIT RESULTS", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The model evaluator (`backend/app/ml/evaluator.py`) calculates five rigorous statistical metrics on the held-out 140-day test set. "
        "Below are the mathematical formulas and exact verified performance numbers extracted from `backend/models/lstm/*_metrics.json`:",
        BodyStyle
    ))

    # Metrics formulas
    metric_formulas = (
        "1. Mean Absolute Error (MAE):           MAE = (1/n) * Σ | y_true - y_pred |\n"
        "2. Root Mean Squared Error (RMSE):      RMSE = sqrt( (1/n) * Σ (y_true - y_pred)^2 )\n"
        "3. Mean Absolute Percentage Error (MAPE): MAPE = (1/n) * Σ ( |y_true - y_pred| / max(y_true, 1.0) ) * 100%\n"
        "4. Coefficient of Determination (R²):    R² = 1 - [ Σ (y_true - y_pred)^2 / Σ (y_true - y_mean)^2 ]\n"
        "5. Residual Standard Deviation (σ_res):  σ_res = sqrt( (1/n) * Σ ( (y_true - y_pred) - residual_mean )^2 )"
    )
    story.append(create_code_block(metric_formulas, caption="Evaluation Metrics Mathematical Formulation"))
    story.append(Spacer(1, 8))

    # Master Verified Results Table
    story.append(Paragraph("Verified Model Evaluation Performance Across All 8 Threat Categories", Heading2Style))
    
    perf_table = [
        ["Threat Vector", "Test MAE", "Test RMSE", "Test MAPE (%)", "R² Score", "Residual STD", "Actual Mean", "Predicted Mean", "Model Status"],
        ["Botnet", "26.22", "44.37", "19.07%", "0.504", "44.11", "134.51", "129.71", "Active [Trained]"],
        ["Brute Force", "39.95", "61.50", "23.61%", "0.534", "61.48", "171.21", "172.96", "Active [Trained]"],
        ["Data Breach", "22.66", "43.20", "36.72%", "0.481", "43.04", "67.41", "63.72", "Active [Trained]"],
        ["DDoS", "46.20", "92.12", "31.16%", "0.446", "90.64", "137.97", "121.49", "Active [Trained]"],
        ["Malware", "24.25", "40.61", "20.17%", "0.576", "40.14", "117.66", "111.54", "Active [Trained]"],
        ["Phishing", "66.50", "91.26", "93.18%", "-0.031", "91.07", "159.41", "153.52", "Active [Trained]"],
        ["Ransomware", "40.12", "76.18", "35.95%", "0.352", "75.11", "117.57", "104.90", "Active [Trained]"],
        ["SQL Injection", "13.66", "19.42", "20.95%", "0.566", "19.37", "72.45", "73.78", "Active [Trained]"]
    ]
    story.append(create_table(
        perf_table[0],
        perf_table[1:],
        col_widths=[75, 48, 50, 68, 48, 62, 58, 65, 62],
        custom_header_bg=PRIMARY
    ))
    story.append(Spacer(1, 8))

    # CRITICAL AUDIT FINDING: Negative R2 for Phishing
    story.append(create_callout(
        "<b>CRITICAL AUDIT FINDING — EXPLAINING PHISHING'S NEGATIVE R² (-0.0312):</b><br/>"
        "In standard regression, R² represents the proportion of target variance explained by the model. "
        "While R² is bounded at 1.0 for perfect predictions, <b>R² can be negative</b> when evaluating on a held-out test split "
        "if the sum of squared errors Σ(y_true - y_pred)² exceeds the total variance Σ(y_true - y_mean)².<br/><br/>"
        "• <b>Why it happened on Phishing:</b> In `generate_demo_data.py`, Phishing was configured with severe quarterly blitzes "
        "(seasonal_amp = 25, burst_prob = 0.05, burst_mult = 2.2x). The 140-day test set coincided with extreme, erratic surge blitzes "
        "reaching 342 incidents/day. Because the univariate LSTM predicts smooth trends, the large residual errors during burst peaks "
        "penalized the quadratic numerator heavily, yielding R² = -0.0312 and MAPE = 93.18%.<br/>"
        "• <b>Viva Defense:</b> Do NOT claim all models are highly accurate. Be honest: state that 7 of the 8 models perform well "
        "(R² between 0.352 and 0.576 with MAPE ~19–36%), while Phishing exhibits high burst-variance non-stationarity, demonstrating "
        "the need for multivariate exogenous features (e.g., spam-filter volume) in future iterations.",
        title="ACADEMIC HONESTY AUDIT: NEGATIVE R² EXPLANATION",
        color=ACCENT_ROSE
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 16. FORECASTING LOGIC & UNCERTAINTY ESTIMATION
    # =========================================================================
    story.append(Paragraph("16. RECURSIVE FORECASTING & UNCERTAINTY ESTIMATION", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "The system executes multi-step time-series forecasting using an <b>autoregressive recursive rollout</b> "
        "combined with a <b>dynamic statistical confidence interval</b>:",
        BodyStyle
    ))

    # Embed recursive forecast plot
    story.append(create_diagram(
        "recursive_forecast_plot.png",
        "Recursive Autoregressive Multi-Step Rollout with Dynamic 95% Confidence Interval Cone",
        width=520,
        height=260
    ))

    story.append(Paragraph("Autoregressive Sliding Window Mechanism", Heading2Style))
    story.append(Paragraph(
        "To project 7, 14, or 30 days ahead, the forecaster uses the trained univariate model sequentially:<br/>"
        "• <b>Step 1:</b> Input window `W(0) = [t-29, t-28, ..., t]` -> Predict `p(1)`.<br/>"
        "• <b>Step 2:</b> Shift window: `W(1) = [t-28, t-27, ..., t, p(1)]` -> Predict `p(2)`.<br/>"
        "• <b>Step k:</b> Shift window: `W(k-1) = [t-29+k, ..., p(k-1)]` -> Predict `p(k)`.<br/>"
        "This recursive structure eliminates the need to maintain separate models for every horizon, but errors compound "
        "as the projection horizon extends into the future.",
        BodyStyle
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Dynamic Confidence Interval Formula", Heading2Style))
    story.append(Paragraph(
        "To represent this compounding uncertainty faithfully on the SOC dashboard, the system calculates expanding "
        "confidence intervals based on Gaussian distribution theory:",
        BodyStyle
    ))

    ci_code = (
        "Margin(step) = z × σ_res × sqrt(1 + step / 30)\n"
        "\n"
        "Where:\n"
        "• z = 1.96:               Standard two-tailed critical value for 95% statistical confidence.\n"
        "• σ_res:                  Residual standard deviation measured during test set evaluation (e.g., 40.14 for Malware).\n"
        "• sqrt(1 + step / 30):    Temporal expansion multiplier. At step 0, factor is 1.0; at step 30, factor expands to sqrt(2) ≈ 1.414.\n"
        "• Lower_Bound:            max(0.0, Prediction - Margin) (Constrained to zero; negative incidents are impossible).\n"
        "• Upper_Bound:            Prediction + Margin"
    )
    story.append(create_code_block(ci_code, caption="Dynamic 95% Confidence Interval Formulation"))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 17. COMPOSITE CYBER RISK SCORING ALGORITHM
    # =========================================================================
    story.append(Paragraph("17. COMPOSITE CYBER RISK SCORING ALGORITHM", Heading1Style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(
        "Raw predicted numbers (e.g., '142 DDoS attacks') lack operational context. The risk scoring engine "
        "(`backend/app/ml/forecast.py:calculate_risk_profile()`) transforms quantitative predictions into a "
        "normalized composite score from 0 to 100:",
        BodyStyle
    ))

    # Embed Risk Matrix Diagram
    story.append(create_diagram(
        "risk_matrix_diagram.png",
        "Multi-Factor Composite Risk Synthesis and SOC Escalation Decision Hierarchy",
        width=520,
        height=280
    ))

    risk_factors_table = [
        ["Component", "Score Range", "Mathematical Formulation", "Operational Context"],
        ["Base Volume", "0 to 50 pts", "min(50.0, avg_predicted / 2.5)", "Normalizes expected daily attack density. 125+ attacks/day saturates the maximum 50 points."],
        ["Trend Velocity", "-15 to +25 pts", "min(25.0, max(-15.0, pct_change * 0.5))", "Rewards negative growth (cooling threats) down to -15; penalizes surging attack velocity up to +25."],
        ["Burst Anomaly", "0 to 25 pts", "min(25.0, ((peak - avg) / avg) * 20.0)", "Penalizes isolated high-amplitude spikes that risk overwhelming SOC tier-1 capacity."],
        ["Threat Weight", "0.85 to 1.40x", "Multiplier based on organizational impact severity", "Ransomware (1.40), Breach (1.35), DDoS (1.25), Malware (1.15), Botnet (1.05), SQLi (1.00), Phishing (0.95), Brute Force (0.85)."]
    ]
    story.append(create_table(
        risk_factors_table[0],
        risk_factors_table[1:],
        col_widths=[85, 75, 175, 201],
        custom_header_bg=SECONDARY
    ))
    story.append(Spacer(1, 8))

    # Tier mapping
    story.append(Paragraph(
        "<b>Final Composite Score:</b> <code>Risk_Score = np.clip((Volume + Trend + Burst) × Category_Weight, 5.0, 98.0)</code><br/>"
        "• <b>CRITICAL (>= 75.0):</b> Red Alert. High probability of catastrophic disruption; immediate executive notification.<br/>"
        "• <b>HIGH (50.0 – 74.9):</b> Amber Alert. Elevated attack trajectory; prime firewall scrubbing and activate secondary on-call staff.<br/>"
        "• <b>MEDIUM (25.0 – 49.9):</b> Yellow Status. Normal fluctuations within expected baseline parameters; routine monitoring.<br/>"
        "• <b>LOW (< 25.0):</b> Green Status. Minimal telemetry activity; automated perimeter defenses sufficient.",
        BodyStyle
    ))

    story.append(PageBreak())
    return story
