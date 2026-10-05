from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query, Request, Depends

from backend.app.config import settings
from backend.app.database import get_database
from backend.app.models.schemas import (
    ForecastRequest,
    ForecastResponse,
    ForecastPoint,
    HistoricalPoint
)
from backend.app.services.forecast_service import forecast_service
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.security import get_optional_current_user
from backend.app.utils.validation import validate_threat_type, validate_forecast_horizon
from backend.app.utils.logging import logger


router = APIRouter()

@router.post(
    "",
    response_model=ForecastResponse,
    summary="Generate deep learning LSTM threat forecast"
)
async def create_forecast(
    request: ForecastRequest,
    req: Request,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    # 1. Validate threat category
    if not validate_threat_type(request.threat_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported threat category '{request.threat_type}'. Must be one of: {settings.SUPPORTED_THREAT_TYPES}"
        )
        
    # 2. Validate forecast horizon
    if not validate_forecast_horizon(request.forecast_days):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid forecast horizon '{request.forecast_days}'. Allowed range is 1 to 90 days (e.g. 7, 14, 30)."
        )

    try:
        result = forecast_service.get_forecast(
            threat_type=request.threat_type,
            forecast_days=request.forecast_days
        )
        
        # Persist forecast points to MongoDB for caching and historical audit
        db = get_database()
        forecast_docs = []
        for pt in result["forecast_data"]:
            forecast_docs.append({
                "threat_type": request.threat_type,
                "forecast_date": pt["date"],
                "predicted_count": pt["predicted_count"],
                "lower_bound": pt["lower_bound"],
                "upper_bound": pt["upper_bound"],
                "horizon_days": request.forecast_days,
                "model_version": result["model_version"],
                "created_at": datetime.utcnow()
            })
            
        if forecast_docs:
            await db.forecasts.delete_many({
                "threat_type": request.threat_type,
                "horizon_days": request.forecast_days
            })
            await db.forecasts.insert_many(forecast_docs)
            
        # Feature 13: Audit Trail for Forecast Generation
        await log_audit_event(
            action="FORECAST_GENERATED",
            user=current_user,
            resource_type="forecast",
            resource_id=request.threat_type,
            status="success",
            details={
                "threat_type": request.threat_type,
                "forecast_days": request.forecast_days,
                "risk_score": result.get("summary_stats", {}).get("risk_score"),
                "risk_level": result.get("risk_level"),
                "trend_direction": result.get("trend_direction"),
                "peak_forecast_count": result.get("summary_stats", {}).get("peak_forecast_count")
            },
            request=req
        )

        logger.info(f"Forecast generated for {request.threat_type} ({request.forecast_days} days).")
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Model artifacts not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model artifacts not found for {request.threat_type}. Please run training pipeline first."
        )
    except Exception as e:
        logger.error(f"Forecasting error for {request.threat_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute forecast: {str(e)}"
        )

@router.get(
    "/models/status",
    summary="List all 8 threat LSTM model statuses and evaluation metrics"
)
async def get_models_status():
    """Returns deployment status, disk existence, and test metrics for all models."""
    return {
        "count": len(settings.SUPPORTED_THREAT_TYPES),
        "models": forecast_service.get_all_models_status()
    }

@router.get(
    "/{threat_type}",
    response_model=ForecastResponse,
    summary="Get forecast for a specific threat category by path"
)
async def get_forecast_by_category(
    threat_type: str,
    req: Request,
    days: int = Query(30, ge=1, le=90, description="Forecast horizon in days (7, 14, 30)"),
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    request_data = ForecastRequest(threat_type=threat_type, forecast_days=days)
    return await create_forecast(request_data, req=req, current_user=current_user)

