from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

# Authentication Schemas
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "analyst"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: Optional[str] = "active"
    is_active: Optional[bool] = True
    created_at: Optional[Any] = None
    last_login_at: Optional[Any] = None
    login_count: Optional[int] = 0

# Admin & User Management Schemas
class AdminUserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("analyst", description="Role to assign: admin, analyst, viewer")
    status: Optional[str] = Field("active", description="Account status: active or disabled")

class AdminUserRoleUpdateRequest(BaseModel):
    role: str = Field(..., description="Target role: admin, analyst, viewer")

class AdminUserStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Target status: active or disabled")

class AdminUserItemResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str = "active"
    is_active: bool = True
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    last_login_at: Optional[Any] = None
    last_logout_at: Optional[Any] = None
    login_count: int = 0
    failed_login_count: int = 0

class AdminUserListResponse(BaseModel):
    total: int
    page: int
    limit: int
    users: List[AdminUserItemResponse]

class AdminUserDetailResponse(BaseModel):
    user: AdminUserItemResponse
    recent_activity: List[Dict[str, Any]]

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    timestamp: Any
    status: str = "success"
    ip_address: Optional[str] = "127.0.0.1"
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AuditLogListResponse(BaseModel):
    total: int
    page: int
    limit: int
    logs: List[AuditLogResponse]

class LoginHistoryResponse(BaseModel):
    total: int
    page: int
    limit: int
    history: List[AuditLogResponse]

class AdminDashboardResponse(BaseModel):
    registered_users: int
    active_users: int
    disabled_users: int
    today_logins: int
    failed_logins: int
    today_forecasts: int
    total_datasets: int
    total_reports: int
    recent_logins: List[AuditLogResponse]
    recent_audits: List[AuditLogResponse]
    recent_datasets: List[Dict[str, Any]]
    recent_reports: List[Dict[str, Any]]

# Report Schemas
class ReportGenerateRequest(BaseModel):
    report_type: str = Field(..., description="Type of report: threat_forecast, risk_assessment, threat_trends, model_performance, dataset_summary, user_activity, audit_trail")
    title: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    id: str
    report_id: str
    title: str
    report_type: str
    generated_by: str
    generated_by_role: str
    timestamp: Any
    parameters: Optional[Dict[str, Any]] = None
    summary_data: Optional[Dict[str, Any]] = None
    status: str = "completed"

class ReportListResponse(BaseModel):
    total: int
    reports: List[ReportResponse]


# Threat Schemas
class ThreatEventCreate(BaseModel):
    date: str
    threat_type: str
    severity: str
    source: Optional[str] = "Manual Entry"
    location: Optional[str] = "Global"
    count: int = 1
    description: Optional[str] = None

class ThreatSummaryResponse(BaseModel):
    total_events: int
    threat_counts: Dict[str, int]
    severity_distribution: Dict[str, int]
    most_frequent_threat: Optional[str]
    highest_severity_threat: Optional[str]
    date_range: Dict[str, Optional[str]]
    category_count: int

# Forecast Schemas
class ForecastRequest(BaseModel):
    threat_type: str = Field(..., description="Threat category to forecast")
    forecast_days: int = Field(30, ge=1, le=90, description="Forecast horizon in days (7, 14, 30)")

class ForecastPoint(BaseModel):
    date: str
    predicted_count: float
    lower_bound: float
    upper_bound: float

class HistoricalPoint(BaseModel):
    date: str
    count: float

class ForecastResponse(BaseModel):
    threat_type: str
    forecast_days: int
    model_name: str
    model_version: str
    evaluation_metrics: Optional[Dict[str, float]] = None
    historical_data: List[HistoricalPoint]
    forecast_data: List[ForecastPoint]
    summary_stats: Dict[str, Any]
    risk_level: str
    trend_direction: str

# Dataset Schemas
class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    number_of_records: int
    date_range: Dict[str, Optional[str]]
    threat_types: List[str]
    is_valid: bool
    errors: List[str]
    summary: Dict[str, Any]

# Analytics Schemas
class RiskIndicator(BaseModel):
    threat_type: str
    risk_level: str  # Low, Medium, High, Critical
    risk_score: float  # 0 to 100
    recent_trend: str  # Increasing, Stable, Decreasing
    avg_daily_count: float
    forecasted_change_pct: float
    contributing_factors: List[str]

class AnalyticsOverviewResponse(BaseModel):
    total_threat_events: int
    most_frequent_threat: str
    highest_severity_threat: str
    threat_categories_count: int
    avg_threats_per_day: float
    overall_trend_direction: str
    threat_distribution: List[Dict[str, Any]]
    severity_distribution: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]
    risk_indicators: List[RiskIndicator]
