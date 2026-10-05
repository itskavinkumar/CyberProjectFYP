from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: EmailStr
    password_hash: str
    role: str = "analyst"  # "analyst", "admin", "viewer"
    status: str = "active"  # "active", "disabled"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_logout_at: Optional[datetime] = None
    login_count: int = 0
    failed_login_count: int = 0

    class Config:
        populate_by_name = True

class AuditLogModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    action: str  # e.g., LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, REGISTER, ROLE_CHANGED, etc.
    resource_type: Optional[str] = None  # user, threat, forecast, dataset, report, auth
    resource_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "success"  # success, failed, warning
    ip_address: Optional[str] = "127.0.0.1"
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

class ReportModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    report_id: str
    title: str
    report_type: str  # threat_forecast, risk_assessment, threat_trends, model_performance, dataset_summary, user_activity, audit_trail
    generated_by: str
    generated_by_role: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parameters: Optional[Dict[str, Any]] = None
    summary_data: Optional[Dict[str, Any]] = None
    status: str = "completed"

    class Config:
        populate_by_name = True


class ThreatEventModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    date: str  # Format: "YYYY-MM-DD"
    threat_type: str  # Phishing, Malware, etc.
    severity: str  # Low, Medium, High, Critical
    source: str = "Firewall-IDS"
    location: str = "Global"
    count: int = 1
    description: Optional[str] = None
    dataset_id: Optional[str] = None

    class Config:
        populate_by_name = True

class ForecastModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    threat_type: str
    forecast_date: str  # Format: "YYYY-MM-DD"
    predicted_count: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    horizon_days: int = 30
    model_version: str = "v1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class DatasetModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    number_of_records: int
    date_range: Dict[str, Optional[str]]
    threat_types: List[str]
    processing_status: str = "processed"  # "pending", "processed", "failed"
    validation_report: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

class ModelMetadataModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    threat_type: str
    model_name: str
    model_version: str = "v1.0.0"
    training_date: datetime = Field(default_factory=datetime.utcnow)
    training_records: int
    sequence_length: int = 30
    architecture: str
    mae: float
    rmse: float
    mape: float
    status: str = "active"

    class Config:
        populate_by_name = True
