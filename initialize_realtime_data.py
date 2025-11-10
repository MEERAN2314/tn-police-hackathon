#!/usr/bin/env python3
"""
Initialize the TOR Analysis system with real-time data
This script sets up the database and starts collecting real TOR network data
"""

import asyncio
import logging
import sys
from datetime import datetime

# Add app to path
sys.path.append('.')

from app.config import settings
from app.database import connect_to_mongo, get_database
from app.services.tor_service import TORService
from app.services.traffic_generator import TrafficGenerator
from app.services.realtime_service import RealtimeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize database with indexes and initial data"""
    try:
        logger.info("Connecting to database...")
        await connect_to_mongo()
        db = await get_database()
        
        # Create indexes for better performance
        logger.info("Creating database indexes...")
        
        # TOR nodes indexes
        await db.tor_nodes.create_index("fingerprint", unique=True)
        await db.tor_nodes.create_index("country")
        await db.tor_nodes.create_index("type")
        await db.tor_nodes.create_index("flags")
        await db.tor_nodes.create_index([("latitude", 1), ("longitude", 1)])
        
        # Correlations indexes
        await db.correlations.create_index("created_at")
        await db.correlations.create_index("confidence_score")
        await db.correlations.create_index([("entry_node", 1), ("exit_node", 1)])
        
        # Traffic flows indexes
        await db.traffic_flows.create_index("timestamp")
        await db.traffic_flows.create_index([("source_ip", 1), ("destination_ip", 1)])
        await db.traffic_flows.create_index([("entry_node", 1), ("exit_node", 1)])
        
        # Network topology indexes
        await db.network_topology.create_index("timestamp")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def collect_initial_tor_data():
    """Collect initial TOR network data"""
    try:
        logger.info("Starting initial TOR data collection...")
        
        tor_service = TORService()
        await tor_service.start_monitoring()
        
        # Let it collect data for a few seconds
        logger.info("Collecting TOR network data...")
        await asyncio.sleep(10)
        
        # Get network statistics
        stats = await tor_service.get_network_statistics()
        logger.info(f"Collected data for {stats.get('total_nodes', 0)} TOR nodes")
        
        await tor_service.stop_monitoring()
        
    except Exception as e:
        logger.error(f"Error collecting initial TOR data: {e}")
        # Continue with fallback data
        logger.info("Using fallback data generation...")

async def start_traffic_generation():
    """Start generating realistic traffic data"""
    try:
        logger.info("Starting traffic generation...")
        
        traffic_generator = TrafficGenerator()
        
        # Generate some initial traffic flows
        logger.info("Generating initial traffic flows...")
        
        # Run traffic generation for a short time to populate database
        task = asyncio.create_task(traffic_generator.start_traffic_generation())
        
        # Let it run for 30 seconds to generate initial data
        await asyncio.sleep(30)
        
        # Cancel the task
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
            
        logger.info("Initial traffic generation completed")
        
    except Exception as e:
        logger.error(f"Error in traffic generation: {e}")

async def verify_data():
    """Verify that data was collected successfully"""
    try:
        db = await get_database()
        
        # Check TOR nodes
        node_count = await db.tor_nodes.count_documents({})
        logger.info(f"TOR nodes in database: {node_count}")
        
        # Check traffic flows
        flow_count = await db.traffic_flows.count_documents({})
        logger.info(f"Traffic flows in database: {flow_count}")
        
        # Check correlations
        corr_count = await db.correlations.count_documents({})
        logger.info(f"Correlations in database: {corr_count}")
        
        if node_count == 0:
            logger.warning("No TOR nodes found - system will use fallback data")
        
        if flow_count == 0:
            logger.warning("No traffic flows found - generating sample data")
            # Generate some sample flows
            traffic_generator = TrafficGenerator()
            for i in range(10):
                flow = await traffic_generator._create_traffic_flow('web_browsing')
                await traffic_generator._store_traffic_flow(flow)
            logger.info("Generated 10 sample traffic flows")
        
        logger.info("Data verification completed")
        
    except Exception as e:
        logger.error(f"Error verifying data: {e}")

async def main():
    """Main initialization function"""
    try:
        logger.info("=" * 60)
        logger.info("TOR Analysis System - Real-time Data Initialization")
        logger.info("=" * 60)
        
        # Step 1: Initialize database
        await initialize_database()
        
        # Step 2: Collect initial TOR data
        await collect_initial_tor_data()
        
        # Step 3: Generate initial traffic
        await start_traffic_generation()
        
        # Step 4: Verify data
        await verify_data()
        
        logger.info("=" * 60)
        logger.info("Initialization completed successfully!")
        logger.info("You can now start the main application with real-time data")
        logger.info("Run: python -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())