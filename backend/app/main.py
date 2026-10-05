from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
import time

from backend.app.config import settings
from backend.app.database import connect_to_mongo, close_mongo_connection, db_manager
from backend.app.utils.logging import logger

# Ensure Starlette / FastAPI compatibility so every route object exposes .path
import fastapi.routing
if hasattr(fastapi.routing, "_IncludedRouter"):
    fastapi.routing._IncludedRouter.path = property(lambda self: getattr(self, "prefix", ""))

@asynccontextmanager

async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB and create indexes
    logger.info("Starting up Cyber Threat Forecasting System Backend...")
    await connect_to_mongo()
    yield
    # Shutdown: Close database pool
    logger.info("Shutting down Cyber Threat Forecasting System Backend...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade cybersecurity analytics and deep learning (LSTM) forecasting API.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} -> Status {response.status_code} ({duration:.3f}s)")
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An internal server error occurred.",
            "detail": str(exc) if "test" in settings.PROJECT_NAME.lower() else "Please contact SOC administrator."
        }
    )

# Root / Health Endpoints
@app.get("/", tags=["Health"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/api/docs"
    }

@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(url="/api/docs")

@app.get("/redoc", include_in_schema=False)
async def redirect_redoc():
    return RedirectResponse(url="/api/redoc")

@app.get("/api/health", tags=["Health"])
async def health_check():
    mongo_status = "connected" if db_manager.db is not None else "disconnected"
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": mongo_status,
        "version": settings.VERSION
    }

# Register Feature Routers
from backend.app.api import (
    auth_router,
    threats_router,
    forecast_router,
    datasets_router,
    analytics_router,
    admin_router,
    reports_router
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(threats_router, prefix=f"{settings.API_V1_STR}/threats", tags=["Threat Events"])
app.include_router(forecast_router, prefix=f"{settings.API_V1_STR}/forecast", tags=["Forecasting"])
app.include_router(datasets_router, prefix=f"{settings.API_V1_STR}/datasets", tags=["Datasets"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics & SOC"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Management & Audit"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports & History"])

