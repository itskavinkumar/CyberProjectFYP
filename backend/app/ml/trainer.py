import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.preprocessor import ThreatDataPreprocessor, get_threat_slug
from backend.app.ml.model import build_lstm_model, save_lstm_model
from backend.app.ml.evaluator import calculate_evaluation_metrics, save_evaluation_metrics

class LSTMTrainer:
    """
    Orchestrates the end-to-end training pipeline for LSTM models across
    all 8 supported cyber threat categories.
    Handles data preprocessing, sequence generation, model training,
    test set evaluation, disk persistence, and database metadata registration.
    """

    def __init__(
        self,
        raw_csv_path: Optional[str] = None,
        sequence_length: int = settings.DEFAULT_SEQUENCE_LENGTH,
        learning_rate: float = 0.003
    ):
        self.preprocessor = ThreatDataPreprocessor(
            raw_csv_path=raw_csv_path,
            sequence_length=sequence_length
        )
        self.sequence_length = sequence_length
        self.learning_rate = learning_rate
        self.daily_matrix: Optional[pd.DataFrame] = None
        self.raw_df: Optional[pd.DataFrame] = None

    def prepare_data(self) -> pd.DataFrame:
        """Loads and preprocesses raw threat data into continuous daily series."""
        logger.info("Starting data preparation and feature engineering...")
        self.raw_df = self.preprocessor.load_raw_dataset()
        self.daily_matrix = self.preprocessor.aggregate_daily_threats(self.raw_df)
        
        # Save processed CSVs
        saved_paths = self.preprocessor.save_processed_datasets(
            daily_matrix=self.daily_matrix,
            raw_df=self.raw_df
        )
        logger.info(f"Feature engineering and processed files created for {len(saved_paths)} datasets.")
        return self.daily_matrix

    def sync_model_metadata_to_mongodb(self, metadata: Dict[str, Any]):
        """Persists trained model metadata to MongoDB 'models' collection."""
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            db = client[settings.DATABASE_NAME]
            
            db.models.update_one(
                {"threat_type": metadata["threat_type"]},
                {"$set": metadata},
                upsert=True
            )
            client.close()
            logger.info(f"Model metadata registered in MongoDB for: {metadata['threat_type']}")
        except Exception as e:
            logger.warning(f"Failed to sync metadata to MongoDB (database may be offline): {str(e)}")

    def train_category(
        self,
        threat_type: str,
        epochs: int = 30,
        batch_size: int = 16,
        verbose: int = 0
    ) -> Dict[str, Any]:
        """
        Trains and evaluates an LSTM forecaster for a single threat category.
        """
        if threat_type not in settings.SUPPORTED_THREAT_TYPES:
            raise ValueError(f"Threat type '{threat_type}' is not supported. Supported: {settings.SUPPORTED_THREAT_TYPES}")

        if self.daily_matrix is None:
            self.prepare_data()

        logger.info(f"=== Starting Training for Threat Category: {threat_type} ===")
        series_values = self.daily_matrix[threat_type].values
        
        # 1. Sequence generation & scaling
        X_train, y_train, X_test, y_test, scaler = self.preprocessor.create_sequences(
            series_values=series_values,
            train_ratio=0.8
        )
        
        # 2. Save fitted scaler
        scaler_path = self.preprocessor.save_scaler(scaler, threat_type)
        
        # 3. Build LSTM architecture
        model = build_lstm_model(
            sequence_length=self.sequence_length,
            n_features=1,
            learning_rate=self.learning_rate
        )
        
        # 4. Train with EarlyStopping
        early_stopping = EarlyStopping(
            monitor="val_loss",
            patience=7,
            restore_best_weights=True,
            verbose=verbose
        )
        
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            verbose=verbose
        )
        
        # 5. Evaluate on test set
        y_pred_scaled = model.predict(X_test, verbose=0)
        y_pred = scaler.inverse_transform(y_pred_scaled).ravel()
        y_true = scaler.inverse_transform(y_test).ravel()
        
        metrics = calculate_evaluation_metrics(y_true, y_pred)
        logger.info(
            f"[{threat_type}] Evaluated on {len(y_test)} test days -> "
            f"MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}, MAPE: {metrics['mape']:.2f}%"
        )
        
        # 6. Save model and metrics to disk
        model_path = save_lstm_model(model, threat_type)
        metrics_path = save_evaluation_metrics(metrics, threat_type)
        
        # 7. Construct metadata matching ModelMetadataModel schema
        metadata = {
            "threat_type": threat_type,
            "model_name": f"{threat_type} LSTM Forecaster",
            "model_version": "v1.0.0",
            "training_date": datetime.utcnow().isoformat(),
            "training_records": len(X_train),
            "test_records": len(X_test),
            "sequence_length": self.sequence_length,
            "architecture": "2-Layer Stacked LSTM (64, 32) + Dropout(0.2) + Dense(16, 1)",
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "mape": metrics["mape"],
            "r2_score": metrics["r2_score"],
            "residual_std": metrics["residual_std"],
            "status": "active",
            "model_file": os.path.basename(model_path),
            "scaler_file": os.path.basename(scaler_path),
            "metrics_file": os.path.basename(metrics_path)
        }
        
        # 8. Sync to MongoDB
        self.sync_model_metadata_to_mongodb(metadata)
        
        return {
            "threat_type": threat_type,
            "metrics": metrics,
            "metadata": metadata,
            "model_path": model_path,
            "scaler_path": scaler_path,
            "metrics_path": metrics_path,
            "epochs_trained": len(history.history["loss"])
        }

    def train_all_categories(
        self,
        epochs: int = 30,
        batch_size: int = 16,
        verbose: int = 0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Trains and persists LSTM models for all 8 supported threat categories sequentially.
        """
        logger.info(f"Starting training across all {len(settings.SUPPORTED_THREAT_TYPES)} threat categories...")
        self.prepare_data()
        
        results = {}
        for idx, threat_type in enumerate(settings.SUPPORTED_THREAT_TYPES, start=1):
            logger.info(f"Progress: [{idx}/{len(settings.SUPPORTED_THREAT_TYPES)}] Training {threat_type}...")
            result = self.train_category(
                threat_type=threat_type,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose
            )
            results[threat_type] = result
            
        logger.info("[+] Completed training for all 8 threat categories successfully!")
        return results
