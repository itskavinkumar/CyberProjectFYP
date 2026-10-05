# API router package
from backend.app.api.auth import router as auth_router
from backend.app.api.threats import router as threats_router
from backend.app.api.forecast import router as forecast_router
from backend.app.api.datasets import router as datasets_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.admin import router as admin_router
from backend.app.api.reports import router as reports_router

__all__ = [
    "auth_router",
    "threats_router",
    "forecast_router",
    "datasets_router",
    "analytics_router",
    "admin_router",
    "reports_router"
]
