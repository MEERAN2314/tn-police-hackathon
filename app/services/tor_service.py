import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import stem
from stem import CircStatus
from stem.control import Controller

from app.config import settings
from app.models import TORNode, NodeType, NetworkTopology
from app.database import get_database

logger = logging.getLogger(__name__)

class TORService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.controller: Optional[Controller] = None
        self.nodes_cache = {}
        self.last_update = None
        
    async def start_monitoring(self):
        """Start TOR network monitoring"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Start periodic data collection
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Try to connect to TOR controller
            await self._connect_tor_controller()
            
            logger.info("TOR monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start TOR monitoring: {e}")
            
    async def stop_monitoring(self):
        """Stop TOR network monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        if self.session:
            await self.session.close()
            
        if self.controller:
            self.controller.close()
            
        logger.info("TOR monitoring stopped")
        
    async def _connect_tor_controller(self):
        """Connect to TOR controller for real-time data"""
        try:
            self.controller = Controller.from_port(port=settings.tor_control_port)
            self.controller.authenticate()
            logger.info("Connected to TOR controller")
        except Exception as e:
            logger.warning(f"Could not connect to TOR controller: {e}")
            
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self.collect_tor_data()
                await asyncio.sleep(settings.tor_data_refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
                
    async def collect_tor_data(self):
        """Collect TOR network data from various sources"""
        try:
            # Collect from Onionoo API
            await self._collect_onionoo_data()
            
            # Collect from TOR Metrics API
            await self._collect_metrics_data()
            
            # Update network topology
            await self._update_network_topology()
            
            self.last_update = datetime.utcnow()
            logger.info("TOR data collection completed")
            
        except Exception as e:
            logger.error(f"Error collecting TOR data: {e}")
            
    async def _collect_onionoo_data(self):
        """Collect data from Onionoo API"""
        try:
            url = f"{settings.onionoo_api}/details"
            params = {
                'type': 'relay',
                'running': 'true',
                'fields': 'nickname,fingerprint,or_addresses,dir_address,country,country_name,region_name,city_name,latitude,longitude,bandwidth,observed_bandwidth,consensus_weight,flags,first_seen,last_seen,contact,platform,version'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._process_relay_data(data.get('relays', []))
                else:
                    logger.error(f"Onionoo API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error collecting Onionoo data: {e}")
            
    async def _collect_metrics_data(self):
        """Collect data from TOR Metrics API"""
        try:
            # Collect bandwidth data
            url = f"{settings.tor_metrics_api}/bandwidth.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Process bandwidth data
                    
        except Exception as e:
            logger.error(f"Error collecting metrics data: {e}")
            
    async def _process_relay_data(self, relays: List[Dict]):
        """Process relay data and store in database"""
        try:
            db = await get_database()
            processed_nodes = []
            
            for relay in relays:
                try:
                    # Determine node type based on flags
                    node_type = self._determine_node_type(relay.get('flags', []))
                    
                    # Parse OR addresses
                    or_addresses = relay.get('or_addresses', [])
                    if not or_addresses:
                        continue
                        
                    address_parts = or_addresses[0].split(':')
                    address = address_parts[0]
                    or_port = int(address_parts[1]) if len(address_parts) > 1 else 9001
                    
                    # Create TOR node object
                    node = TORNode(
                        fingerprint=relay['fingerprint'],
                        nickname=relay.get('nickname', 'Unknown'),
                        address=address,
                        or_port=or_port,
                        dir_port=None,
                        country=relay.get('country', 'Unknown'),
                        country_name=relay.get('country_name', 'Unknown'),
                        region_name=relay.get('region_name'),
                        city_name=relay.get('city_name'),
                        latitude=relay.get('latitude'),
                        longitude=relay.get('longitude'),
                        bandwidth=relay.get('bandwidth', 0),
                        observed_bandwidth=relay.get('observed_bandwidth', 0),
                        consensus_weight=relay.get('consensus_weight', 0),
                        flags=relay.get('flags', []),
                        type=node_type,
                        first_seen=datetime.fromisoformat(relay['first_seen'].replace('Z', '+00:00')),
                        last_seen=datetime.fromisoformat(relay['last_seen'].replace('Z', '+00:00')),
                        contact=relay.get('contact'),
                        platform=relay.get('platform'),
                        version=relay.get('version')
                    )
                    
                    processed_nodes.append(node.dict())
                    
                except Exception as e:
                    logger.warning(f"Error processing relay {relay.get('fingerprint', 'unknown')}: {e}")
                    continue
                    
            # Bulk upsert to database
            if processed_nodes:
                operations = []
                for node in processed_nodes:
                    operations.append({
                        'updateOne': {
                            'filter': {'fingerprint': node['fingerprint']},
                            'update': {'$set': node},
                            'upsert': True
                        }
                    })
                
                await db.tor_nodes.bulk_write(operations)
                logger.info(f"Processed {len(processed_nodes)} TOR nodes")
                
        except Exception as e:
            logger.error(f"Error processing relay data: {e}")
            
    def _determine_node_type(self, flags: List[str]) -> NodeType:
        """Determine node type based on flags"""
        if 'Guard' in flags:
            return NodeType.GUARD
        elif 'Exit' in flags:
            return NodeType.EXIT
        elif 'Bridge' in flags:
            return NodeType.BRIDGE
        else:
            return NodeType.MIDDLE
            
    async def _update_network_topology(self):
        """Update network topology statistics"""
        try:
            db = await get_database()
            
            # Count nodes by type
            pipeline = [
                {'$group': {
                    '_id': '$type',
                    'count': {'$sum': 1},
                    'total_bandwidth': {'$sum': '$bandwidth'},
                    'total_consensus_weight': {'$sum': '$consensus_weight'}
                }}
            ]
            
            results = await db.tor_nodes.aggregate(pipeline).to_list(None)
            
            # Count unique countries
            countries = await db.tor_nodes.distinct('country')
            
            # Calculate totals
            total_nodes = sum(r['count'] for r in results)
            total_bandwidth = sum(r['total_bandwidth'] for r in results)
            total_consensus_weight = sum(r['total_consensus_weight'] for r in results)
            
            # Count by type
            type_counts = {r['_id']: r['count'] for r in results}
            
            topology = NetworkTopology(
                total_nodes=total_nodes,
                guard_nodes=type_counts.get('guard', 0),
                middle_nodes=type_counts.get('middle', 0),
                exit_nodes=type_counts.get('exit', 0),
                bridge_nodes=type_counts.get('bridge', 0),
                countries=countries,
                total_bandwidth=total_bandwidth,
                consensus_weight=total_consensus_weight
            )
            
            # Store topology data
            await db.network_topology.insert_one(topology.dict())
            
            # Keep only last 24 hours of topology data
            cutoff = datetime.utcnow() - timedelta(hours=24)
            await db.network_topology.delete_many({'timestamp': {'$lt': cutoff}})
            
        except Exception as e:
            logger.error(f"Error updating network topology: {e}")
            
    async def get_nodes_by_country(self, country: str) -> List[TORNode]:
        """Get TOR nodes by country"""
        try:
            db = await get_database()
            cursor = db.tor_nodes.find({'country': country})
            nodes = []
            
            async for doc in cursor:
                nodes.append(TORNode(**doc))
                
            return nodes
            
        except Exception as e:
            logger.error(f"Error getting nodes by country: {e}")
            return []
            
    async def get_network_statistics(self) -> Dict:
        """Get current network statistics"""
        try:
            db = await get_database()
            
            # Get latest topology
            topology = await db.network_topology.find_one(
                {},
                sort=[('timestamp', -1)]
            )
            
            if not topology:
                return {}
                
            return {
                'total_nodes': topology['total_nodes'],
                'guard_nodes': topology['guard_nodes'],
                'middle_nodes': topology['middle_nodes'],
                'exit_nodes': topology['exit_nodes'],
                'bridge_nodes': topology['bridge_nodes'],
                'countries': len(topology['countries']),
                'total_bandwidth': topology['total_bandwidth'],
                'last_updated': topology['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error getting network statistics: {e}")
            return {}
            
    async def search_nodes(self, query: str, limit: int = 50) -> List[TORNode]:
        """Search TOR nodes by various criteria"""
        try:
            db = await get_database()
            
            # Create search filter
            search_filter = {
                '$or': [
                    {'nickname': {'$regex': query, '$options': 'i'}},
                    {'fingerprint': {'$regex': query, '$options': 'i'}},
                    {'address': {'$regex': query, '$options': 'i'}},
                    {'country_name': {'$regex': query, '$options': 'i'}},
                    {'city_name': {'$regex': query, '$options': 'i'}}
                ]
            }
            
            cursor = db.tor_nodes.find(search_filter).limit(limit)
            nodes = []
            
            async for doc in cursor:
                nodes.append(TORNode(**doc))
                
            return nodes
            
        except Exception as e:
            logger.error(f"Error searching nodes: {e}")
            return []