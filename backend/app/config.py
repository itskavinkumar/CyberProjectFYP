import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cyber Threat Forecasting System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "cyber_threat_forecast"
    
    # Security
    JWT_SECRET: str = "cyber_forecast_super_secret_jwt_key_academic_fyp_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # ML & File Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA_PATH: str = os.path.join(BASE_DIR, "data", "raw")
    PROCESSED_DATA_PATH: str = os.path.join(BASE_DIR, "data", "processed")
    MODELS_PATH: str = os.path.join(BASE_DIR, "models", "lstm")
    
    # ML Hyperparameters
    DEFAULT_SEQUENCE_LENGTH: int = 30
    DEFAULT_FORECAST_HORIZONS: List[int] = [7, 14, 30]
    SUPPORTED_THREAT_TYPES: List[str] = [
        "Phishing",
        "Malware",
        "Brute Force",
        "DDoS",
        "Botnet",
        "SQL Injection",
        "Ransomware",
        "Data Breach"
    ]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
