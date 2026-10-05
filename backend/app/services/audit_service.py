import re
from datetime import datetime
from typing import Optional, Dict, Any, Union
from fastapi import Request

from backend.app.database import get_database
from backend.app.utils.logging import logger

SENSITIVE_KEYS = {"password", "password_hash", "token", "access_token", "secret", "authorization", "jwt"}

def sanitize_details(details: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively sanitize sensitive fields like passwords, hashes, and tokens."""
    if not details or not isinstance(details, dict):
        return details
    
    sanitized = {}
    for key, value in details.items():
        if any(s in key.lower() for s in SENSITIVE_KEYS):
            continue
        if isinstance(value, dict):
            sanitized[key] = sanitize_details(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_details(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized

def extract_client_info(request: Optional[Request] = None) -> tuple[str, str]:
    """Extract client IP address and user-agent string safely from Request."""
    if not request:
        return ("127.0.0.1", "Internal / Automated Service")
    
    # 1. IP extraction with reverse proxy headers fallback
    ip = "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    elif request.headers.get("x-real-ip"):
        ip = request.headers.get("x-real-ip").strip()
    elif request.client and request.client.host:
        ip = request.client.host

    # 2. User-Agent extraction
    ua = request.headers.get("user-agent", "Unknown Device")
    return (ip, ua)

async def log_audit_event(
    action: str,
    user: Optional[Dict[str, Any]] = None,
    email: Optional[str] = None,
    user_name: Optional[str] = None,
    role: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Centralized SOC Audit Service.
    Writes a structured audit record into the MongoDB audit_logs collection.
    Never exposes passwords, tokens, or private secrets.
    """
    try:
        # Extract IP and User-Agent if not explicitly passed
        req_ip, req_ua = extract_client_info(request)
        final_ip = ip_address or req_ip
        final_ua = user_agent or req_ua

        # Extract user attributes safely
        user_id = None
        if user:
            user_id = str(user.get("_id") or user.get("id") or "")
            email = email or user.get("email")
            user_name = user_name or user.get("name")
            role = role or user.get("role")

        audit_doc = {
            "user_id": user_id,
            "user_name": user_name or "Anonymous / System",
            "email": email.lower().strip() if email else None,
            "role": role or "viewer",
            "action": action.strip().upper(),
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id is not None else None,
            "timestamp": datetime.utcnow(),
            "status": status.lower(),
            "ip_address": final_ip,
            "user_agent": final_ua,
            "details": sanitize_details(details) or {}
        }

        db = get_database()
        res = await db.audit_logs.insert_one(audit_doc)
        audit_doc["id"] = str(res.inserted_id)
        audit_doc.pop("_id", None)
        return audit_doc

    except Exception as e:
        logger.error(f"Audit log recording error: {str(e)}", exc_info=True)
        return None
