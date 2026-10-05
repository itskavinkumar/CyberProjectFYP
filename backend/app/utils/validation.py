from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
from backend.app.config import settings

REQUIRED_COLUMNS = ["Date", "Threat_Type", "Severity", "Count"]

def validate_threat_type(threat_type: str) -> bool:
    """Validate that the threat type belongs to supported categories."""
    return threat_type in settings.SUPPORTED_THREAT_TYPES

def validate_forecast_horizon(days: int) -> bool:
    """Validate that the forecast horizon is valid (e.g. 7, 14, 30 days)."""
    return days in settings.DEFAULT_FORECAST_HORIZONS or (1 <= days <= 90)

def validate_csv_dataset(df: pd.DataFrame) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validates an uploaded CSV dataset for required columns, data types,
    and valid threat categories and severity ratings.
    """
    errors: List[str] = []
    
    # Check column names (case-insensitive mapping)
    col_map = {c.lower(): c for c in df.columns}
    normalized_cols = {req.lower(): col_map.get(req.lower()) for req in REQUIRED_COLUMNS}
    
    missing_cols = [req for req in REQUIRED_COLUMNS if normalized_cols[req.lower()] is None]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, errors, {}
    
    # Standardize column names
    rename_dict = {normalized_cols[req.lower()]: req for req in REQUIRED_COLUMNS}
    df = df.rename(columns=rename_dict)
    
    # Row count check
    if len(df) == 0:
        errors.append("Dataset is empty.")
        return False, errors, {}
    
    # Date validation
    invalid_dates = pd.to_datetime(df["Date"], errors="coerce").isna().sum()
    if invalid_dates > 0:
        errors.append(f"Dataset contains {invalid_dates} invalid or unparseable dates.")
    
    # Count validation
    invalid_counts = pd.to_numeric(df["Count"], errors="coerce").isna().sum()
    negative_counts = (pd.to_numeric(df["Count"], errors="coerce") < 0).sum()
    if invalid_counts > 0:
        errors.append(f"Dataset contains {invalid_counts} invalid numerical counts.")
    if negative_counts > 0:
        errors.append(f"Dataset contains {negative_counts} negative counts.")
        
    # Check recognized threat types
    found_threats = df["Threat_Type"].dropna().unique().tolist()
    unrecognized_threats = [t for t in found_threats if t not in settings.SUPPORTED_THREAT_TYPES]
    
    # Summary metadata
    parsed_dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
    summary = {
        "total_records": int(len(df)),
        "valid_records": int(len(df) - int(invalid_dates) - int(invalid_counts)),
        "date_range": {
            "start": str(parsed_dates.min().date()) if not parsed_dates.empty else None,
            "end": str(parsed_dates.max().date()) if not parsed_dates.empty else None
        },
        "threat_types_found": [str(t) for t in found_threats],
        "unrecognized_threat_types": [str(t) for t in unrecognized_threats],
        "severities_found": [str(s) for s in (df["Severity"].dropna().unique().tolist() if "Severity" in df.columns else [])]
    }
    
    is_valid = len(errors) == 0
    return is_valid, errors, summary
