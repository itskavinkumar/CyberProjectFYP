from pymongo import MongoClient
import datetime
from backend.app.utils.security import hash_password

db = MongoClient("mongodb://localhost:27017")["cyber_threat_forecast"]
db.users.update_one(
    {"email": "analyst@soc.defense.gov"},
    {"$set": {
        "name": "SOC Threat Analyst",
        "email": "analyst@soc.defense.gov",
        "password_hash": hash_password("CyberAnalyst2026!"),
        "role": "analyst",
        "status": "active",
        "is_active": True,
        "login_count": 0,
        "failed_login_count": 0,
        "created_at": datetime.datetime.utcnow()
    }},
    upsert=True
)
db.users.update_one(
    {"email": "admin@soc.defense.gov"},
    {"$set": {
        "name": "SOC Director",
        "email": "admin@soc.defense.gov",
        "password_hash": hash_password("CyberAdmin2026!"),
        "role": "admin",
        "status": "active",
        "is_active": True,
        "login_count": 0,
        "failed_login_count": 0,
        "created_at": datetime.datetime.utcnow()
    }},
    upsert=True
)
db.users.update_one(
    {"email": "viewer@soc.defense.gov"},
    {"$set": {
        "name": "SOC Intelligence Auditor",
        "email": "viewer@soc.defense.gov",
        "password_hash": hash_password("CyberViewer2026!"),
        "role": "viewer",
        "status": "active",
        "is_active": True,
        "login_count": 0,
        "failed_login_count": 0,
        "created_at": datetime.datetime.utcnow()
    }},
    upsert=True
)
print("Demo users (analyst, admin, viewer) seeded successfully!")
