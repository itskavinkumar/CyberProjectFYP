import io
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request, Depends
from bson import ObjectId

from backend.app.config import settings
from backend.app.database import get_database
from backend.app.models.schemas import DatasetUploadResponse
from backend.app.utils.validation import validate_csv_dataset
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.security import get_optional_current_user
from backend.app.utils.logging import logger

router = APIRouter()

@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload, validate, and ingest cybersecurity CSV dataset"
)
async def upload_dataset(
    req: Request,
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    # RBAC Guard: Viewers cannot upload datasets
    if current_user and (current_user.get("role") or "").lower() == "viewer":
        await log_audit_event(
            action="DATASET_REJECTED",
            user=current_user,
            resource_type="dataset",
            status="failed",
            details={"filename": file.filename, "reason": "viewer_role_prohibited"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Viewers cannot upload datasets. Operation requires Analyst or Admin role."
        )

    # 1. Validate file extension
    filename = file.filename or "uploaded_dataset.csv"
    if not filename.lower().endswith(".csv"):
        await log_audit_event(
            action="DATASET_REJECTED",
            user=current_user,
            resource_type="dataset",
            status="failed",
            details={"filename": filename, "reason": "invalid_extension"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files (.csv) are supported."
        )

    # 2. Read contents into DataFrame
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        logger.error(f"Error parsing uploaded CSV '{filename}': {str(e)}")
        await log_audit_event(
            action="DATASET_REJECTED",
            user=current_user,
            resource_type="dataset",
            status="failed",
            details={"filename": filename, "reason": f"read_error: {str(e)}"},
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read CSV content: {str(e)}"
        )

    # 3. Validate dataset schema and contents
    is_valid, errors, summary = validate_csv_dataset(df)
    dataset_id = f"ds_{uuid.uuid4().hex[:10]}"
    
    if not is_valid:
        logger.warning(f"Uploaded dataset '{filename}' failed validation: {errors}")
        await log_audit_event(
            action="DATASET_REJECTED",
            user=current_user,
            resource_type="dataset",
            resource_id=dataset_id,
            status="failed",
            details={
                "filename": filename,
                "errors": errors[:5],
                "summary": summary
            },
            request=req
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dataset validation failed.",
                "errors": errors,
                "summary": summary
            }
        )


    # 4. Standardize columns
    col_map = {c.lower(): c for c in df.columns}
    date_col = col_map.get("date")
    threat_col = col_map.get("threat_type") or col_map.get("threat")
    sev_col = col_map.get("severity")
    count_col = col_map.get("count")
    src_col = col_map.get("source")
    loc_col = col_map.get("location")
    desc_col = col_map.get("description")

    # Ingest records into MongoDB in batches
    db = get_database()
    mongo_records = []
    
    for _, row in df.iterrows():
        mongo_records.append({
            "date": str(row[date_col]),
            "threat_type": str(row[threat_col]),
            "severity": str(row[sev_col]),
            "source": str(row[src_col]) if src_col and pd.notna(row.get(src_col)) else "Sensor",
            "location": str(row[loc_col]) if loc_col and pd.notna(row.get(loc_col)) else "Global",
            "count": int(row[count_col]),
            "description": str(row[desc_col]) if desc_col and pd.notna(row.get(desc_col)) else "",
            "dataset_id": dataset_id,
            "created_at": datetime.utcnow()
        })

    batch_size = 1000
    for i in range(0, len(mongo_records), batch_size):
        await db.threat_events.insert_many(mongo_records[i:i + batch_size])

    # 5. Register in datasets collection
    dataset_record = {
        "dataset_id": dataset_id,
        "filename": filename,
        "upload_date": datetime.utcnow(),
        "number_of_records": len(df),
        "date_range": summary.get("date_range", {}),
        "threat_types": summary.get("threat_types_found", []),
        "processing_status": "processed",
        "validation_report": {
            "is_valid": True,
            "errors": [],
            "summary": summary
        }
    }
    await db.datasets.insert_one(dataset_record)
    logger.info(f"Dataset '{filename}' successfully ingested: {len(df):,} events (ID: {dataset_id})")

    # Feature 12: Audit Event for Dataset Ingestion
    uploader_name = current_user.get("email") if current_user else "System/Automated"
    await log_audit_event(
        action="DATASET_UPLOADED",
        user=current_user,
        resource_type="dataset",
        resource_id=dataset_id,
        status="success",
        details={
            "dataset_id": dataset_id,
            "filename": filename,
            "record_count": len(df),
            "threat_types": summary.get("threat_types_found", []),
            "date_range": summary.get("date_range", {}),
            "uploader": uploader_name,
            "validation_status": "valid"
        },
        request=req
    )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "number_of_records": len(df),
        "date_range": summary.get("date_range", {}),
        "threat_types": summary.get("threat_types_found", []),
        "is_valid": True,
        "errors": [],
        "summary": summary
    }


@router.get(
    "",
    summary="List all registered datasets"
)
async def list_datasets():
    db = get_database()
    cursor = db.datasets.find({}).sort("upload_date", -1)
    datasets = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        datasets.append(doc)
    return {
        "total": len(datasets),
        "datasets": datasets
    }

@router.get(
    "/{dataset_identifier}",
    summary="Get details and validation report of a specific dataset"
)
async def get_dataset_details(dataset_identifier: str):
    db = get_database()
    
    # Try finding by dataset_id first, then filename, then Mongo ObjectId
    query = {"$or": [{"dataset_id": dataset_identifier}, {"filename": dataset_identifier}]}
    if ObjectId.is_valid(dataset_identifier):
        query["$or"].append({"_id": ObjectId(dataset_identifier)})
        
    doc = await db.datasets.find_one(query)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_identifier}' not found."
        )
        
    doc["id"] = str(doc.pop("_id"))
    return doc
