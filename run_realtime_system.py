#!/usr/bin/env python3
"""
Enhanced startup script for TOR Analysis System with real-time capabilities
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime

# Add app to path
sys.path.append('.')

from app.main import socket_app
from app.config import settings
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TORAnalysisServer:
    """Enhanced server class for TOR Analysis System"""
    
    def __init__(self):
        self.server = None
        self.running = False
        
    async def start_server(self):
        """Start the server with real-time capabilities"""
        try:
            logger.info("=" * 80)
            logger.info("🔍 TOR Analysis System - Real-time Edition")
            logger.info("=" * 80)
            logger.info(f"🚀 Starting server on http://0.0.0.0:8000")
            logger.info(f"📊 Dashboard: http://localhost:8000")
            logger.info(f"🔗 WebSocket: ws://localhost:8000/ws")
            logger.info(f"📖 API Docs: http://localhost:8000/docs")
            logger.info("=" * 80)
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=socket_app,
                host="0.0.0.0",
                port=8000,
                reload=settings.debug,
                log_level=settings.log_level.lower(),
                access_log=True,
                ws_ping_interval=20,
                ws_ping_timeout=20
            )
            
            self.server = uvicorn.Server(config)
            self.running = True
            
            # Start server
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            raise
            
    async def stop_server(self):
        """Stop the server gracefully"""
        if self.server and self.running:
            logger.info("🛑 Stopping TOR Analysis System...")
            self.running = False
            self.server.should_exit = True
            
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}")
            asyncio.create_task(self.stop_server())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def print_system_info():
    """Print system information and features"""
    logger.info("🔧 System Configuration:")
    logger.info(f"   • Debug Mode: {settings.debug}")
    logger.info(f"   • Log Level: {settings.log_level}")
    logger.info(f"   • MongoDB: {settings.mongodb_url}")
    logger.info(f"   • Redis: {settings.redis_url}")
    logger.info("")
    logger.info("⚡ Real-time Features:")
    logger.info("   • Live TOR network monitoring")
    logger.info("   • Real-time traffic correlation")
    logger.info("   • WebSocket updates")
    logger.info("   • AI-enhanced analysis")
    logger.info("   • Geographic visualization")
    logger.info("")
    logger.info("🌐 API Endpoints:")
    logger.info("   • GET  /api/v1/dashboard/stats - Real-time statistics")
    logger.info("   • GET  /api/v1/nodes - TOR network nodes")
    logger.info("   • GET  /api/v1/correlations - Traffic correlations")
    logger.info("   • GET  /api/v1/traffic/flows - Traffic flows")
    logger.info("   • WS   /ws - Real-time WebSocket updates")
    logger.info("")

def check_dependencies():
    """Check if all dependencies are available"""
    try:
        import pymongo
        import redis
        import stem
        import aiohttp
        import pandas
        import numpy
        import sklearn
        logger.info("✅ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        return False

async def main():
    """Main function"""
    try:
        # Print banner
        print("\n" + "=" * 80)
        print("🔍 TOR ANALYSIS SYSTEM - REAL-TIME EDITION")
        print("   Advanced TOR Network Analysis & Correlation System")
        print("   Tamil Nadu Police Hackathon 2025")
        print("=" * 80)
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
            
        # Print system info
        print_system_info()
        
        # Create and start server
        server = TORAnalysisServer()
        server.setup_signal_handlers()
        
        logger.info("🎯 Starting TOR Analysis System...")
        logger.info("💡 Tip: Use Ctrl+C to stop the server gracefully")
        logger.info("")
        
        await server.start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 TOR Analysis System stopped")

if __name__ == "__main__":
    # Check if initialization is needed
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        logger.info("🔧 Running initialization first...")
        os.system("python initialize_realtime_data.py")
        logger.info("✅ Initialization completed, starting server...")
        
    # Start the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass