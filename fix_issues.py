#!/usr/bin/env python3
"""
Quick fix script for common TOR Analysis System issues
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_env_file():
    """Fix .env file issues"""
    logger.info("🔧 Fixing .env file...")
    
    env_content = """# TOR Analysis System Configuration - Fixed

# Database
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
DATABASE_NAME=tor_analysis

# Application
DEBUG=true
LOG_LEVEL=WARNING
SECRET_KEY=demo-secret-key-change-in-production

# TOR Configuration
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
TOR_DATA_REFRESH_INTERVAL=300

# External APIs
ONIONOO_API=https://onionoo.torproject.org
TOR_METRICS_API=https://metrics.torproject.org

# API Keys (Optional - system works without these)
GEMINI_API_KEY=
IPGEOLOCATION_API_KEY=
USE_FREE_GEOLOCATION=true

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    logger.info("✅ .env file updated")

def create_startup_script():
    """Create a simple startup script"""
    logger.info("🔧 Creating startup script...")
    
    startup_content = '''#!/bin/bash
echo "🚀 Starting TOR Analysis System..."
echo "📍 Using port 8004 as requested"
echo "⚠️  Some warnings during startup are normal"
echo ""

# Set environment variables to reduce noise
export PYTHONWARNINGS="ignore"
export LOG_LEVEL="WARNING"

# Start the server
python -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8004 --reload --log-level warning

echo "👋 Server stopped"
'''
    
    with open('start_server.sh', 'w') as f:
        f.write(startup_content)
    
    os.chmod('start_server.sh', 0o755)
    logger.info("✅ Created start_server.sh")

def main():
    """Main fix function"""
    logger.info("🔧 TOR Analysis System - Quick Fix")
    logger.info("=" * 50)
    
    # Fix .env file
    fix_env_file()
    
    # Create startup script
    create_startup_script()
    
    logger.info("=" * 50)
    logger.info("✅ Fixes applied successfully!")
    logger.info("")
    logger.info("🚀 To start the system:")
    logger.info("   ./start_server.sh")
    logger.info("   OR")
    logger.info("   python run_fixed_system.py")
    logger.info("")
    logger.info("🌐 Dashboard will be available at:")
    logger.info("   http://localhost:8004")
    logger.info("")
    logger.info("💡 Notes:")
    logger.info("   - Some API warnings are normal")
    logger.info("   - System uses fallback data when APIs are unavailable")
    logger.info("   - Real TOR data will load in the background")

if __name__ == "__main__":
    main()