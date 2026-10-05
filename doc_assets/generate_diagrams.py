import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def save_fig(fig, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[+] Saved {filepath}")

# Style configuration
BG_DARK = "#0f172a"
PANEL_BG = "#1e293b"
ACCENT_CYAN = "#06b6d4"
ACCENT_PURPLE = "#a855f7"
ACCENT_GREEN = "#10b981"
ACCENT_AMBER = "#f59e0b"
ACCENT_ROSE = "#f43f5e"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#94a3b8"
LINE_COLOR = "#334155"

# 1. SYSTEM ARCHITECTURE DIAGRAM
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    plt.title("CYBER THREAT FORECASTING SYSTEM — MULTI-TIER SYSTEM ARCHITECTURE", 
              color=TEXT_WHITE, fontsize=15, fontweight='bold', pad=15, family='sans-serif')

    def draw_box(x, y, w, h, title, subtitle, color, border_color=None):
        bc = border_color or color
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor=PANEL_BG, edgecolor=bc, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.65, title, color=color, fontsize=10.5, fontweight='bold',
                ha='center', va='center', family='sans-serif')
        ax.text(x + w/2, y + h*0.3, subtitle, color=TEXT_MUTED, fontsize=8,
                ha='center', va='center', family='sans-serif')

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=1.6, mutation_scale=14))
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.15, label, color=TEXT_WHITE, fontsize=7.5, ha='center',
                    backgroundcolor=BG_DARK, family='sans-serif', fontweight='bold')

    # Column 1: Presentation Layer
    ax.text(1.7, 7.7, "PRESENTATION TIER", color=ACCENT_CYAN, fontsize=11, fontweight='bold', ha='center')
    draw_box(0.5, 5.8, 2.4, 1.4, "SOC Analyst Terminal", "Web Browser / HTTPS", TEXT_WHITE, ACCENT_CYAN)
    draw_box(0.5, 3.8, 2.4, 1.6, "React 19 SPA (Vite)", "Chart.js, Lucide Icons\nModular SOC Views", ACCENT_CYAN)
    draw_box(0.5, 1.8, 2.4, 1.4, "State & Storage", "JWT in localStorage\nAxios/Fetch Client", TEXT_MUTED)

    draw_arrow(1.7, 5.8, 1.7, 5.4)
    draw_arrow(1.7, 3.8, 1.7, 3.2)

    # Proxy Arrow
    draw_arrow(2.9, 4.6, 4.3, 4.6, "REST API (JSON)")

    # Column 2: Backend Application Tier
    ax.text(5.5, 7.7, "APPLICATION SERVICE TIER", color=ACCENT_PURPLE, fontsize=11, fontweight='bold', ha='center')
    draw_box(4.3, 5.8, 2.4, 1.4, "FastAPI Web Core", "ASGI / Uvicorn Server\nCORS & Logging Middleware", ACCENT_PURPLE)
    draw_box(4.3, 3.8, 2.4, 1.6, "API Router Mesh", "/auth, /threats, /forecast\n/datasets, /analytics", ACCENT_PURPLE)
    draw_box(4.3, 1.8, 2.4, 1.4, "Security & Auth", "bcrypt (12 rounds)\nJWT HMAC-SHA256 & RBAC", TEXT_MUTED)

    draw_arrow(5.5, 5.8, 5.5, 5.4)
    draw_arrow(5.5, 3.8, 5.5, 3.2)

    # Router to Service & ML
    draw_arrow(6.7, 4.6, 8.1, 5.8, "Service Calls")
    draw_arrow(6.7, 4.6, 8.1, 2.5, "Async Motor Queries")

    # Column 3: ML Engine & Database
    ax.text(9.5, 7.7, "INTELLIGENCE & STORAGE TIER", color=ACCENT_GREEN, fontsize=11, fontweight='bold', ha='center')
    draw_box(8.1, 5.2, 2.8, 2.0, "Deep Learning ML Engine", "8 Dedicated LSTM Models\nMinMaxScaler (.joblib)\nRecursive 7/14/30d Rollout", ACCENT_GREEN)
    draw_box(8.1, 1.5, 2.8, 2.1, "MongoDB Database", "Collections:\n• threat_events  • forecasts\n• datasets  • models  • users", ACCENT_AMBER)

    draw_fig_box = patches.Rectangle((0.2, 0.8), 11.6, 7.2, fill=False, edgecolor=LINE_COLOR, lw=1, ls="--")
    ax.add_patch(draw_fig_box)

    save_fig(fig, "architecture_diagram.png")

# 2. END-TO-END WORKFLOW DIAGRAM
def create_workflow_diagram():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.axis('off')

    plt.title("END-TO-END DATA PROCESSING & RECURSIVE FORECASTING PIPELINE", 
              color=TEXT_WHITE, fontsize=14, fontweight='bold', pad=15)

    steps = [
        ("1. Raw Incident Logs", "17,678 Synthetic Logs\n(Date, Threat, Severity, Count)", ACCENT_CYAN, 0.4, 4.2),
        ("2. Daily Aggregation", "Continuous Daily Matrix\n730 Consecutive Days", ACCENT_CYAN, 2.8, 4.2),
        ("3. Feature Engineering", "14 Features (Rolling, Lag,\nEMA, Calendar, Severity)", ACCENT_CYAN, 5.2, 4.2),
        ("4. Sequence Creation", "Sliding Window: 30x1 Input\nTrain/Test Split (80/20)", ACCENT_PURPLE, 7.6, 4.2),
        ("5. LSTM Training", "2-Layer Stacked LSTM\nEarlyStopping, Huber Loss", ACCENT_PURPLE, 10.0, 4.2),
        
        ("10. SOC Dashboard", "Interactive Visual Chart\nRisk Indicators & Actions", ACCENT_GREEN, 0.4, 1.2),
        ("9. DB Caching", "Store Points in MongoDB\nAudit & Instant Recall", ACCENT_AMBER, 2.8, 1.2),
        ("8. Risk Calculation", "Volume, Velocity, Bursts\nThreat Severity Weighting", ACCENT_ROSE, 5.2, 1.2),
        ("7. Uncertainty Bounds", "95% Confidence Cone\nz * sigma * sqrt(1 + t/30)", ACCENT_GREEN, 7.6, 1.2),
        ("6. Recursive Rollout", "Autoregressive Multi-Step\n7, 14, 30-Day Horizons", ACCENT_PURPLE, 10.0, 1.2),
    ]

    for title, desc, col, x, y in steps:
        rect = patches.FancyBboxPatch((x, y), 2.2, 1.7, boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=PANEL_BG, edgecolor=col, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(x + 1.1, y + 1.2, title, color=col, fontsize=9.5, fontweight='bold', ha='center', va='center')
        ax.text(x + 1.1, y + 0.6, desc, color=TEXT_MUTED, fontsize=8, ha='center', va='center')

    # Top row forward arrows
    for i in range(4):
        ax.annotate('', xy=(steps[i+1][3], steps[i][4] + 0.85), xytext=(steps[i][3] + 2.2, steps[i][4] + 0.85),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=2))

    # Turn down arrow
    ax.annotate('', xy=(11.1, 2.9), xytext=(11.1, 4.2),
                arrowprops=dict(arrowstyle="->", color=ACCENT_PURPLE, lw=2))

    # Bottom row backward arrows
    for i in range(5, 9):
        ax.annotate('', xy=(steps[i+1][3] + 2.2, steps[i][4] + 0.85), xytext=(steps[i][3], steps[i][4] + 0.85),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_GREEN, lw=2))

    save_fig(fig, "workflow_diagram.png")

# 3. LSTM ARCHITECTURE DIAGRAM
def create_lstm_diagram():
    fig, ax = plt.subplots(figsize=(11, 7.5), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    plt.title("STACKED LSTM NEURAL NETWORK ARCHITECTURE FOR THREAT FORECASTING", 
              color=TEXT_WHITE, fontsize=14, fontweight='bold', pad=15)

    layers = [
        ("Input Layer", "threat_time_series_input", "Input Shape: (Batch, 30, 1)\nNormalized Threat Incident Counts", ACCENT_CYAN, 7.0),
        ("LSTM Layer 1", "lstm_layer_1", "64 Hidden Units | return_sequences=True\nExtracts Long-Term Temporal Dependencies", ACCENT_PURPLE, 5.8),
        ("Dropout Layer 1", "dropout_1", "Rate = 0.20 (20% Random Deactivation)\nRegularization Against Attack Surge Overfitting", TEXT_MUTED, 4.8),
        ("LSTM Layer 2", "lstm_layer_2", "32 Hidden Units | return_sequences=False\nCompresses Sequential Latent Representation", ACCENT_PURPLE, 3.8),
        ("Dropout Layer 2", "dropout_2", "Rate = 0.20 (20% Regularization)\nPrevents Co-Adaptation of Recurrent Neurons", TEXT_MUTED, 2.8),
        ("Dense Layer", "dense_hidden", "16 Units | Activation: ReLU\nNon-Linear Feature Mapping", ACCENT_AMBER, 1.8),
        ("Output Layer", "threat_count_output", "1 Unit | Activation: Linear\nOutputs Next-Day Scaled Prediction [0, 1]", ACCENT_GREEN, 0.8),
    ]

    for title, name, desc, col, y in layers:
        rect = patches.FancyBboxPatch((1.5, y), 8.0, 0.75, boxstyle="round,pad=0.06,rounding_size=0.12",
                                      facecolor=PANEL_BG, edgecolor=col, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(2.0, y + 0.38, title, color=col, fontsize=10.5, fontweight='bold', va='center')
        ax.text(4.5, y + 0.38, f"[{name}]", color="#64748b", fontsize=8.5, family='monospace', va='center')
        ax.text(6.0, y + 0.38, desc, color=TEXT_WHITE, fontsize=8, va='center')

    # Connect with arrows
    for i in range(len(layers)-1):
        y_top = layers[i][4]
        y_bot = layers[i+1][4] + 0.75
        ax.annotate('', xy=(5.5, y_bot), xytext=(5.5, y_top),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=1.6))

    save_fig(fig, "lstm_architecture_diagram.png")

# 4. RECURSIVE FORECASTING & CONFIDENCE CONE
def create_forecasting_logic_diagram():
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)

    # Generate synthetic demonstration curve
    t_hist = np.arange(0, 30)
    y_hist = 120 + 20 * np.sin(t_hist / 3) + np.random.normal(0, 5, 30)

    t_future = np.arange(29, 60)
    trend = np.linspace(0, 40, len(t_future))
    y_pred = y_hist[-1] + trend + 15 * np.sin(t_future / 3)
    
    # Confidence bounds
    residual_std = 18.0
    sigma_cone = residual_std * np.sqrt(1 + (t_future - 29)/30.0) * 1.96
    y_upper = y_pred + sigma_cone
    y_lower = np.maximum(0, y_pred - sigma_cone)

    ax.plot(t_hist, y_hist, color=ACCENT_CYAN, lw=2.5, label="Observed 30-Day Historical Incidents (Window)")
    ax.plot(t_future, y_pred, color=ACCENT_PURPLE, lw=2.5, ls="--", label="Autoregressive LSTM Forecast (Multi-Step)")
    ax.fill_between(t_future, y_lower, y_upper, color=ACCENT_PURPLE, alpha=0.18, label="95% Dynamic Confidence Interval [Lower, Upper]")

    ax.axvline(29, color=ACCENT_ROSE, ls=":", lw=1.8, label="Forecast Horizon Cutoff (Day t)")

    ax.set_facecolor(PANEL_BG)
    ax.grid(True, color="#334155", alpha=0.5, linestyle=":")
    ax.set_title("RECURSIVE MULTI-STEP LSTM FORECASTING & UNCERTAINTY CONE DYNAMICS", color=TEXT_WHITE, fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Timeline (Days)", color=TEXT_MUTED, fontsize=9.5)
    ax.set_ylabel("Daily Incident Count", color=TEXT_MUTED, fontsize=9.5)
    ax.tick_params(colors=TEXT_MUTED)

    legend = ax.legend(facecolor=BG_DARK, edgecolor=LINE_COLOR, labelcolor=TEXT_WHITE, loc='upper left', fontsize=8.5)

    save_fig(fig, "recursive_forecast_plot.png")

# 5. RISK SCORING MATRIX
def create_risk_matrix_diagram():
    fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')

    plt.title("COMPOSITE RISK SCORING METHODOLOGY & SOC ESCALATION TIERS", 
              color=TEXT_WHITE, fontsize=14, fontweight='bold', pad=15)

    # 4 Formula Factors
    draw_rect = lambda x, y, w, h, t, s, c: ax.add_patch(
        patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                               facecolor=PANEL_BG, edgecolor=c, linewidth=1.6))

    factors = [
        ("Base Volume (0 - 50)", "min(50, avg_pred / 2.5)", ACCENT_CYAN, 0.5),
        ("Trend Shift (-15 - 25)", "min(25, max(-15, pct_chg * 0.5))", ACCENT_PURPLE, 3.1),
        ("Burst Spike (0 - 25)", "min(25, (peak-avg)/avg * 20)", ACCENT_AMBER, 5.7),
        ("Threat Weight (0.85 - 1.4)", "Ransomware: 1.4, DDoS: 1.25...", ACCENT_ROSE, 8.3),
    ]

    for title, formula, col, x in factors:
        draw_rect(x, 4.0, 2.3, 1.4, title, formula, col)
        ax.text(x + 1.15, 4.95, title, color=col, fontsize=9, fontweight='bold', ha='center')
        ax.text(x + 1.15, 4.4, formula, color=TEXT_WHITE, fontsize=7.5, ha='center', family='monospace')

    # Formula Box
    rect = patches.FancyBboxPatch((1.5, 2.5), 8.0, 1.1, boxstyle="round,pad=0.1,rounding_size=0.12",
                                  facecolor="#090d16", edgecolor=ACCENT_CYAN, linewidth=1.8)
    ax.add_patch(rect)
    ax.text(5.5, 3.2, "Raw Score = (Volume + Trend + Burst) × Threat_Severity_Weight", 
            color=TEXT_WHITE, fontsize=10.5, fontweight='bold', ha='center')
    ax.text(5.5, 2.8, "Final Risk Score = np.clip(Raw Score, 5.0, 98.0)", 
            color=ACCENT_CYAN, fontsize=9.5, family='monospace', ha='center')

    # Escalation Tiers
    tiers = [
        ("CRITICAL (>= 75)", "Immediate Red Alert\nDirect SOC Intervention", ACCENT_ROSE, 0.5),
        ("HIGH (50 - 74)", "High Caution Threat\nIntensified Firewall Probes", ACCENT_AMBER, 3.1),
        ("MEDIUM (25 - 49)", "Elevated Posture\nStandard Tier-2 Review", ACCENT_CYAN, 5.7),
        ("LOW (< 25)", "Normal Baseline\nAutomated Routine Scrubbing", ACCENT_GREEN, 8.3),
    ]

    for title, desc, col, x in tiers:
        draw_rect(x, 0.6, 2.3, 1.5, title, desc, col)
        ax.text(x + 1.15, 1.6, title, color=col, fontsize=9.5, fontweight='bold', ha='center')
        ax.text(x + 1.15, 1.05, desc, color=TEXT_MUTED, fontsize=8, ha='center')

    save_fig(fig, "risk_matrix_diagram.png")

# 6. DATA FLOW DIAGRAM (DFD LEVEL 1)
def create_dfd_diagram():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    plt.title("DATA FLOW DIAGRAM (DFD LEVEL 1) — CYBER THREAT FORECASTING SYSTEM", 
              color=TEXT_WHITE, fontsize=14, fontweight='bold', pad=15)

    def draw_entity(x, y, text):
        rect = patches.Rectangle((x, y), 2.0, 1.1, facecolor="#1e293b", edgecolor=ACCENT_CYAN, lw=2)
        ax.add_patch(rect)
        ax.text(x + 1.0, y + 0.55, text, color=TEXT_WHITE, fontsize=9, fontweight='bold', ha='center', va='center')

    def draw_proc(x, y, num, text):
        circle = patches.Circle((x, y), 0.75, facecolor="#1e293b", edgecolor=ACCENT_PURPLE, lw=2)
        ax.add_patch(circle)
        ax.text(x, y + 0.2, num, color=ACCENT_PURPLE, fontsize=8.5, fontweight='bold', ha='center')
        ax.text(x, y - 0.2, text, color=TEXT_WHITE, fontsize=8, ha='center', va='center')

    def draw_store(x, y, name):
        ax.plot([x, x+2.2], [y+0.6, y+0.6], color=ACCENT_AMBER, lw=2)
        ax.plot([x, x+2.2], [y, y], color=ACCENT_AMBER, lw=2)
        ax.fill_between([x, x+2.2], [y, y], [y+0.6, y+0.6], color="#1e293b")
        ax.text(x + 1.1, y + 0.3, name, color=TEXT_WHITE, fontsize=8.5, ha='center', va='center')

    # Entities
    draw_entity(0.5, 5.0, "SOC Analyst /\nOperator")
    draw_entity(0.5, 1.5, "Network Sensors /\nThreat Feeds")

    # Processes
    draw_proc(4.0, 5.5, "P1", "Authenticate\n& Authorize")
    draw_proc(4.0, 2.0, "P2", "Ingest &\nValidate Logs")
    draw_proc(7.0, 3.8, "P3", "Execute LSTM\nForecaster")
    draw_proc(10.0, 5.5, "P4", "Render SOC\nVisualizations")

    # Data Stores
    draw_store(6.0, 5.7, "D1: Users DB")
    draw_store(6.0, 1.2, "D2: Threat Events")
    draw_store(9.2, 2.0, "D3: Forecast Cache")
    draw_store(9.2, 0.2, "D4: Model Registry")

    # Connectors
    ax.annotate('', xy=(3.25, 5.5), xytext=(2.5, 5.5), arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=1.5))
    ax.annotate('', xy=(3.25, 2.0), xytext=(2.5, 2.0), arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=1.5))
    ax.annotate('', xy=(6.0, 6.0), xytext=(4.75, 5.5), arrowprops=dict(arrowstyle="->", color=ACCENT_PURPLE, lw=1.5))
    ax.annotate('', xy=(6.0, 1.5), xytext=(4.75, 2.0), arrowprops=dict(arrowstyle="->", color=ACCENT_PURPLE, lw=1.5))
    ax.annotate('', xy=(6.5, 3.8), xytext=(4.75, 2.3), arrowprops=dict(arrowstyle="->", color=ACCENT_GREEN, lw=1.5))
    ax.annotate('', xy=(9.25, 5.5), xytext=(7.75, 4.0), arrowprops=dict(arrowstyle="->", color=ACCENT_GREEN, lw=1.5))
    ax.annotate('', xy=(9.2, 2.3), xytext=(7.5, 3.2), arrowprops=dict(arrowstyle="->", color=ACCENT_AMBER, lw=1.5))

    save_fig(fig, "data_flow_diagram.png")

if __name__ == "__main__":
    print("[*] Generating high-resolution technical diagrams...")
    create_architecture_diagram()
    create_workflow_diagram()
    create_lstm_diagram()
    create_forecasting_logic_diagram()
    create_risk_matrix_diagram()
    create_dfd_diagram()
    print("[+] All 6 technical diagrams successfully rendered to doc_assets/!")
