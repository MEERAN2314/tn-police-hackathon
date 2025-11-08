from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

# MongoDB connection
async def connect_to_mongo():
    """Create database connection"""
    try:
        Database.client = AsyncIOMotorClient(settings.mongodb_url)
        Database.database = Database.client[settings.database_name]
        
        # Test connection
        await Database.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if Database.client:
        Database.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # TOR nodes collection indexes
        await Database.database.tor_nodes.create_index("fingerprint", unique=True)
        await Database.database.tor_nodes.create_index("nickname")
        await Database.database.tor_nodes.create_index("country")
        await Database.database.tor_nodes.create_index("type")
        await Database.database.tor_nodes.create_index("last_seen")
        
        # Traffic analysis collection indexes
        await Database.database.traffic_analysis.create_index("timestamp")
        await Database.database.traffic_analysis.create_index("entry_node")
        await Database.database.traffic_analysis.create_index("exit_node")
        await Database.database.traffic_analysis.create_index("correlation_id")
        
        # Correlations collection indexes
        await Database.database.correlations.create_index("confidence_score")
        await Database.database.correlations.create_index("created_at")
        await Database.database.correlations.create_index("origin_ip")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

# Redis connection
def get_redis_client():
    """Get Redis client for caching and task queue"""
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        logger.info("Successfully connected to Redis")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

# Database dependency
async def get_database():
    return Database.database