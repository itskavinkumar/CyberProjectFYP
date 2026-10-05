from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.config import settings
from backend.app.utils.logging import logger
from typing import Optional

class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    """Connect to MongoDB and initialize collections and indexes."""
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000
        )
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        
        # Verify connection by pinging
        await db_manager.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB database: '{settings.DATABASE_NAME}'")
        
        # Create indexes for optimal query performance
        await init_db_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        # We don't crash here so API health check can report status accurately
        
async def close_mongo_connection():
    """Close MongoDB connection pool."""
    if db_manager.client:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Retrieve active database instance."""
    if db_manager.db is None:
        raise ConnectionError("Database not initialized. Please ensure MongoDB is running.")
    return db_manager.db

async def init_db_indexes():
    """Create essential compound indexes on collections."""
    if db_manager.db is None:
        return
        
    try:
        # threat_events indexes
        await db_manager.db.threat_events.create_index([("date", 1), ("threat_type", 1)])
        await db_manager.db.threat_events.create_index([("threat_type", 1)])
        await db_manager.db.threat_events.create_index([("severity", 1)])
        
        # forecasts indexes
        await db_manager.db.forecasts.create_index([("threat_type", 1), ("forecast_date", 1)])
        
        # users index
        await db_manager.db.users.create_index([("email", 1)], unique=True)
        await db_manager.db.users.create_index([("role", 1)])
        await db_manager.db.users.create_index([("status", 1)])
        
        # models index
        await db_manager.db.models.create_index([("threat_type", 1)], unique=True)
        
        # audit_logs indexes (Feature 22)
        await db_manager.db.audit_logs.create_index([("timestamp", -1)])
        await db_manager.db.audit_logs.create_index([("action", 1), ("timestamp", -1)])
        await db_manager.db.audit_logs.create_index([("user_id", 1), ("timestamp", -1)])
        await db_manager.db.audit_logs.create_index([("email", 1), ("timestamp", -1)])
        await db_manager.db.audit_logs.create_index([("status", 1), ("timestamp", -1)])
        
        # reports indexes (Feature 22)
        await db_manager.db.reports.create_index([("timestamp", -1)])
        await db_manager.db.reports.create_index([("generated_by", 1), ("timestamp", -1)])
        await db_manager.db.reports.create_index([("report_type", 1), ("timestamp", -1)])
        
        logger.info("MongoDB indexes successfully verified and initialized.")
        
        # Migrate existing users to have default schema attributes if missing
        await migrate_user_defaults()
    except Exception as e:
        logger.warning(f"Index creation warning: {str(e)}")

async def migrate_user_defaults():
    """Ensures existing user records have backward-compatible default fields."""
    if db_manager.db is None:
        return
    try:
        res = await db_manager.db.users.update_many(
            {"status": {"$exists": False}},
            {"$set": {
                "status": "active",
                "is_active": True,
                "login_count": 0,
                "failed_login_count": 0,
                "last_login_at": None,
                "last_logout_at": None,
                "updated_at": None
            }}
        )
        if res.modified_count > 0:
            logger.info(f"Migrated {res.modified_count} legacy user records with active default status.")
    except Exception as e:
        logger.warning(f"User schema migration warning: {str(e)}")

# Helper collection accessors
def get_users_collection():
    return get_database()["users"]

def get_threats_collection():
    return get_database()["threat_events"]

def get_forecasts_collection():
    return get_database()["forecasts"]

def get_datasets_collection():
    return get_database()["datasets"]

def get_models_collection():
    return get_database()["models"]

def get_audit_logs_collection():
    return get_database()["audit_logs"]

def get_reports_collection():
    return get_database()["reports"]

