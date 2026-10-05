import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Ensure workspace root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(BACKEND_DIR)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

DATA_RAW_DIR = os.path.join(BACKEND_DIR, "data", "raw")
OUTPUT_CSV = os.path.join(DATA_RAW_DIR, "synthetic_threat_events.csv")

# Constants
START_DATE = datetime(2024, 1, 1)
NUM_DAYS = 730  # 2 full years (2024-01-01 through 2025-12-31)

THREAT_PROFILES = {
    "Phishing": {
        "base_count": 85,
        "trend_slope": 0.06,      # Gradually increasing over time
        "weekday_boost": 1.45,    # Heavily weekday-oriented (work emails)
        "weekend_mult": 0.40,
        "seasonal_freq": 90,      # Quarterly phishing blitzes
        "seasonal_amp": 25,
        "burst_prob": 0.05,
        "burst_mult": 2.2,
        "severity_weights": {"Low": 0.20, "Medium": 0.50, "High": 0.25, "Critical": 0.05},
        "sources": ["Email-Gateway", "Spam-Filter", "User-Report", "EDR-Agent"],
        "locations": ["North America", "Europe", "Asia-Pacific", "Latin America"],
        "desc_template": "Credential harvesting / spear-phishing campaign detected"
    },
    "Malware": {
        "base_count": 65,
        "trend_slope": 0.04,
        "weekday_boost": 1.15,
        "weekend_mult": 0.85,
        "seasonal_freq": 60,
        "seasonal_amp": 15,
        "burst_prob": 0.06,
        "burst_mult": 2.5,
        "severity_weights": {"Low": 0.10, "Medium": 0.35, "High": 0.40, "Critical": 0.15},
        "sources": ["EDR-Agent", "Antivirus-Console", "Firewall-IDS", "Sandbox-Analysis"],
        "locations": ["North America", "Europe", "Asia-Pacific", "Global"],
        "desc_template": "Trojan/loader dropper signature triggered on enterprise host"
    },
    "Brute Force": {
        "base_count": 120,
        "trend_slope": 0.03,
        "weekday_boost": 0.90,
        "weekend_mult": 1.25,     # Threat actors scan heavily on weekends
        "seasonal_freq": 30,
        "seasonal_amp": 20,
        "burst_prob": 0.08,
        "burst_mult": 2.8,
        "severity_weights": {"Low": 0.45, "Medium": 0.40, "High": 0.12, "Critical": 0.03},
        "sources": ["Firewall-IDS", "SSH-Auth-Log", "RDP-Gateway", "VPN-Concentrator"],
        "locations": ["Global", "North America", "Europe", "Asia-Pacific"],
        "desc_template": "High-frequency credential stuffing against remote authentication service"
    },
    "DDoS": {
        "base_count": 40,
        "trend_slope": 0.05,
        "weekday_boost": 0.95,
        "weekend_mult": 1.35,     # Peak gaming/commercial weekend disruptions
        "seasonal_freq": 45,
        "seasonal_amp": 18,
        "burst_prob": 0.04,
        "burst_mult": 4.5,        # Massive sudden volumetric surge
        "severity_weights": {"Low": 0.05, "Medium": 0.20, "High": 0.50, "Critical": 0.25},
        "sources": ["WAF-Gateway", "Cloud-Scrubbing-Center", "BGP-Monitor", "Core-Router"],
        "locations": ["North America", "Europe", "Asia-Pacific", "Latin America"],
        "desc_template": "Distributed volumetric UDP/SYN amplification flood attack"
    },
    "Botnet": {
        "base_count": 55,
        "trend_slope": 0.05,
        "weekday_boost": 1.05,
        "weekend_mult": 1.15,
        "seasonal_freq": 40,
        "seasonal_amp": 12,
        "burst_prob": 0.07,
        "burst_mult": 2.4,
        "severity_weights": {"Low": 0.25, "Medium": 0.45, "High": 0.25, "Critical": 0.05},
        "sources": ["DNS-Sinkhole", "Honeypot-Sensor", "NetFlow-Analyzer", "Threat-Feed"],
        "locations": ["Global", "Asia-Pacific", "Europe", "North America"],
        "desc_template": "Automated C2 beaconing and zombie node coordination traffic"
    },
    "SQL Injection": {
        "base_count": 45,
        "trend_slope": 0.02,
        "weekday_boost": 1.20,
        "weekend_mult": 0.80,
        "seasonal_freq": 50,
        "seasonal_amp": 10,
        "burst_prob": 0.05,
        "burst_mult": 2.2,
        "severity_weights": {"Low": 0.30, "Medium": 0.45, "High": 0.20, "Critical": 0.05},
        "sources": ["WAF-Gateway", "App-Access-Logs", "API-Gateway", "DB-Audit-Log"],
        "locations": ["North America", "Europe", "Asia-Pacific"],
        "desc_template": "Automated SQL injection probe payloads against public endpoints"
    },
    "Ransomware": {
        "base_count": 18,
        "trend_slope": 0.07,      # Escalating trend over the years
        "weekday_boost": 1.30,    # Triggered during working hours or Friday nights
        "weekend_mult": 0.70,
        "seasonal_freq": 75,
        "seasonal_amp": 8,
        "burst_prob": 0.03,
        "burst_mult": 3.8,        # High-impact double-extortion campaigns
        "severity_weights": {"Low": 0.02, "Medium": 0.08, "High": 0.40, "Critical": 0.50},
        "sources": ["EDR-Agent", "SIEM-Collector", "Backup-Vault-Monitor", "Incident-Response"],
        "locations": ["North America", "Europe", "Asia-Pacific", "Middle East"],
        "desc_template": "Volume shadow copy deletion and bulk encryption telemetry flagged"
    },
    "Data Breach": {
        "base_count": 12,
        "trend_slope": 0.05,
        "weekday_boost": 1.25,
        "weekend_mult": 0.65,
        "seasonal_freq": 90,
        "seasonal_amp": 6,
        "burst_prob": 0.02,
        "burst_mult": 4.0,
        "severity_weights": {"Low": 0.01, "Medium": 0.14, "High": 0.45, "Critical": 0.40},
        "sources": ["DLP-Agent", "Cloud-Security-Broker", "SIEM-Collector", "Audit-Log"],
        "locations": ["North America", "Europe", "Asia-Pacific", "Latin America"],
        "desc_template": "Anomalous exfiltration volume detected from critical repository"
    }
}

def generate_synthetic_dataset(output_path: str = OUTPUT_CSV) -> pd.DataFrame:
    """
    Generates realistic, chronologically structured time-series cybersecurity threat data
    with clear trends, weekly patterns, quarterly seasonality, noise, and attack surges.
    """
    np.random.seed(42)
    random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    dates = [START_DATE + timedelta(days=i) for i in range(NUM_DAYS)]
    records = []
    
    for threat_name, profile in THREAT_PROFILES.items():
        base = profile["base_count"]
        slope = profile["trend_slope"]
        sev_weights = profile["severity_weights"]
        severities = list(sev_weights.keys())
        weights = list(sev_weights.values())
        
        # Burst state tracker for multi-day attack campaigns
        burst_days_remaining = 0
        current_burst_factor = 1.0
        
        for t, dt in enumerate(dates):
            # 1. Base trend (linear growth)
            trend_val = base + (slope * t)
            
            # 2. Weekly seasonality
            is_weekend = dt.weekday() >= 5
            weekday_factor = profile["weekend_mult"] if is_weekend else profile["weekday_boost"]
            
            # 3. Cyclical / seasonal pattern
            seasonal_factor = profile["seasonal_amp"] * np.sin(2 * np.pi * t / profile["seasonal_freq"])
            
            # 4. Multi-day attack burst simulation
            if burst_days_remaining > 0:
                burst_days_remaining -= 1
            else:
                if random.random() < profile["burst_prob"]:
                    burst_days_remaining = random.randint(2, 4)
                    current_burst_factor = random.uniform(profile["burst_mult"] * 0.8, profile["burst_mult"] * 1.2)
                else:
                    current_burst_factor = 1.0
            
            # 5. Stochastic noise
            noise = np.random.normal(0, max(2, base * 0.12))
            
            # Calculate final total daily count
            total_daily_count = (trend_val * weekday_factor + seasonal_factor) * current_burst_factor + noise
            total_daily_count = max(2, int(round(total_daily_count)))
            
            # Distribute into severity records for realistic granular breakdown
            # We break each day into 1 to 4 distinct logging events
            num_sub_events = random.randint(2, 4)
            proportions = np.random.dirichlet(np.ones(num_sub_events))
            sub_counts = [max(1, int(round(p * total_daily_count))) for p in proportions]
            
            for cnt in sub_counts:
                sev = np.random.choice(severities, p=weights)
                src = random.choice(profile["sources"])
                loc = random.choice(profile["locations"])
                date_str = dt.strftime("%Y-%m-%d")
                
                records.append({
                    "Date": date_str,
                    "Threat_Type": threat_name,
                    "Severity": sev,
                    "Source": src,
                    "Location": loc,
                    "Count": cnt,
                    "Description": f"{profile['desc_template']} - Severity {sev}"
                })
                
    df = pd.DataFrame(records)
    # Sort chronologically and by threat type
    df = df.sort_values(by=["Date", "Threat_Type"]).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"[+] Successfully generated realistic synthetic dataset:")
    print(f"    - Total Records: {len(df):,}")
    print(f"    - Date Range: {df['Date'].min()} to {df['Date'].max()} ({NUM_DAYS} days)")
    print(f"    - Threat Types: {', '.join(df['Threat_Type'].unique())}")
    print(f"    - Output File: {output_path}")
    
    return df

async def seed_mongodb(df: pd.DataFrame = None):
    """Seed the MongoDB database with synthetic dataset events."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from backend.app.config import settings
    
    if df is None:
        if os.path.exists(OUTPUT_CSV):
            df = pd.read_csv(OUTPUT_CSV)
        else:
            df = generate_synthetic_dataset()
            
    print(f"[*] Connecting to MongoDB at {settings.MONGODB_URI} to seed threat events...")
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.DATABASE_NAME]
    
    # Check existing count
    existing_count = await db.threat_events.count_documents({})
    if existing_count > 0:
        print(f"[*] Existing threat_events collection has {existing_count:,} records.")
        print("[*] Clearing previous threat_events to ensure fresh clean state...")
        await db.threat_events.delete_many({})
        
    # Normalize fields to lowercase for MongoDB schema consistency
    mongo_records = []
    for r in df.to_dict(orient="records"):
        mongo_records.append({
            "date": str(r.get("Date") or r.get("date")),
            "threat_type": str(r.get("Threat_Type") or r.get("threat_type")),
            "severity": str(r.get("Severity") or r.get("severity")),
            "source": str(r.get("Source") or r.get("source", "Sensor")),
            "location": str(r.get("Location") or r.get("location", "Global")),
            "count": int(r.get("Count") or r.get("count", 1)),
            "description": str(r.get("Description") or r.get("description", ""))
        })
        
    batch_size = 1000
    for i in range(0, len(mongo_records), batch_size):
        batch = mongo_records[i:i + batch_size]
        await db.threat_events.insert_many(batch)
        
    total_inserted = await db.threat_events.count_documents({})
    print(f"[+] MongoDB threat_events collection seeded with {total_inserted:,} documents.")
    
    # Also register default synthetic dataset in datasets collection
    await db.datasets.update_one(
        {"filename": "synthetic_threat_events.csv"},
        {
            "$set": {
                "filename": "synthetic_threat_events.csv",
                "upload_date": datetime.utcnow(),
                "number_of_records": len(df),
                "date_range": {
                    "start_date": str(df["Date"].min()),
                    "end_date": str(df["Date"].max())
                },
                "threat_types": df["Threat_Type"].unique().tolist(),
                "processing_status": "processed",
                "validation_report": {
                    "synthetic": True,
                    "is_valid": True,
                    "records": len(df)
                }
            }
        },
        upsert=True
    )
    print("[+] Registered synthetic dataset entry in 'datasets' collection.")
    client.close()

if __name__ == "__main__":
    import asyncio
    print("=== Generating Synthetic Cyber Threat Dataset ===")
    df = generate_synthetic_dataset()
    print("\n=== Seeding MongoDB with Generated Data ===")
    asyncio.run(seed_mongodb(df))
    print("[+] Phase 1 Data Generation & Database Seeding Complete!")
