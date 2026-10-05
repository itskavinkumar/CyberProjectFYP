import os
import sys
import time

# Ensure workspace root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(BACKEND_DIR)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.trainer import LSTMTrainer

def main():
    print("=" * 75)
    print("      CYBER THREAT FORECASTING SYSTEM - PHASE 2 ML TRAINING PIPELINE      ")
    print("=" * 75)
    print(f"[*] Base Directory:       {settings.BASE_DIR}")
    print(f"[*] Raw Data Path:        {settings.RAW_DATA_PATH}")
    print(f"[*] Processed Data Path:  {settings.PROCESSED_DATA_PATH}")
    print(f"[*] Models Storage Path:  {settings.MODELS_PATH}")
    print(f"[*] Sequence Length:      {settings.DEFAULT_SEQUENCE_LENGTH} days")
    print(f"[*] Threat Categories:    {len(settings.SUPPORTED_THREAT_TYPES)} categories")
    for t in settings.SUPPORTED_THREAT_TYPES:
        print(f"    - {t}")
    print("=" * 75)

    start_time = time.time()
    trainer = LSTMTrainer()

    # 1. Prepare data and feature engineering
    print("\n[STEP 1/3] Ingesting Raw Data, Daily Aggregation & Feature Engineering...")
    daily_matrix = trainer.prepare_data()
    print(f"[+] Aggregated continuous time series: {len(daily_matrix)} days")
    print(f"[+] Processed datasets generated in: {settings.PROCESSED_DATA_PATH}")

    # 2. Train LSTM models for all categories
    print("\n[STEP 2/3] Training Stacked LSTM Models for All 8 Categories...")
    results = trainer.train_all_categories(epochs=30, batch_size=16, verbose=0)

    # 3. Summary reporting
    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print("                    TRAINING PIPELINE EVALUATION SUMMARY                   ")
    print("=" * 75)
    print(f"{'Threat Category':<16} | {'MAE':<8} | {'RMSE':<8} | {'MAPE':<8} | {'R2 Score':<8} | {'Status'}")
    print("-" * 75)

    all_models_exist = True
    for threat_type, res in results.items():
        m = res["metrics"]
        model_exists = os.path.exists(res["model_path"])
        scaler_exists = os.path.exists(res["scaler_path"])
        if not (model_exists and scaler_exists):
            all_models_exist = False
            
        status = "OK [Trained]" if model_exists and scaler_exists else "ERROR [Missing]"
        print(f"{threat_type:<16} | {m['mae']:<8.2f} | {m['rmse']:<8.2f} | {m['mape']:<7.2f}% | {m['r2_score']:<8.3f} | {status}")

    print("=" * 75)
    print(f"[+] Training completed in {elapsed:.2f} seconds.")
    
    if all_models_exist:
        print("[+] SUCCESS: All 8 LSTM models and scalers are verified on disk!")
    else:
        print("[-] WARNING: Some model artifacts were not found on disk.")
        sys.exit(1)

if __name__ == "__main__":
    main()
