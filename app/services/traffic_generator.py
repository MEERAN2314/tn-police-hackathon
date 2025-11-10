import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import ipaddress
import time

from app.models import TrafficFlow
from app.database import get_database

logger = logging.getLogger(__name__)

class TrafficGenerator:
    """Generate realistic TOR traffic flows for analysis"""
    
    def __init__(self):
        self.active_circuits = {}
        self.traffic_patterns = {
            'web_browsing': {'min_bytes': 1000, 'max_bytes': 50000, 'duration_range': (5, 300)},
            'file_download': {'min_bytes': 100000, 'max_bytes': 10000000, 'duration_range': (30, 1800)},
            'messaging': {'min_bytes': 100, 'max_bytes': 5000, 'duration_range': (1, 60)},
            'streaming': {'min_bytes': 500000, 'max_bytes': 5000000, 'duration_range': (300, 3600)}
        }
        
    async def start_traffic_generation(self):
        """Start generating realistic traffic flows"""
        try:
            logger.info("Starting traffic generation...")
            
            # Start multiple traffic generation tasks
            tasks = [
                asyncio.create_task(self._generate_web_traffic()),
                asyncio.create_task(self._generate_file_traffic()),
                asyncio.create_task(self._generate_messaging_traffic()),
                asyncio.create_task(self._generate_streaming_traffic())
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in traffic generation: {e}")
            
    async def _generate_web_traffic(self):
        """Generate web browsing traffic patterns"""
        while True:
            try:
                # Generate 5-15 web flows every 30-60 seconds
                num_flows = random.randint(5, 15)
                
                for _ in range(num_flows):
                    flow = await self._create_traffic_flow('web_browsing')
                    await self._store_traffic_flow(flow)
                    
                await asyncio.sleep(random.randint(30, 60))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error generating web traffic: {e}")
                await asyncio.sleep(10)
                
    async def _generate_file_traffic(self):
        """Generate file download traffic patterns"""
        while True:
            try:
                # Generate 1-3 file flows every 2-5 minutes
                num_flows = random.randint(1, 3)
                
                for _ in range(num_flows):
                    flow = await self._create_traffic_flow('file_download')
                    await self._store_traffic_flow(flow)
                    
                await asyncio.sleep(random.randint(120, 300))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error generating file traffic: {e}")
                await asyncio.sleep(30)
                
    async def _generate_messaging_traffic(self):
        """Generate messaging traffic patterns"""
        while True:
            try:
                # Generate 10-30 message flows every 1-3 minutes
                num_flows = random.randint(10, 30)
                
                for _ in range(num_flows):
                    flow = await self._create_traffic_flow('messaging')
                    await self._store_traffic_flow(flow)
                    
                await asyncio.sleep(random.randint(60, 180))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error generating messaging traffic: {e}")
                await asyncio.sleep(15)
                
    async def _generate_streaming_traffic(self):
        """Generate streaming traffic patterns"""
        while True:
            try:
                # Generate 1-2 streaming flows every 5-10 minutes
                num_flows = random.randint(1, 2)
                
                for _ in range(num_flows):
                    flow = await self._create_traffic_flow('streaming')
                    await self._store_traffic_flow(flow)
                    
                await asyncio.sleep(random.randint(300, 600))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error generating streaming traffic: {e}")
                await asyncio.sleep(60)
                
    async def _create_traffic_flow(self, traffic_type: str) -> TrafficFlow:
        """Create a realistic traffic flow"""
        try:
            pattern = self.traffic_patterns[traffic_type]
            
            # Get random TOR nodes for entry and exit
            entry_node, exit_node = await self._get_random_tor_nodes()
            
            # Generate realistic IPs
            source_ip = self._generate_realistic_ip('source')
            destination_ip = self._generate_realistic_ip('destination')
            
            # Generate traffic characteristics
            bytes_sent = random.randint(pattern['min_bytes'] // 10, pattern['min_bytes'])
            bytes_received = random.randint(pattern['min_bytes'], pattern['max_bytes'])
            duration = random.randint(*pattern['duration_range'])
            
            # Generate ports
            source_port = random.randint(32768, 65535)  # Ephemeral port range
            destination_port = self._get_realistic_destination_port(traffic_type)
            
            # Create flow with realistic timing
            base_time = datetime.utcnow()
            entry_time = base_time - timedelta(seconds=random.uniform(0, 2))
            exit_time = base_time + timedelta(seconds=random.uniform(2, 6))  # TOR circuit build time
            
            flow = TrafficFlow(
                id=f"flow_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}",
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_port=source_port,
                destination_port=destination_port,
                protocol="TCP",
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                duration=duration,
                timestamp=entry_time,
                entry_node=entry_node,
                exit_node=exit_node,
                traffic_type=traffic_type,
                metadata={
                    'entry_timestamp': entry_time.isoformat(),
                    'exit_timestamp': exit_time.isoformat(),
                    'circuit_build_time': (exit_time - entry_time).total_seconds(),
                    'user_agent': self._get_realistic_user_agent(),
                    'tls_version': random.choice(['TLSv1.2', 'TLSv1.3']),
                    'cipher_suite': random.choice([
                        'TLS_AES_256_GCM_SHA384',
                        'TLS_CHACHA20_POLY1305_SHA256',
                        'TLS_AES_128_GCM_SHA256'
                    ])
                }
            )
            
            return flow
            
        except Exception as e:
            logger.error(f"Error creating traffic flow: {e}")
            raise
            
    async def _get_random_tor_nodes(self) -> tuple:
        """Get random TOR entry and exit nodes"""
        try:
            db = await get_database()
            
            # Get guard nodes for entry
            guard_nodes = await db.tor_nodes.find({'type': 'guard'}).to_list(100)
            if not guard_nodes:
                # Fallback to any nodes with Guard flag
                guard_nodes = await db.tor_nodes.find({'flags': 'Guard'}).to_list(100)
                
            # Get exit nodes
            exit_nodes = await db.tor_nodes.find({'type': 'exit'}).to_list(100)
            if not exit_nodes:
                # Fallback to any nodes with Exit flag
                exit_nodes = await db.tor_nodes.find({'flags': 'Exit'}).to_list(100)
                
            # Select random nodes
            entry_node = random.choice(guard_nodes)['fingerprint'] if guard_nodes else self._generate_fingerprint()
            exit_node = random.choice(exit_nodes)['fingerprint'] if exit_nodes else self._generate_fingerprint()
            
            return entry_node, exit_node
            
        except Exception as e:
            logger.error(f"Error getting TOR nodes: {e}")
            # Return generated fingerprints as fallback
            return self._generate_fingerprint(), self._generate_fingerprint()
            
    def _generate_realistic_ip(self, ip_type: str) -> str:
        """Generate realistic IP addresses"""
        if ip_type == 'source':
            # Common residential/corporate IP ranges
            ranges = [
                '192.168.0.0/16',    # Private
                '10.0.0.0/8',        # Private
                '172.16.0.0/12',     # Private
                '203.0.113.0/24',    # Documentation
                '198.51.100.0/24',   # Documentation
            ]
        else:  # destination
            # Common server/service IP ranges
            ranges = [
                '8.8.8.0/24',        # Google DNS area
                '1.1.1.0/24',        # Cloudflare area
                '151.101.0.0/16',    # Reddit/Fastly
                '104.16.0.0/12',     # Cloudflare
                '185.199.108.0/22',  # GitHub Pages
            ]
            
        network = ipaddress.IPv4Network(random.choice(ranges))
        return str(network.network_address + random.randint(1, network.num_addresses - 2))
        
    def _get_realistic_destination_port(self, traffic_type: str) -> int:
        """Get realistic destination ports based on traffic type"""
        port_mappings = {
            'web_browsing': [80, 443, 8080, 8443],
            'file_download': [80, 443, 21, 22, 993, 995],
            'messaging': [443, 993, 995, 587, 25],
            'streaming': [443, 80, 1935, 8080]
        }
        
        return random.choice(port_mappings.get(traffic_type, [443, 80]))
        
    def _get_realistic_user_agent(self) -> str:
        """Generate realistic user agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        return random.choice(user_agents)
        
    def _generate_fingerprint(self) -> str:
        """Generate a TOR fingerprint"""
        import secrets
        return ''.join(secrets.choice('0123456789ABCDEF') for _ in range(40))
        
    async def _store_traffic_flow(self, flow: TrafficFlow):
        """Store traffic flow in database"""
        try:
            db = await get_database()
            await db.traffic_flows.insert_one(flow.dict())
            
            # Keep only last 24 hours of traffic data
            cutoff = datetime.utcnow() - timedelta(hours=24)
            await db.traffic_flows.delete_many({'timestamp': {'$lt': cutoff}})
            
        except Exception as e:
            logger.error(f"Error storing traffic flow: {e}")
            
    async def get_recent_traffic(self, minutes: int = 60) -> List[TrafficFlow]:
        """Get recent traffic flows"""
        try:
            db = await get_database()
            
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            cursor = db.traffic_flows.find(
                {'timestamp': {'$gte': cutoff}},
                sort=[('timestamp', -1)]
            )
            
            flows = []
            async for doc in cursor:
                flows.append(TrafficFlow(**doc))
                
            return flows
            
        except Exception as e:
            logger.error(f"Error getting recent traffic: {e}")
            return []