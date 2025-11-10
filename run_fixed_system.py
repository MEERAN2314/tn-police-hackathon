#!/usr/bin/env python3
"""
Fixed startup script for TOR Analysis System
Handles common issues and provides fallback options
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add app to path
sys.path.append('.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check and fix environment issues"""
    logger.info("🔧 Checking environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.warning("⚠️  .env file not found, creating default...")
        create_default_env()
    
    # Check MongoDB connection
    try:
        import pymongo
        logger.info("✅ MongoDB driver available")
    except ImportError:
        logger.error("❌ MongoDB driver not installed: pip install pymongo")
        return False
    
    # Check other dependencies
    missing_deps = []
    try:
        import fastapi
        import uvicorn
        import jinja2
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        logger.error(f"❌ Missing dependencies: {missing_deps}")
        logger.error("Run: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Environment check passed")
    return True

def create_default_env():
    """Create a default .env file"""
    default_env = """# TOR Analysis System Configuration

# Database
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
DATABASE_NAME=tor_analysis

# Application
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=demo-secret-key-change-in-production

# TOR Configuration
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
TOR_DATA_REFRESH_INTERVAL=300

# External APIs
ONIONOO_API=https://onionoo.torproject.org
TOR_METRICS_API=https://metrics.torproject.org

# Optional API Keys (leave empty to use fallback data)
GEMINI_API_KEY=
IPGEOLOCATION_API_KEY=
USE_FREE_GEOLOCATION=true
"""
    
    with open('.env', 'w') as f:
        f.write(default_env)
    
    logger.info("✅ Created default .env file")

async def test_services():
    """Test core services"""
    logger.info("🧪 Testing services...")
    
    try:
        from app.database import connect_to_mongo, get_database
        
        # Test database connection
        await connect_to_mongo()
        db = await get_database()
        await db.command("ping")
        logger.info("✅ Database connection successful")
        
    except Exception as e:
        logger.warning(f"⚠️  Database connection failed: {e}")
        logger.info("💡 System will use fallback data")
    
    try:
        from app.services.tor_service import TORService
        tor_service = TORService()
        logger.info("✅ TOR service initialized")
    except Exception as e:
        logger.warning(f"⚠️  TOR service issue: {e}")
    
    logger.info("✅ Service tests completed")

async def start_server():
    """Start the server with error handling"""
    try:
        logger.info("🚀 Starting TOR Analysis System...")
        
        # Import and configure
        import uvicorn
        from app.main import socket_app
        from app.config import settings
        
        # Configure server
        config = uvicorn.Config(
            app=socket_app,
            host="0.0.0.0",
            port=8004,  # Use the port from your command
            reload=settings.debug,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        logger.info("=" * 60)
        logger.info("🎯 TOR Analysis System - Real-time Edition")
        logger.info("=" * 60)
        logger.info("🌐 Dashboard: http://localhost:8004")
        logger.info("📡 WebSocket: ws://localhost:8004/ws")
        logger.info("📖 API Docs: http://localhost:8004/docs")
        logger.info("=" * 60)
        logger.info("💡 Note: Some warnings are normal during startup")
        logger.info("🔄 Real-time data will be available shortly")
        logger.info("=" * 60)
        
        # Start server
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        raise

async def main():
    """Main function with comprehensive error handling"""
    try:
        print("\n" + "=" * 60)
        print("🔍 TOR ANALYSIS SYSTEM - STARTUP")
        print("=" * 60)
        
        # Check environment
        if not check_environment():
            sys.exit(1)
        
        # Test services
        await test_services()
        
        # Start server
        await start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("💡 Try running: python run_fixed_system.py")
        sys.exit(1)
    finally:
        logger.info("👋 TOR Analysis System stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print("💡 Check the logs above for details")