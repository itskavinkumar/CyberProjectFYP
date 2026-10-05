import io
import csv
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from bson import ObjectId

from backend.app.database import get_database
from backend.app.config import settings
from backend.app.models.schemas import (
    ReportGenerateRequest,
    ReportResponse,
    ReportListResponse
)
from backend.app.utils.security import (
    get_current_active_user,
    require_role
)
from backend.app.services.forecast_service import forecast_service
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.logging import logger

router = APIRouter()

ADMIN_ONLY_REPORTS = {"user_activity", "audit_trail"}
ANALYST_ALLOWED_REPORTS = {
    "threat_forecast",
    "risk_assessment",
    "threat_trends",
    "model_performance",
    "dataset_summary"
}
VIEWER_ALLOWED_REPORTS = {
    "threat_forecast",
    "risk_assessment",
    "threat_trends",
    "model_performance"
}

def _serialize_report(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc_copy = dict(doc)
    if "_id" in doc_copy:
        doc_copy["id"] = str(doc_copy.pop("_id"))
    return doc_copy

@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an operational or administrative SOC report"
)
async def generate_report(
    body: ReportGenerateRequest,
    req: Request,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    report_type = body.report_type.lower().strip()
    user_role = (current_user.get("role") or "viewer").lower().strip()

    # Feature 28: Role-based Report Access Control
    if report_type in ADMIN_ONLY_REPORTS and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: '{report_type}' report generation requires administrative privileges."
        )

    if user_role == "viewer" and report_type not in VIEWER_ALLOWED_REPORTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Viewers cannot generate '{report_type}' reports."
        )

    now = datetime.utcnow()
    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    params = body.parameters or {}
    summary_data: Dict[str, Any] = {}
    default_title = f"{report_type.replace('_', ' ').title()} Report"

    try:
        if report_type == "threat_forecast":
            threat_type = params.get("threat_type", "Phishing")
            days = int(params.get("forecast_days", 30))
            fc = forecast_service.get_forecast(threat_type, forecast_days=days)
            summary_data = {
                "threat_type": threat_type,
                "forecast_days": days,
                "risk_level": fc.get("risk_level"),
                "risk_score": fc.get("summary_stats", {}).get("risk_score"),
                "trend_direction": fc.get("trend_direction"),
                "peak_forecast_count": fc.get("summary_stats", {}).get("peak_forecast_count"),
                "avg_forecast_count": fc.get("summary_stats", {}).get("avg_forecast_count"),
                "model_version": fc.get("model_version"),
                "evaluation_metrics": fc.get("evaluation_metrics", {})
            }
            default_title = f"{threat_type} {days}-Day AI Forecast Report"

        elif report_type == "risk_assessment":
            indicators = []
            for t in settings.SUPPORTED_THREAT_TYPES:
                try:
                    f = forecast_service.get_forecast(t, forecast_days=14)
                    indicators.append({
                        "threat_type": t,
                        "risk_level": f.get("risk_level", "Medium"),
                        "risk_score": f.get("summary_stats", {}).get("risk_score", 50.0),
                        "trend": f.get("trend_direction", "Stable")
                    })
                except Exception:
                    indicators.append({"threat_type": t, "risk_level": "Medium", "risk_score": 50.0, "trend": "Stable"})
            
            critical_count = sum(1 for i in indicators if i["risk_level"] == "Critical")
            high_count = sum(1 for i in indicators if i["risk_level"] == "High")
            summary_data = {
                "total_threats_evaluated": len(indicators),
                "critical_threats_count": critical_count,
                "high_threats_count": high_count,
                "indicators": indicators
            }
            default_title = "SOC Comprehensive Threat Risk Assessment"

        elif report_type == "threat_trends":
            total_events = await db.threat_events.count_documents({})
            pipeline = [
                {"$group": {"_id": "$threat_type", "count": {"$sum": "$count"}}},
                {"$sort": {"count": -1}}
            ]
            agg = await db.threat_events.aggregate(pipeline).to_list(100)
            summary_data = {
                "total_recorded_events": total_events,
                "breakdown": [{"threat_type": item["_id"], "count": item["count"]} for item in agg if item["_id"]]
            }
            default_title = "Historical Threat Trend Analysis Report"

        elif report_type == "model_performance":
            models_info = forecast_service.get_all_models_status()
            summary_data = {
                "total_models": len(models_info),
                "models": models_info
            }
            default_title = "LSTM Deep Learning Model Performance Audit"

        elif report_type == "dataset_summary":
            cursor = db.datasets.find({}).sort("upload_date", -1)
            datasets = [_serialize_report(d) async for d in cursor]
            summary_data = {
                "total_datasets": len(datasets),
                "datasets": datasets
            }
            default_title = "SOC Dataset Ingestion & Validation Summary"

        elif report_type == "user_activity":
            # Admin only
            total_users = await db.users.count_documents({})
            active_users = await db.users.count_documents({"status": "active"})
            disabled_users = await db.users.count_documents({"status": "disabled"})
            total_logins = await db.audit_logs.count_documents({"action": "LOGIN_SUCCESS"})
            failed_logins = await db.audit_logs.count_documents({"action": "LOGIN_FAILED"})
            
            # Roles count
            roles_pipeline = [{"$group": {"_id": "$role", "count": {"$sum": 1}}}]
            role_counts = {item["_id"]: item["count"] for item in await db.users.aggregate(roles_pipeline).to_list(10)}

            summary_data = {
                "total_registered_users": total_users,
                "active_accounts": active_users,
                "disabled_accounts": disabled_users,
                "role_distribution": role_counts,
                "successful_logins": total_logins,
                "failed_login_attempts": failed_logins
            }
            default_title = "SOC Personnel Activity & Access Governance Report"

        elif report_type == "audit_trail":
            # Admin only
            total_audits = await db.audit_logs.count_documents({})
            action_pipeline = [
                {"$group": {"_id": "$action", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            action_counts = {item["_id"]: item["count"] for item in await db.audit_logs.aggregate(action_pipeline).to_list(50)}
            security_failures = await db.audit_logs.count_documents({"status": "failed"})

            summary_data = {
                "total_audit_events": total_audits,
                "security_failures": security_failures,
                "action_distribution": action_counts
            }
            default_title = "SOC Comprehensive Security Audit Trail Report"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported report type: '{report_type}'"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error compiling report '{report_type}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

    report_title = body.title.strip() if body.title else default_title
    report_doc = {
        "report_id": report_id,
        "title": report_title,
        "report_type": report_type,
        "generated_by": current_user["email"],
        "generated_by_role": user_role,
        "timestamp": now,
        "parameters": params,
        "summary_data": summary_data,
        "status": "completed"
    }

    res = await db.reports.insert_one(report_doc)
    report_doc["id"] = str(res.inserted_id)
    report_doc.pop("_id", None)

    # Feature 14 Audit Logging
    await log_audit_event(
        action="REPORT_GENERATED",
        user=current_user,
        resource_type="report",
        resource_id=report_id,
        status="success",
        details={
            "report_id": report_id,
            "report_type": report_type,
            "title": report_title
        },
        request=req
    )

    logger.info(f"Report generated: {report_id} ({report_type}) by {current_user['email']}")
    return report_doc

@router.get(
    "",
    response_model=ReportListResponse,
    summary="List generated reports with role-based access filtering"
)
async def list_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    user_role = (current_user.get("role") or "viewer").lower().strip()
    query: Dict[str, Any] = {}

    if report_type and report_type.lower() != "all":
        query["report_type"] = report_type.lower().strip()

    # Feature 28: Non-admins cannot see admin-only reports
    if user_role != "admin":
        query["report_type"] = {"$nin": list(ADMIN_ONLY_REPORTS)}
        if report_type in ADMIN_ONLY_REPORTS:
            return {"total": 0, "reports": []}

    cursor = db.reports.find(query).sort("timestamp", -1)
    reports = [_serialize_report(d) async for d in cursor]
    return {
        "total": len(reports),
        "reports": reports
    }

@router.get(
    "/{report_identifier}",
    response_model=ReportResponse,
    summary="Retrieve report details by report_id or MongoDB ID"
)
async def get_report_details(
    report_identifier: str,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    query = {"$or": [{"report_id": report_identifier}]}
    if ObjectId.is_valid(report_identifier):
        query["$or"].append({"_id": ObjectId(report_identifier)})

    report = await db.reports.find_one(query)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_identifier}' not found."
        )

    user_role = (current_user.get("role") or "viewer").lower().strip()
    if report.get("report_type") in ADMIN_ONLY_REPORTS and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Administrative privileges required to view this report."
        )

    return _serialize_report(report)

@router.get(
    "/{report_identifier}/export",
    summary="Export generated report data as CSV or JSON"
)
async def export_report(
    report_identifier: str,
    export_format: str = Query("csv", alias="format", description="Export format: 'csv' or 'json'"),
    current_user: dict = Depends(get_current_active_user)
):
    report = await get_report_details(report_identifier, current_user)
    
    if export_format.lower() == "json":
        json_str = json.dumps(report, default=str, indent=2)
        return StreamingResponse(
            io.BytesIO(json_str.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={report['report_id']}.json"}
        )

    # Flatten report data into CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Report ID", report["report_id"]])
    writer.writerow(["Title", report["title"]])
    writer.writerow(["Report Type", report["report_type"]])
    writer.writerow(["Generated By", report["generated_by"]])
    writer.writerow(["Generated By Role", report["generated_by_role"]])
    writer.writerow(["Timestamp", str(report["timestamp"])])
    writer.writerow([])
    writer.writerow(["--- SUMMARY METRICS ---"])

    summary = report.get("summary_data", {})
    if isinstance(summary, dict):
        for k, v in summary.items():
            if isinstance(v, (dict, list)):
                writer.writerow([k, json.dumps(v, default=str)])
            else:
                writer.writerow([k, v])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report['report_id']}.csv"}
    )
