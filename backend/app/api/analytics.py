from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter

from backend.app.config import settings
from backend.app.database import get_database
import time
from backend.app.models.schemas import AnalyticsOverviewResponse, RiskIndicator
from backend.app.services.forecast_service import forecast_service

router = APIRouter()

_risk_cache = {
    "timestamp": 0,
    "data": None,
    "overall_trend": "Increasing"
}


CONTRIBUTING_FACTORS = {
    "Phishing": ["Credential harvesting surges", "Employee email spoofing", "Seasonal quarter blitzes"],
    "Malware": ["Trojan loader payloads", "EDR signature triggers", "Command & Control beaconing"],
    "Brute Force": ["Credential stuffing scans", "RDP/VPN endpoint probing", "Weekend automated bot traffic"],
    "DDoS": ["Volumetric UDP amplification", "Botnet reflection floods", "Edge infrastructure saturation"],
    "Botnet": ["Zombie network expansion", "Automated IoT scanning", "Coordinated DDoS priming"],
    "SQL Injection": ["Public API perimeter probes", "Automated SQLmap scans", "Database error leakage"],
    "Ransomware": ["Double-extortion tactics", "Shadow copy deletion", "Rapid lateral movement"],
    "Data Breach": ["High-volume exfiltration anomalies", "Privileged credential abuse", "DLP violation alerts"]
}

@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Comprehensive cybersecurity operations center (SOC) analytics overview"
)
async def get_analytics_overview():
    db = get_database()

    # 1. Total events and threat breakdown
    type_pipeline = [
        {"$group": {"_id": "$threat_type", "total": {"$sum": "$count"}}},
        {"$sort": {"total": -1}}
    ]
    type_results = await db.threat_events.aggregate(type_pipeline).to_list(length=100)
    
    total_events = sum(item["total"] for item in type_results)
    threat_distribution = [
        {"threat_type": item["_id"], "count": item["total"], "percentage": round((item["total"] / max(total_events, 1)) * 100, 2)}
        for item in type_results if item["_id"]
    ]

    most_frequent = type_results[0]["_id"] if type_results else "None"

    # 2. Severity distribution
    sev_pipeline = [
        {"$group": {"_id": "$severity", "total": {"$sum": "$count"}}},
        {"$sort": {"total": -1}}
    ]
    sev_results = await db.threat_events.aggregate(sev_pipeline).to_list(length=100)
    severity_distribution = [
        {"severity": item["_id"], "count": item["total"], "percentage": round((item["total"] / max(total_events, 1)) * 100, 2)}
        for item in sev_results if item["_id"]
    ]

    # 3. Highest severity category (most Critical + High)
    crit_pipeline = [
        {"$match": {"severity": {"$in": ["Critical", "High"]}}},
        {"$group": {"_id": "$threat_type", "count": {"$sum": "$count"}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    crit_res = await db.threat_events.aggregate(crit_pipeline).to_list(length=1)
    highest_severity_threat = crit_res[0]["_id"] if crit_res else most_frequent

    # 4. Daily trend timeline (last 90 days of recorded events)
    daily_pipeline = [
        {"$group": {"_id": "$date", "total_threats": {"$sum": "$count"}}},
        {"$sort": {"_id": 1}}
    ]
    daily_res = await db.threat_events.aggregate(daily_pipeline).to_list(length=1000)
    daily_trend = [
        {"date": item["_id"], "count": item["total_threats"]}
        for item in daily_res if item["_id"]
    ]

    total_days = max(len(daily_trend), 1)
    avg_threats_per_day = round(float(total_events / total_days), 2)

    # 5. Risk Indicators for each supported threat category (with in-memory cache)
    global _risk_cache
    now = time.time()
    
    if _risk_cache["data"] and (now - _risk_cache["timestamp"] < 300):
        risk_indicators = _risk_cache["data"]
        overall_trend = _risk_cache["overall_trend"]
    else:
        risk_indicators = []
        trend_counts = {"Increasing": 0, "Decreasing": 0, "Stable": 0}

        for threat_type in settings.SUPPORTED_THREAT_TYPES:
            try:
                # Query recent forecast
                fc = forecast_service.get_forecast(threat_type, forecast_days=14)
                r_level = fc["risk_level"]
                r_score = fc["summary_stats"]["risk_score"]
                trend = fc["trend_direction"]
                avg_daily = fc["summary_stats"]["avg_historical_count"]
                chg_pct = fc["summary_stats"]["predicted_change_pct"]
            except Exception:
                # Fallback if model not ready
                r_level = "Medium"
                r_score = 50.0
                trend = "Stable"
                avg_daily = 50.0
                chg_pct = 0.0

            trend_counts[trend] = trend_counts.get(trend, 0) + 1
            factors = CONTRIBUTING_FACTORS.get(threat_type, ["Anomalous activity observed"])

            risk_indicators.append(RiskIndicator(
                threat_type=threat_type,
                risk_level=r_level,
                risk_score=r_score,
                recent_trend=trend,
                avg_daily_count=round(avg_daily, 2),
                forecasted_change_pct=round(chg_pct, 2),
                contributing_factors=factors
            ))

        overall_trend = max(trend_counts.items(), key=lambda x: x[1])[0]
        _risk_cache["timestamp"] = now
        _risk_cache["data"] = risk_indicators
        _risk_cache["overall_trend"] = overall_trend


    return AnalyticsOverviewResponse(
        total_threat_events=total_events,
        most_frequent_threat=most_frequent,
        highest_severity_threat=highest_severity_threat,
        threat_categories_count=len(type_results),
        avg_threats_per_day=avg_threats_per_day,
        overall_trend_direction=overall_trend,
        threat_distribution=threat_distribution,
        severity_distribution=severity_distribution,
        daily_trend=daily_trend[-60:],  # Provide last 60 days for smooth charting
        risk_indicators=risk_indicators
    )

@router.get(
    "/risk-matrix",
    summary="SOC Threat Prioritization and Risk Matrix"
)
async def get_risk_matrix():
    overview = await get_analytics_overview()
    matrix = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": []
    }
    for ind in overview.risk_indicators:
        matrix[ind.risk_level].append({
            "threat_type": ind.threat_type,
            "risk_score": ind.risk_score,
            "trend": ind.recent_trend,
            "change_pct": ind.forecasted_change_pct
        })
    return matrix
