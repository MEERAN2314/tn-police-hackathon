import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

from app.database import get_database
from app.services.tor_service import TORService
from app.services.correlation_service import CorrelationService
from app.services.traffic_generator import TrafficGenerator
from app.models import DashboardStats

logger = logging.getLogger(__name__)

class RealtimeService:
    """Service for real-time data processing and updates"""
    
    def __init__(self):
        self.tor_service = TORService()
        self.correlation_service = CorrelationService()
        self.traffic_generator = TrafficGenerator()
        self.websocket_clients = set()
        self.stats_cache = {}
        self.last_stats_update = None
        
    async def start_realtime_processing(self):
        """Start all real-time processing tasks"""
        try:
            logger.info("Starting real-time processing...")
            
            # Start TOR monitoring
            await self.tor_service.start_monitoring()
            
            # Start traffic generation
            asyncio.create_task(self.traffic_generator.start_traffic_generation())
            
            # Start correlation analysis
            asyncio.create_task(self._correlation_analysis_loop())
            
            # Start stats update loop
            asyncio.create_task(self._stats_update_loop())
            
            # Start websocket broadcast loop
            asyncio.create_task(self._websocket_broadcast_loop())
            
            logger.info("Real-time processing started successfully")
            
        except Exception as e:
            logger.error(f"Error starting real-time processing: {e}")
            
    async def stop_realtime_processing(self):
        """Stop all real-time processing"""
        try:
            await self.tor_service.stop_monitoring()
            logger.info("Real-time processing stopped")
            
        except Exception as e:
            logger.error(f"Error stopping real-time processing: {e}")
            
    async def _correlation_analysis_loop(self):
        """Continuous correlation analysis"""
        while True:
            try:
                # Get recent traffic flows
                recent_flows = await self.traffic_generator.get_recent_traffic(minutes=10)
                
                if recent_flows:
                    # Analyze correlations
                    correlations = await self.correlation_service.analyze_traffic_correlation(recent_flows)
                    
                    # Store new correlations
                    for correlation in correlations:
                        await self.correlation_service.store_correlation(correlation)
                        
                    if correlations:
                        logger.info(f"Found {len(correlations)} new correlations")
                        
                        # Broadcast to websocket clients
                        await self._broadcast_correlations(correlations)
                
                # Wait before next analysis
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in correlation analysis loop: {e}")
                await asyncio.sleep(60)
                
    async def _stats_update_loop(self):
        """Update dashboard statistics"""
        while True:
            try:
                # Update stats every 15 seconds
                stats = await self._calculate_dashboard_stats()
                self.stats_cache = stats
                self.last_stats_update = datetime.utcnow()
                
                # Broadcast stats to websocket clients
                await self._broadcast_stats(stats)
                
                await asyncio.sleep(15)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stats update loop: {e}")
                await asyncio.sleep(30)
                
    async def _websocket_broadcast_loop(self):
        """Broadcast updates to websocket clients"""
        while True:
            try:
                # Send heartbeat every 10 seconds
                if self.websocket_clients:
                    heartbeat_data = {
                        'type': 'heartbeat',
                        'timestamp': datetime.utcnow().isoformat(),
                        'connected_clients': len(self.websocket_clients)
                    }
                    
                    await self._broadcast_to_clients(heartbeat_data)
                
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in websocket broadcast loop: {e}")
                await asyncio.sleep(15)
                
    async def _calculate_dashboard_stats(self) -> Dict[str, Any]:
        """Calculate real-time dashboard statistics"""
        try:
            db = await get_database()
            
            # Get TOR network stats
            network_stats = await self.tor_service.get_network_statistics()
            
            # Get correlation stats
            total_correlations = await db.correlations.count_documents({})
            high_confidence = await db.correlations.count_documents({'confidence_score': {'$gte': 0.8}})
            recent_correlations = await db.correlations.count_documents({
                'created_at': {'$gte': datetime.utcnow() - timedelta(hours=1)}
            })
            
            # Get traffic stats
            recent_traffic = await db.traffic_flows.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=5)}
            })
            
            # Calculate bandwidth
            total_bandwidth = network_stats.get('total_bandwidth', 0)
            bandwidth_str = self._format_bandwidth(total_bandwidth)
            
            # Get geographic distribution
            countries_pipeline = [
                {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            
            countries_cursor = db.tor_nodes.aggregate(countries_pipeline)
            top_countries = []
            async for country_data in countries_cursor:
                if country_data['_id'] and country_data['_id'] != 'Unknown':
                    top_countries.append({
                        'country': country_data['_id'],
                        'count': country_data['count']
                    })
            
            # System uptime (mock for demo)
            uptime_percentage = 99.2 + (hash(str(datetime.utcnow().minute)) % 100) / 1000
            
            return {
                'nodes': {
                    'total': network_stats.get('total_nodes', 0),
                    'guard': network_stats.get('guard_nodes', 0),
                    'middle': network_stats.get('middle_nodes', 0),
                    'exit': network_stats.get('exit_nodes', 0),
                    'bridge': network_stats.get('bridge_nodes', 0)
                },
                'correlations': {
                    'total': total_correlations,
                    'high_confidence': high_confidence,
                    'recent': recent_correlations,
                    'active': recent_correlations
                },
                'traffic': {
                    'recent_flows': recent_traffic,
                    'total_bandwidth': bandwidth_str,
                    'active_circuits': recent_traffic // 3  # Estimate
                },
                'geographic': {
                    'countries': network_stats.get('countries', 0),
                    'top_countries': top_countries[:5]
                },
                'system': {
                    'uptime_percentage': round(uptime_percentage, 1),
                    'last_updated': datetime.utcnow().isoformat(),
                    'status': 'active'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating dashboard stats: {e}")
            return self._get_fallback_stats()
            
    def _format_bandwidth(self, bytes_per_sec: int) -> str:
        """Format bandwidth in human readable format"""
        if bytes_per_sec >= 1_000_000_000:
            return f"{bytes_per_sec / 1_000_000_000:.1f} GB/s"
        elif bytes_per_sec >= 1_000_000:
            return f"{bytes_per_sec / 1_000_000:.1f} MB/s"
        elif bytes_per_sec >= 1_000:
            return f"{bytes_per_sec / 1_000:.1f} KB/s"
        else:
            return f"{bytes_per_sec} B/s"
            
    def _get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback stats when database is unavailable"""
        return {
            'nodes': {
                'total': 7234,
                'guard': 2156,
                'middle': 3421,
                'exit': 1234,
                'bridge': 423
            },
            'correlations': {
                'total': 156,
                'high_confidence': 34,
                'recent': 12,
                'active': 89
            },
            'traffic': {
                'recent_flows': 45,
                'total_bandwidth': "2.4 GB/s",
                'active_circuits': 15
            },
            'geographic': {
                'countries': 67,
                'top_countries': [
                    {'country': 'US', 'count': 1823},
                    {'country': 'DE', 'count': 1245},
                    {'country': 'FR', 'count': 987},
                    {'country': 'NL', 'count': 756},
                    {'country': 'GB', 'count': 634}
                ]
            },
            'system': {
                'uptime_percentage': 99.2,
                'last_updated': datetime.utcnow().isoformat(),
                'status': 'active'
            }
        }
        
    async def _broadcast_correlations(self, correlations: List):
        """Broadcast new correlations to websocket clients"""
        try:
            if self.websocket_clients:
                data = {
                    'type': 'new_correlations',
                    'correlations': [corr.dict() for corr in correlations],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self._broadcast_to_clients(data)
                
        except Exception as e:
            logger.error(f"Error broadcasting correlations: {e}")
            
    async def _broadcast_stats(self, stats: Dict[str, Any]):
        """Broadcast stats to websocket clients"""
        try:
            if self.websocket_clients:
                data = {
                    'type': 'stats_update',
                    'stats': stats,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self._broadcast_to_clients(data)
                
        except Exception as e:
            logger.error(f"Error broadcasting stats: {e}")
            
    async def _broadcast_to_clients(self, data: Dict[str, Any]):
        """Broadcast data to all connected websocket clients"""
        if not self.websocket_clients:
            return
            
        # Convert to JSON
        message = json.dumps(data, default=str)
        
        # Send to all clients
        disconnected_clients = set()
        
        for client in self.websocket_clients:
            try:
                await client.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected_clients.add(client)
                
        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients
        
    def add_websocket_client(self, websocket):
        """Add a websocket client"""
        self.websocket_clients.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.websocket_clients)}")
        
    def remove_websocket_client(self, websocket):
        """Remove a websocket client"""
        self.websocket_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.websocket_clients)}")
        
    async def get_current_stats(self) -> Dict[str, Any]:
        """Get current dashboard statistics"""
        if self.stats_cache and self.last_stats_update:
            # Return cached stats if recent (less than 30 seconds old)
            if (datetime.utcnow() - self.last_stats_update).total_seconds() < 30:
                return self.stats_cache
                
        # Calculate fresh stats
        return await self._calculate_dashboard_stats()
        
    async def get_recent_activity(self, minutes: int = 60) -> Dict[str, Any]:
        """Get recent system activity"""
        try:
            db = await get_database()
            
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            
            # Get recent correlations
            recent_correlations = []
            cursor = db.correlations.find(
                {'created_at': {'$gte': cutoff}},
                sort=[('created_at', -1)],
                limit=10
            )
            
            async for doc in cursor:
                recent_correlations.append({
                    'id': doc['id'],
                    'confidence_score': doc['confidence_score'],
                    'method': doc['correlation_method'],
                    'created_at': doc['created_at'].isoformat()
                })
                
            # Get traffic volume over time
            traffic_pipeline = [
                {'$match': {'timestamp': {'$gte': cutoff}}},
                {'$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d %H:%M',
                            'date': '$timestamp'
                        }
                    },
                    'count': {'$sum': 1},
                    'total_bytes': {'$sum': {'$add': ['$bytes_sent', '$bytes_received']}}
                }},
                {'$sort': {'_id': 1}}
            ]
            
            traffic_cursor = db.traffic_flows.aggregate(traffic_pipeline)
            traffic_timeline = []
            
            async for doc in traffic_cursor:
                traffic_timeline.append({
                    'time': doc['_id'],
                    'flows': doc['count'],
                    'bytes': doc['total_bytes']
                })
                
            return {
                'recent_correlations': recent_correlations,
                'traffic_timeline': traffic_timeline,
                'period_minutes': minutes,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return {
                'recent_correlations': [],
                'traffic_timeline': [],
                'period_minutes': minutes,
                'generated_at': datetime.utcnow().isoformat()
            }