from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.database import get_database
from backend.app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse
)
from backend.app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.logging import logger

router = APIRouter()

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new analyst or viewer"
)
async def register(request: UserRegisterRequest, req: Request):
    db = get_database()
    
    # 1. Critical Security Rule: Prevent public registration as ADMIN
    requested_role = (request.role or "analyst").strip().lower()
    if requested_role == "admin":
        logger.warning(f"Rejected public self-registration attempt as admin: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative accounts cannot be self-registered publicly. Contact a SOC Administrator."
        )
    
    # Normalize valid public roles (analyst or viewer)
    assigned_role = "viewer" if requested_role == "viewer" else "analyst"
    clean_email = request.email.lower().strip()

    # 2. Check if user already exists
    existing_user = await db.users.find_one({"email": clean_email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    now = datetime.utcnow()
    user_doc = {
        "name": request.name.strip(),
        "email": clean_email,
        "password_hash": hash_password(request.password),
        "role": assigned_role,
        "status": "active",
        "is_active": True,
        "created_at": now,
        "updated_at": None,
        "last_login_at": None,
        "last_logout_at": None,
        "login_count": 0,
        "failed_login_count": 0
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # 3. Record Audit Trail Event (Feature 11)
    await log_audit_event(
        action="REGISTER",
        email=clean_email,
        user_name=user_doc["name"],
        role=assigned_role,
        resource_type="auth",
        resource_id=user_id,
        status="success",
        details={"assigned_role": assigned_role, "registration_type": "public_self_service"},
        request=req
    )
    
    # 4. Generate JWT token
    token = create_access_token(data={"sub": user_doc["email"], "role": user_doc["role"]})
    
    logger.info(f"New user registered: {user_doc['email']} with role {user_doc['role']}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_doc["name"],
            "email": user_doc["email"],
            "role": user_doc["role"],
            "status": user_doc["status"]
        }
    }

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user, update login telemetry, and return JWT bearer token"
)
async def login(request: UserLoginRequest, req: Request):
    db = get_database()
    clean_email = request.email.lower().strip()
    user = await db.users.find_one({"email": clean_email})
    
    # 1. Non-existent user check
    if not user:
        await log_audit_event(
            action="LOGIN_FAILED",
            email=clean_email,
            resource_type="auth",
            status="failed",
            details={"reason": "user_not_found"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = str(user.get("_id", ""))
    user_role = user.get("role", "viewer")
    user_name = user.get("name", "Operator")
    
    # 2. Account disabled check (Feature 9)
    if user.get("status") == "disabled" or user.get("is_active") is False:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$inc": {"failed_login_count": 1}}
        )
        await log_audit_event(
            action="LOGIN_FAILED",
            user=user,
            resource_type="auth",
            resource_id=user_id,
            status="failed",
            details={"reason": "account_disabled"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Please contact SOC administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Password verification check
    if not verify_password(request.password, user.get("password_hash", "")):
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$inc": {"failed_login_count": 1}}
        )
        await log_audit_event(
            action="LOGIN_FAILED",
            user=user,
            resource_type="auth",
            resource_id=user_id,
            status="failed",
            details={"reason": "invalid_credentials"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Successful login: update last_login_at and increment login_count (Feature 3)
    login_time = datetime.utcnow()
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"last_login_at": login_time},
            "$inc": {"login_count": 1}
        }
    )
    
    # 5. Record successful login in audit trail
    await log_audit_event(
        action="LOGIN_SUCCESS",
        user=user,
        resource_type="auth",
        resource_id=user_id,
        status="success",
        details={"login_count": user.get("login_count", 0) + 1},
        request=req
    )

    token = create_access_token(data={"sub": user["email"], "role": user_role})
    logger.info(f"Successful login for user: {user['email']} (Role: {user_role})")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_name,
            "email": user["email"],
            "role": user_role,
            "status": user.get("status", "active")
        }
    }

@router.post(
    "/token",
    response_model=TokenResponse,
    include_in_schema=True,
    summary="OAuth2 compatible password login for API docs"
)
async def login_for_access_token(req: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    clean_email = form_data.username.lower().strip()
    user = await db.users.find_one({"email": clean_email})
    
    if not user:
        await log_audit_event(
            action="LOGIN_FAILED",
            email=clean_email,
            resource_type="auth",
            status="failed",
            details={"reason": "user_not_found"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = str(user.get("_id", ""))
    if user.get("status") == "disabled" or user.get("is_active") is False:
        await db.users.update_one({"_id": user["_id"]}, {"$inc": {"failed_login_count": 1}})
        await log_audit_event(
            action="LOGIN_FAILED",
            user=user,
            resource_type="auth",
            resource_id=user_id,
            status="failed",
            details={"reason": "account_disabled"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Please contact SOC administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.get("password_hash", "")):
        await db.users.update_one({"_id": user["_id"]}, {"$inc": {"failed_login_count": 1}})
        await log_audit_event(
            action="LOGIN_FAILED",
            user=user,
            resource_type="auth",
            resource_id=user_id,
            status="failed",
            details={"reason": "invalid_credentials"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    now = datetime.utcnow()
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": now}, "$inc": {"login_count": 1}}
    )
    
    await log_audit_event(
        action="LOGIN_SUCCESS",
        user=user,
        resource_type="auth",
        resource_id=user_id,
        status="success",
        request=req
    )

    token = create_access_token(data={"sub": user["email"], "role": user.get("role", "analyst")})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "analyst"),
            "status": user.get("status", "active")
        }
    }

@router.post(
    "/logout",
    summary="Explicitly log out active session and record audit event"
)
async def logout(req: Request, current_user: dict = Depends(get_current_user)):
    """
    Records an explicit logout audit event and updates last_logout_at.
    Note: Client-side storage (localStorage) token removal completes the sign-out.
    """
    db = get_database()
    now = datetime.utcnow()
    user_id = current_user.get("id") or str(current_user.get("_id", ""))
    
    # Update last_logout_at
    await db.users.update_one(
        {"email": current_user["email"]},
        {"$set": {"last_logout_at": now}}
    )
    
    # Audit log (Feature 4)
    await log_audit_event(
        action="LOGOUT",
        user=current_user,
        resource_type="auth",
        resource_id=user_id,
        status="success",
        details={"client_note": "Client-side JWT token deleted"},
        request=req
    )
    
    logger.info(f"User logged out: {current_user['email']}")
    return {
        "success": True,
        "message": "User session closed successfully."
    }

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Retrieve profile of currently authenticated user"
)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.get("id") or str(current_user.get("_id", "")),
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user.get("role", "analyst"),
        "status": current_user.get("status", "active"),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user.get("created_at"),
        "last_login_at": current_user.get("last_login_at"),
        "login_count": current_user.get("login_count", 0)
    }
