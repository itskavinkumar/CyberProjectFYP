from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from bson import ObjectId

from backend.app.database import get_database
from backend.app.models.schemas import (
    AdminUserCreateRequest,
    AdminUserRoleUpdateRequest,
    AdminUserStatusUpdateRequest,
    AdminUserItemResponse,
    AdminUserListResponse,
    AdminUserDetailResponse,
    AuditLogResponse,
    AuditLogListResponse,
    LoginHistoryResponse,
    AdminDashboardResponse
)
from backend.app.utils.security import (
    require_role,
    hash_password,
    get_current_active_user
)
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.logging import logger

router = APIRouter(dependencies=[Depends(require_role(["admin"]))])

def _serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB _id to string id."""
    if not doc:
        return doc
    doc_copy = dict(doc)
    if "_id" in doc_copy:
        doc_copy["id"] = str(doc_copy.pop("_id"))
    return doc_copy

def _build_user_query(user_identifier: str) -> Dict[str, Any]:
    """Build query matching either ObjectId or email string."""
    query = {"$or": [{"email": user_identifier.lower().strip()}]}
    if ObjectId.is_valid(user_identifier):
        query["$or"].append({"_id": ObjectId(user_identifier)})
    return query

# ============================================================================
# 1. Admin Security Dashboard (Feature 15)
# ============================================================================

@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    summary="Retrieve high-level SOC administration metrics and recent audit streams"
)
async def get_admin_dashboard():
    db = get_database()
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day)

    # User metrics
    registered_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"status": "active"})
    disabled_users = await db.users.count_documents({"status": "disabled"})

    # Today's activity metrics
    today_logins = await db.audit_logs.count_documents({
        "action": "LOGIN_SUCCESS",
        "timestamp": {"$gte": start_of_today}
    })
    failed_logins = await db.audit_logs.count_documents({
        "action": "LOGIN_FAILED",
        "timestamp": {"$gte": start_of_today}
    })
    today_forecasts = await db.audit_logs.count_documents({
        "action": "FORECAST_GENERATED",
        "timestamp": {"$gte": start_of_today}
    })
    total_datasets = await db.datasets.count_documents({})
    total_reports = await db.reports.count_documents({})

    # Recent login stream
    login_cursor = db.audit_logs.find({
        "action": {"$in": ["LOGIN_SUCCESS", "LOGIN_FAILED", "LOGOUT"]}
    }).sort("timestamp", -1).limit(6)
    recent_logins = [_serialize_mongo_doc(d) async for d in login_cursor]

    # Recent general audit stream
    audit_cursor = db.audit_logs.find({}).sort("timestamp", -1).limit(6)
    recent_audits = [_serialize_mongo_doc(d) async for d in audit_cursor]

    # Recent datasets
    dataset_cursor = db.datasets.find({}).sort("upload_date", -1).limit(5)
    recent_datasets = [_serialize_mongo_doc(d) async for d in dataset_cursor]

    # Recent reports
    report_cursor = db.reports.find({}).sort("timestamp", -1).limit(5)
    recent_reports = [_serialize_mongo_doc(d) async for d in report_cursor]

    return {
        "registered_users": registered_users,
        "active_users": active_users,
        "disabled_users": disabled_users,
        "today_logins": today_logins,
        "failed_logins": failed_logins,
        "today_forecasts": today_forecasts,
        "total_datasets": total_datasets,
        "total_reports": total_reports,
        "recent_logins": recent_logins,
        "recent_audits": recent_audits,
        "recent_datasets": recent_datasets,
        "recent_reports": recent_reports
    }

# ============================================================================
# 2. User Management APIs (Feature 1, Feature 8, Feature 9, Feature 10)
# ============================================================================

@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List all registered users with filtering, sorting, and pagination"
)
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role: admin, analyst, viewer"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, disabled"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: int = Query(-1, description="-1 for descending, 1 for ascending"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    db = get_database()
    query: Dict[str, Any] = {}

    if search:
        s = search.strip()
        query["$or"] = [
            {"name": {"$regex": s, "$options": "i"}},
            {"email": {"$regex": s, "$options": "i"}}
        ]
    if role and role.lower() != "all":
        query["role"] = role.lower().strip()
    if status_filter and status_filter.lower() != "all":
        query["status"] = status_filter.lower().strip()

    total = await db.users.count_documents(query)
    skip = (page - 1) * limit

    sort_field = sort_by if sort_by in ["created_at", "last_login_at", "name", "role", "status", "login_count"] else "created_at"
    cursor = db.users.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)

    users = []
    async for u in cursor:
        doc = _serialize_mongo_doc(u)
        doc.pop("password_hash", None)
        # Ensure default fields are present
        doc.setdefault("status", "active")
        doc.setdefault("is_active", doc.get("status") == "active")
        doc.setdefault("login_count", 0)
        doc.setdefault("failed_login_count", 0)
        users.append(doc)

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "users": users
    }

@router.post(
    "/users",
    response_model=AdminUserItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a new SOC user account with specified role and status"
)
async def create_user(
    request: AdminUserCreateRequest,
    req: Request,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    clean_email = request.email.lower().strip()
    
    # Check duplicate
    existing = await db.users.find_one({"email": clean_email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{clean_email}' already exists."
        )

    assigned_role = request.role.lower().strip()
    if assigned_role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: 'admin', 'analyst', 'viewer'."
        )

    user_status = (request.status or "active").lower().strip()
    now = datetime.utcnow()

    user_doc = {
        "name": request.name.strip(),
        "email": clean_email,
        "password_hash": hash_password(request.password),
        "role": assigned_role,
        "status": user_status,
        "is_active": (user_status == "active"),
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
        "last_logout_at": None,
        "login_count": 0,
        "failed_login_count": 0
    }

    res = await db.users.insert_one(user_doc)
    new_user_id = str(res.inserted_id)

    # Record Admin Audit Event (Feature 11)
    await log_audit_event(
        action="USER_CREATED",
        user=current_user,
        resource_type="user",
        resource_id=new_user_id,
        status="success",
        details={
            "created_by_admin": current_user["email"],
            "target_user": clean_email,
            "assigned_role": assigned_role,
            "assigned_status": user_status
        },
        request=req
    )

    user_doc["id"] = new_user_id
    user_doc.pop("password_hash", None)
    return user_doc

@router.get(
    "/users/{user_identifier}",
    response_model=AdminUserDetailResponse,
    summary="Get user profile and recent security activity timeline"
)
async def get_user_details(user_identifier: str):
    db = get_database()
    query = _build_user_query(user_identifier)
    user = await db.users.find_one(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_identifier}' not found."
        )

    user_doc = _serialize_mongo_doc(user)
    user_doc.pop("password_hash", None)
    user_doc.setdefault("status", "active")
    user_doc.setdefault("is_active", user_doc.get("status") == "active")
    user_doc.setdefault("login_count", 0)
    user_doc.setdefault("failed_login_count", 0)

    # Fetch recent activity for this user
    act_query = {
        "$or": [
            {"user_id": user_doc["id"]},
            {"email": user_doc["email"]}
        ]
    }
    cursor = db.audit_logs.find(act_query).sort("timestamp", -1).limit(20)
    activity = [_serialize_mongo_doc(a) async for a in cursor]

    return {
        "user": user_doc,
        "recent_activity": activity
    }

@router.patch(
    "/users/{user_identifier}/role",
    summary="Change user role (with Last-Admin Protection)"
)
async def update_user_role(
    user_identifier: str,
    body: AdminUserRoleUpdateRequest,
    req: Request,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    query = _build_user_query(user_identifier)
    target_user = await db.users.find_one(query)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_identifier}' not found."
        )

    new_role = body.role.lower().strip()
    if new_role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: 'admin', 'analyst', 'viewer'."
        )

    old_role = target_user.get("role", "viewer")
    target_id = str(target_user["_id"])
    target_email = target_user["email"]

    # Feature 10: Last-Admin Protection Mechanism
    if old_role == "admin" and new_role != "admin":
        active_admins_count = await db.users.count_documents({"role": "admin", "status": "active"})
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security protection: Cannot demote the final remaining active administrator account."
            )

    now = datetime.utcnow()
    await db.users.update_one(
        {"_id": target_user["_id"]},
        {"$set": {"role": new_role, "updated_at": now}}
    )

    # Audit log
    await log_audit_event(
        action="ROLE_CHANGED",
        user=current_user,
        resource_type="user",
        resource_id=target_id,
        status="success",
        details={
            "old_role": old_role,
            "new_role": new_role,
            "target_user": target_email,
            "changed_by": current_user["email"]
        },
        request=req
    )

    logger.info(f"Admin {current_user['email']} changed role of {target_email}: {old_role} -> {new_role}")
    return {
        "success": True,
        "message": f"User '{target_email}' role updated to '{new_role}'.",
        "user_id": target_id,
        "new_role": new_role
    }

@router.patch(
    "/users/{user_identifier}/status",
    summary="Enable or Disable a user account (with Last-Admin Protection)"
)
async def update_user_status(
    user_identifier: str,
    body: AdminUserStatusUpdateRequest,
    req: Request,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    query = _build_user_query(user_identifier)
    target_user = await db.users.find_one(query)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_identifier}' not found."
        )

    new_status = body.status.lower().strip()
    if new_status not in ["active", "disabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'active' or 'disabled'."
        )

    old_status = target_user.get("status", "active")
    target_id = str(target_user["_id"])
    target_email = target_user["email"]
    target_role = target_user.get("role", "viewer")

    # Feature 10 & 9: Last-Admin Protection Mechanism
    if target_role == "admin" and old_status == "active" and new_status == "disabled":
        active_admins_count = await db.users.count_documents({"role": "admin", "status": "active"})
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security protection: Cannot disable the final remaining active administrator account."
            )

    now = datetime.utcnow()
    is_active = (new_status == "active")
    await db.users.update_one(
        {"_id": target_user["_id"]},
        {"$set": {"status": new_status, "is_active": is_active, "updated_at": now}}
    )

    action_name = "USER_ENABLED" if is_active else "USER_DISABLED"
    await log_audit_event(
        action=action_name,
        user=current_user,
        resource_type="user",
        resource_id=target_id,
        status="success",
        details={
            "old_status": old_status,
            "new_status": new_status,
            "target_user": target_email,
            "changed_by": current_user["email"]
        },
        request=req
    )

    logger.info(f"Admin {current_user['email']} set status of {target_email} to '{new_status}'")
    return {
        "success": True,
        "message": f"User account '{target_email}' is now {new_status.upper()}.",
        "user_id": target_id,
        "new_status": new_status,
        "is_active": is_active
    }

# ============================================================================
# 3. Login History & Audit Trail APIs (Feature 3, Feature 5, Feature 6, Feature 7)
# ============================================================================

@router.get(
    "/login-history",
    response_model=LoginHistoryResponse,
    summary="List chronological login history with success/failed/logout filtering"
)
async def get_login_history(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter: success or failed"),
    search: Optional[str] = Query(None, description="Search by email, username, or IP address"),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100)
):
    db = get_database()
    query: Dict[str, Any] = {
        "action": {"$in": ["LOGIN_SUCCESS", "LOGIN_FAILED", "LOGOUT"]}
    }

    if status_filter and status_filter.lower() != "all":
        query["status"] = status_filter.lower().strip()

    if search:
        s = search.strip()
        query["$or"] = [
            {"email": {"$regex": s, "$options": "i"}},
            {"user_name": {"$regex": s, "$options": "i"}},
            {"ip_address": {"$regex": s, "$options": "i"}}
        ]

    total = await db.audit_logs.count_documents(query)
    skip = (page - 1) * limit
    cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)

    history = [_serialize_mongo_doc(doc) async for doc in cursor]
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "history": history
    }

@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="List complete SOC audit log stream with comprehensive filters"
)
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action name"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: success, failed"),
    search: Optional[str] = Query(None, description="Search across emails, usernames, IPs, and actions"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    db = get_database()
    query: Dict[str, Any] = {}

    if action and action.upper() != "ALL":
        query["action"] = action.upper().strip()
    if resource_type and resource_type.lower() != "all":
        query["resource_type"] = resource_type.lower().strip()
    if role and role.lower() != "all":
        query["role"] = role.lower().strip()
    if status_filter and status_filter.lower() != "all":
        query["status"] = status_filter.lower().strip()

    if search:
        s = search.strip()
        query["$or"] = [
            {"action": {"$regex": s, "$options": "i"}},
            {"email": {"$regex": s, "$options": "i"}},
            {"user_name": {"$regex": s, "$options": "i"}},
            {"ip_address": {"$regex": s, "$options": "i"}},
            {"resource_type": {"$regex": s, "$options": "i"}}
        ]

    total = await db.audit_logs.count_documents(query)
    skip = (page - 1) * limit
    cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)

    logs = [_serialize_mongo_doc(doc) async for doc in cursor]
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "logs": logs
    }

@router.get(
    "/audit-logs/{log_id}",
    response_model=AuditLogResponse,
    summary="Retrieve single audit log entry by ID"
)
async def get_audit_log_by_id(log_id: str):
    db = get_database()
    if not ObjectId.is_valid(log_id):
        raise HTTPException(status_code=400, detail="Invalid audit log ID format.")
    doc = await db.audit_logs.find_one({"_id": ObjectId(log_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Audit log entry not found.")
    return _serialize_mongo_doc(doc)

@router.get(
    "/activity/{user_id}",
    response_model=List[AuditLogResponse],
    summary="Retrieve activity audit stream for a designated user"
)
async def get_user_activity(user_id: str, limit: int = Query(30, ge=1, le=100)):
    db = get_database()
    query = {"$or": [{"user_id": user_id}]}
    if ObjectId.is_valid(user_id):
        query["$or"].append({"user_id": str(ObjectId(user_id))})

    cursor = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
    return [_serialize_mongo_doc(doc) async for doc in cursor]

# ============================================================================
# 4. Admin Reports APIs (Feature 14, Feature 18)
# ============================================================================

@router.get(
    "/reports",
    summary="List all reports for administrative review and audit"
)
async def get_admin_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    limit: int = Query(50, ge=1, le=100)
):
    db = get_database()
    query: Dict[str, Any] = {}
    if report_type and report_type.lower() != "all":
        query["report_type"] = report_type.lower().strip()
    cursor = db.reports.find(query).sort("timestamp", -1).limit(limit)
    reports = [_serialize_mongo_doc(d) async for d in cursor]
    return {
        "total": len(reports),
        "reports": reports
    }

@router.get(
    "/reports/{report_identifier}",
    summary="Retrieve report details for admin by report_id or MongoDB ID"
)
async def get_admin_report_by_id(report_identifier: str):
    db = get_database()
    query = {"$or": [{"report_id": report_identifier}]}
    if ObjectId.is_valid(report_identifier):
        query["$or"].append({"_id": ObjectId(report_identifier)})
    doc = await db.reports.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Report '{report_identifier}' not found.")
    return _serialize_mongo_doc(doc)

