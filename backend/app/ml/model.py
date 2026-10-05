import os
from typing import Optional
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber

from backend.app.config import settings
from backend.app.utils.logging import logger
from backend.app.ml.preprocessor import get_threat_slug

def build_lstm_model(
    sequence_length: int = settings.DEFAULT_SEQUENCE_LENGTH,
    n_features: int = 1,
    learning_rate: float = 0.003,
    dropout_rate: float = 0.2
) -> Sequential:
    """
    Constructs a 2-layer stacked LSTM network tailored for cyber threat time-series forecasting.
    Includes dropout regularization to prevent overfitting on bursty attack patterns.
    """
    model = Sequential([
        Input(shape=(sequence_length, n_features), name="threat_time_series_input"),
        LSTM(units=64, return_sequences=True, name="lstm_layer_1"),
        Dropout(rate=dropout_rate, name="dropout_1"),
        LSTM(units=32, return_sequences=False, name="lstm_layer_2"),
        Dropout(rate=dropout_rate, name="dropout_2"),
        Dense(units=16, activation="relu", name="dense_hidden"),
        Dense(units=1, activation="linear", name="threat_count_output")
    ], name="CyberThreatLSTMForecaster")

    # Huber loss provides smooth transitions between L2 (small errors) and L1 (large bursts)
    optimizer = Adam(learning_rate=learning_rate)
    loss = Huber(delta=1.0)
    
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=["mae"]
    )
    return model

def get_model_path(threat_type: str, models_dir: Optional[str] = None) -> str:
    """Returns canonical model filepath for a threat type."""
    m_dir = models_dir or settings.MODELS_PATH
    slug = get_threat_slug(threat_type)
    return os.path.join(m_dir, f"{slug}_lstm.keras")

def save_lstm_model(model: Sequential, threat_type: str, models_dir: Optional[str] = None) -> str:
    """Saves trained Keras LSTM model to disk."""
    filepath = get_model_path(threat_type, models_dir)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    model.save(filepath)
    logger.info(f"Saved LSTM model for '{threat_type}' to: {filepath}")
    return filepath

def load_lstm_model(threat_type: str, models_dir: Optional[str] = None) -> Sequential:
    """Loads saved Keras LSTM model from disk."""
    filepath = get_model_path(threat_type, models_dir)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file for '{threat_type}' not found at: {filepath}")
    model = load_model(filepath)
    return model
