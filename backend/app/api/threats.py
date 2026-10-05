from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status, Depends, Request

from backend.app.config import settings
from backend.app.database import get_database
from backend.app.models.schemas import ThreatEventCreate, ThreatSummaryResponse
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.security import get_optional_current_user
from backend.app.utils.validation import validate_threat_type
from backend.app.utils.logging import logger


router = APIRouter()

ALLOWED_SEVERITIES = ["Low", "Medium", "High", "Critical"]

@router.get(
    "",
    summary="List threat events with filtering and pagination"
)
async def list_threat_events(
    threat_type: Optional[str] = Query(None, description="Filter by threat category"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    start_date: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter up to end date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=1000, description="Page size limit"),
    skip: int = Query(0, ge=0, description="Number of records to skip")
):
    db = get_database()
    query: Dict[str, Any] = {}

    if threat_type:
        query["threat_type"] = threat_type
    if severity:
        query["severity"] = severity
        
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date
    if date_filter:
        query["date"] = date_filter

    total_count = await db.threat_events.count_documents(query)
    
    cursor = db.threat_events.find(query).sort("date", -1).skip(skip).limit(limit)
    events = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        events.append(doc)

    return {
        "total": total_count,
        "limit": limit,
        "skip": skip,
        "count": len(events),
        "data": events
    }

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Record a single new threat event"
)
async def create_threat_event(event: ThreatEventCreate):
    db = get_database()
    
    # 1. Validate threat type
    if not validate_threat_type(event.threat_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported threat category '{event.threat_type}'. Must be one of: {settings.SUPPORTED_THREAT_TYPES}"
        )
        
    # 2. Validate severity
    if event.severity not in ALLOWED_SEVERITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity '{event.severity}'. Allowed: {ALLOWED_SEVERITIES}"
        )
        
    # 3. Validate date format
    try:
        datetime.strptime(event.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected YYYY-MM-DD."
        )
        
    # 4. Validate count
    if event.count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be at least 1."
        )

    doc = {
        "date": event.date,
        "threat_type": event.threat_type,
        "severity": event.severity,
        "source": event.source or "Manual Entry",
        "location": event.location or "Global",
        "count": event.count,
        "description": event.description or f"{event.threat_type} incident reported - Severity {event.severity}",
        "created_at": datetime.utcnow()
    }
    
    result = await db.threat_events.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    
    logger.info(f"Ingested single threat event: {doc['threat_type']} ({doc['severity']}) on {doc['date']}")
    return doc

@router.get(
    "/summary",
    response_model=ThreatSummaryResponse,
    summary="Retrieve high-level summary of historical threat incidents"
)
async def get_threats_summary():
    db = get_database()
    
    total_docs = await db.threat_events.count_documents({})
    if total_docs == 0:
        return {
            "total_events": 0,
            "threat_counts": {},
            "severity_distribution": {},
            "most_frequent_threat": None,
            "highest_severity_threat": None,
            "date_range": {"start": None, "end": None},
            "category_count": 0
        }

    # Aggregate total threat counts by category
    type_pipeline = [
        {"$group": {"_id": "$threat_type", "total_count": {"$sum": "$count"}}}
    ]
    type_agg = await db.threat_events.aggregate(type_pipeline).to_list(length=100)
    threat_counts = {item["_id"]: item["total_count"] for item in type_agg if item["_id"]}

    # Aggregate severity distribution
    sev_pipeline = [
        {"$group": {"_id": "$severity", "total_count": {"$sum": "$count"}}}
    ]
    sev_agg = await db.threat_events.aggregate(sev_pipeline).to_list(length=100)
    sev_counts = {item["_id"]: item["total_count"] for item in sev_agg if item["_id"]}

    # Most frequent threat category
    most_frequent = max(threat_counts.items(), key=lambda x: x[1])[0] if threat_counts else None

    # Threat category with highest critical + high severity volume
    crit_pipeline = [
        {"$match": {"severity": {"$in": ["Critical", "High"]}}},
        {"$group": {"_id": "$threat_type", "severe_count": {"$sum": "$count"}}},
        {"$sort": {"severe_count": -1}},
        {"$limit": 1}
    ]
    crit_agg = await db.threat_events.aggregate(crit_pipeline).to_list(length=1)
    highest_sev_threat = crit_agg[0]["_id"] if crit_agg else most_frequent

    # Min and max dates
    date_pipeline = [
        {"$group": {"_id": None, "min_date": {"$min": "$date"}, "max_date": {"$max": "$date"}}}
    ]
    date_agg = await db.threat_events.aggregate(date_pipeline).to_list(length=1)
    date_range = {
        "start": date_agg[0]["min_date"] if date_agg else None,
        "end": date_agg[0]["max_date"] if date_agg else None
    }

    return {
        "total_events": sum(threat_counts.values()),
        "threat_counts": threat_counts,
        "severity_distribution": sev_counts,
        "most_frequent_threat": most_frequent,
        "highest_severity_threat": highest_sev_threat,
        "date_range": date_range,
        "category_count": len(threat_counts)
    }

@router.get(
    "/categories",
    summary="Get supported threat categories and severities"
)
async def get_categories():
    return {
        "supported_threat_types": settings.SUPPORTED_THREAT_TYPES,
        "allowed_severities": ALLOWED_SEVERITIES,
        "default_horizons": settings.DEFAULT_FORECAST_HORIZONS
    }
