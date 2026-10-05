import os
import json
from typing import Tuple, Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

from backend.app.config import settings
from backend.app.utils.logging import logger

def get_threat_slug(threat_type: str) -> str:
    """Convert human-readable threat name to filesystem-safe slug."""
    return threat_type.strip().lower().replace(" ", "_").replace("-", "_")

class ThreatDataPreprocessor:
    """
    Handles data ingestion, daily aggregation, time-series continuity,
    feature engineering, and sequence generation for LSTM training.
    """

    def __init__(
        self,
        raw_csv_path: Optional[str] = None,
        processed_dir: Optional[str] = None,
        models_dir: Optional[str] = None,
        sequence_length: int = settings.DEFAULT_SEQUENCE_LENGTH
    ):
        self.raw_csv_path = raw_csv_path or os.path.join(settings.RAW_DATA_PATH, "synthetic_threat_events.csv")
        self.processed_dir = processed_dir or settings.PROCESSED_DATA_PATH
        self.models_dir = models_dir or settings.MODELS_PATH
        self.sequence_length = sequence_length
        
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

    def load_raw_dataset(self) -> pd.DataFrame:
        """Load raw dataset from CSV file."""
        if not os.path.exists(self.raw_csv_path):
            raise FileNotFoundError(f"Raw dataset not found at: {self.raw_csv_path}")
        
        df = pd.read_csv(self.raw_csv_path)
        logger.info(f"Loaded raw dataset from {self.raw_csv_path} with {len(df):,} records.")
        return df

    def aggregate_daily_threats(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Aggregates raw incident logs into a continuous daily time-series
        matrix for all supported threat categories.
        Guarantees no missing dates between min_date and max_date.
        """
        if df is None:
            df = self.load_raw_dataset()

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]
        date_col = next(c for c in df.columns if c.lower() == "date")
        threat_col = next(c for c in df.columns if "threat" in c.lower())
        count_col = next(c for c in df.columns if c.lower() == "count")
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Group by Date and Threat_Type
        grouped = df.groupby([date_col, threat_col])[count_col].sum().unstack(fill_value=0)
        
        # Ensure all supported threat types are present as columns
        for threat in settings.SUPPORTED_THREAT_TYPES:
            if threat not in grouped.columns:
                grouped[threat] = 0
                
        grouped = grouped[settings.SUPPORTED_THREAT_TYPES]
        
        # Ensure continuous daily date index
        min_date = grouped.index.min()
        max_date = grouped.index.max()
        continuous_idx = pd.date_range(min_date, max_date, freq="D")
        daily_df = grouped.reindex(continuous_idx, fill_value=0)
        daily_df.index.name = "Date"
        
        logger.info(f"Daily aggregation completed: {len(daily_df)} days across {len(daily_df.columns)} threat types.")
        return daily_df

    def engineer_features_for_category(
        self,
        daily_series: pd.Series,
        raw_events_df: Optional[pd.DataFrame] = None,
        threat_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculates time-series features for a specific threat category:
        - Temporal/Calendar features (day_of_week, day_of_month, month, is_weekend)
        - Rolling statistics (rolling_mean_7, rolling_std_7, rolling_mean_14, rolling_mean_30)
        - Lag features (lag_1, lag_7, lag_14)
        - Exponential moving average (ema_7)
        - Rate of change (daily_change)
        - Granular severity counts (if raw_events_df provided)
        """
        df = pd.DataFrame({"Count": daily_series.values}, index=daily_series.index)
        
        # Calendar features
        df["day_of_week"] = df.index.dayofweek
        df["day_of_month"] = df.index.day
        df["month"] = df.index.month
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        
        # Rolling statistics
        df["rolling_mean_7"] = df["Count"].rolling(window=7, min_periods=1).mean()
        df["rolling_std_7"] = df["Count"].rolling(window=7, min_periods=1).std().fillna(0)
        df["rolling_mean_14"] = df["Count"].rolling(window=14, min_periods=1).mean()
        df["rolling_mean_30"] = df["Count"].rolling(window=30, min_periods=1).mean()
        
        # Lag features (with backward-fill for the first few days)
        df["lag_1"] = df["Count"].shift(1).bfill()
        df["lag_7"] = df["Count"].shift(7).bfill()
        df["lag_14"] = df["Count"].shift(14).bfill()
        
        # Exponential moving average
        df["ema_7"] = df["Count"].ewm(span=7, adjust=False).mean()
        
        # Daily change
        df["daily_change"] = df["Count"] - df["lag_1"]
        
        # Severity breakdowns if raw event data is provided
        if raw_events_df is not None and threat_type is not None:
            sub = raw_events_df[raw_events_df["Threat_Type"] == threat_type].copy()
            sub["Date"] = pd.to_datetime(sub["Date"])
            for sev in ["Low", "Medium", "High", "Critical"]:
                sev_counts = sub[sub["Severity"] == sev].groupby("Date")["Count"].sum()
                df[f"severity_{sev.lower()}"] = sev_counts.reindex(df.index, fill_value=0)
                
        return df

    def save_processed_datasets(
        self,
        daily_matrix: pd.DataFrame,
        raw_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, str]:
        """
        Saves master daily aggregated dataset and per-category processed feature CSVs
        to settings.PROCESSED_DATA_PATH.
        """
        saved_paths = {}
        
        # Save master summary CSV
        summary_path = os.path.join(self.processed_dir, "daily_threats_summary.csv")
        daily_matrix.to_csv(summary_path)
        saved_paths["master_summary"] = summary_path
        
        # Save each category with engineered features
        for threat_type in daily_matrix.columns:
            slug = get_threat_slug(threat_type)
            cat_df = self.engineer_features_for_category(
                daily_series=daily_matrix[threat_type],
                raw_events_df=raw_df,
                threat_type=threat_type
            )
            cat_path = os.path.join(self.processed_dir, f"daily_{slug}.csv")
            cat_df.to_csv(cat_path)
            saved_paths[slug] = cat_path
            
        logger.info(f"Saved {len(saved_paths)} processed datasets to {self.processed_dir}")
        return saved_paths

    def create_sequences(
        self,
        series_values: np.ndarray,
        train_ratio: float = 0.8
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, MinMaxScaler]:
        """
        Transforms 1D time-series count data into scaled sliding window sequences for LSTM:
        X: shape (n_samples, sequence_length, 1)
        y: shape (n_samples, 1)
        Splits chronologically into train and test sets to prevent time leakage.
        """
        if len(series_values.shape) == 1:
            series_values = series_values.reshape(-1, 1)

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(series_values)

        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i : i + self.sequence_length])
            y.append(scaled_data[i + self.sequence_length])

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)

        split_idx = int(len(X) * train_ratio)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        return X_train, y_train, X_test, y_test, scaler

    def save_scaler(self, scaler: MinMaxScaler, threat_type: str) -> str:
        """Persists fitted MinMaxScaler to disk using joblib."""
        slug = get_threat_slug(threat_type)
        scaler_filename = f"{slug}_scaler.joblib"
        scaler_path = os.path.join(self.models_dir, scaler_filename)
        joblib.dump(scaler, scaler_path)
        return scaler_path

    def load_scaler(self, threat_type: str) -> MinMaxScaler:
        """Loads fitted MinMaxScaler from disk."""
        slug = get_threat_slug(threat_type)
        scaler_filename = f"{slug}_scaler.joblib"
        scaler_path = os.path.join(self.models_dir, scaler_filename)
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found for {threat_type} at {scaler_path}")
        return joblib.load(scaler_path)
