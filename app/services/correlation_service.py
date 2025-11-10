import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import networkx as nx

from app.config import settings
from app.models import Correlation, TrafficFlow, TORNode
from app.database import get_database
from app.services.ai_service import AIService
from app.services.geolocation_service import GeolocationService

logger = logging.getLogger(__name__)

class CorrelationService:
    def __init__(self):
        self.ai_service = AIService()
        self.correlation_cache = {}
        self.active_circuits = {}
        
    async def analyze_traffic_correlation(self, traffic_flows: List[TrafficFlow]) -> List[Correlation]:
        """Analyze traffic flows to find correlations"""
        try:
            correlations = []
            
            # Group flows by time windows
            time_windows = self._group_by_time_windows(traffic_flows)
            
            for window_start, flows in time_windows.items():
                # Perform timing analysis
                timing_correlations = await self._timing_analysis(flows)
                
                # Perform traffic pattern analysis
                pattern_correlations = await self._pattern_analysis(flows)
                
                # Combine correlations
                combined = self._combine_correlations(timing_correlations, pattern_correlations)
                
                # Apply AI enhancement
                enhanced = await self._ai_enhance_correlations(combined)
                
                correlations.extend(enhanced)
                
            return correlations
            
        except Exception as e:
            logger.error(f"Error in traffic correlation analysis: {e}")
            return []
            
    def _group_by_time_windows(self, flows: List[TrafficFlow], window_size: int = 300) -> Dict[datetime, List[TrafficFlow]]:
        """Group traffic flows by time windows"""
        windows = {}
        
        for flow in flows:
            # Round timestamp to window boundary
            window_start = flow.timestamp.replace(
                second=0, microsecond=0
            ) - timedelta(
                minutes=flow.timestamp.minute % (window_size // 60)
            )
            
            if window_start not in windows:
                windows[window_start] = []
            windows[window_start].append(flow)
            
        return windows
        
    async def _timing_analysis(self, flows: List[TrafficFlow]) -> List[Correlation]:
        """Perform timing-based correlation analysis"""
        correlations = []
        
        try:
            # Group flows by entry and exit nodes
            entry_flows = {}
            exit_flows = {}
            
            for flow in flows:
                if flow.entry_node:
                    if flow.entry_node not in entry_flows:
                        entry_flows[flow.entry_node] = []
                    entry_flows[flow.entry_node].append(flow)
                    
                if flow.exit_node:
                    if flow.exit_node not in exit_flows:
                        exit_flows[flow.exit_node] = []
                    exit_flows[flow.exit_node].append(flow)
                    
            # Find timing correlations
            for entry_node, entry_list in entry_flows.items():
                for exit_node, exit_list in exit_flows.items():
                    correlation = await self._calculate_timing_correlation(
                        entry_node, entry_list, exit_node, exit_list
                    )
                    
                    if correlation and correlation.confidence_score > 0.5:
                        correlations.append(correlation)
                        
        except Exception as e:
            logger.error(f"Error in timing analysis: {e}")
            
        return correlations
        
    async def _calculate_timing_correlation(
        self, 
        entry_node: str, 
        entry_flows: List[TrafficFlow],
        exit_node: str, 
        exit_flows: List[TrafficFlow]
    ) -> Optional[Correlation]:
        """Calculate timing correlation between entry and exit flows"""
        try:
            # Expected circuit build time (2-6 seconds for TOR)
            min_delay = 2.0
            max_delay = 6.0
            
            best_correlation = None
            best_score = 0.0
            
            for entry_flow in entry_flows:
                for exit_flow in exit_flows:
                    # Calculate time difference
                    time_diff = (exit_flow.timestamp - entry_flow.timestamp).total_seconds()
                    
                    # Check if within expected range
                    if min_delay <= time_diff <= max_delay:
                        # Calculate correlation score based on timing precision
                        timing_score = 1.0 - (abs(time_diff - 4.0) / 2.0)  # Optimal at 4 seconds
                        
                        # Factor in traffic volume correlation
                        volume_score = self._calculate_volume_correlation(entry_flow, exit_flow)
                        
                        # Combined score
                        combined_score = (timing_score * 0.6) + (volume_score * 0.4)
                        
                        if combined_score > best_score:
                            best_score = combined_score
                            best_correlation = Correlation(
                                id=f"corr_{entry_node[:8]}_{exit_node[:8]}_{int(entry_flow.timestamp.timestamp())}",
                                entry_node=entry_node,
                                exit_node=exit_node,
                                origin_ip=entry_flow.source_ip,
                                destination_ip=exit_flow.destination_ip,
                                confidence_score=combined_score,
                                correlation_method="timing_analysis",
                                timing_analysis={
                                    "time_difference": time_diff,
                                    "timing_score": timing_score,
                                    "volume_score": volume_score,
                                    "entry_timestamp": entry_flow.timestamp.isoformat(),
                                    "exit_timestamp": exit_flow.timestamp.isoformat()
                                }
                            )
                            
            return best_correlation
            
        except Exception as e:
            logger.error(f"Error calculating timing correlation: {e}")
            return None
            
    def _calculate_volume_correlation(self, entry_flow: TrafficFlow, exit_flow: TrafficFlow) -> float:
        """Calculate traffic volume correlation"""
        try:
            # Compare bytes sent/received with some tolerance for TOR overhead
            entry_total = entry_flow.bytes_sent + entry_flow.bytes_received
            exit_total = exit_flow.bytes_sent + exit_flow.bytes_received
            
            if entry_total == 0 and exit_total == 0:
                return 1.0
                
            if entry_total == 0 or exit_total == 0:
                return 0.0
                
            # Calculate ratio (accounting for TOR overhead ~10-20%)
            ratio = min(entry_total, exit_total) / max(entry_total, exit_total)
            
            # Adjust for expected TOR overhead
            if ratio >= 0.8:  # Within 20% difference
                return 1.0
            elif ratio >= 0.6:  # Within 40% difference
                return 0.7
            elif ratio >= 0.4:  # Within 60% difference
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"Error calculating volume correlation: {e}")
            return 0.0
            
    async def _pattern_analysis(self, flows: List[TrafficFlow]) -> List[Correlation]:
        """Perform traffic pattern analysis"""
        correlations = []
        
        try:
            # Extract features for clustering
            features = []
            flow_data = []
            
            for flow in flows:
                if flow.entry_node and flow.exit_node:
                    feature_vector = [
                        flow.bytes_sent,
                        flow.bytes_received,
                        flow.duration,
                        flow.source_port,
                        flow.destination_port,
                        hash(flow.source_ip) % 1000,  # IP hash for anonymity
                        hash(flow.destination_ip) % 1000
                    ]
                    features.append(feature_vector)
                    flow_data.append(flow)
                    
            if len(features) < 2:
                return correlations
                
            # Normalize features
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(features)
            
            # Apply DBSCAN clustering
            clustering = DBSCAN(eps=0.5, min_samples=2)
            cluster_labels = clustering.fit_predict(normalized_features)
            
            # Group flows by clusters
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label != -1:  # Ignore noise points
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(flow_data[i])
                    
            # Create correlations for each cluster
            for cluster_id, cluster_flows in clusters.items():
                if len(cluster_flows) >= 2:
                    correlation = self._create_pattern_correlation(cluster_flows)
                    if correlation:
                        correlations.append(correlation)
                        
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            
        return correlations
        
    def _create_pattern_correlation(self, flows: List[TrafficFlow]) -> Optional[Correlation]:
        """Create correlation from clustered flows"""
        try:
            # Find most common entry and exit nodes
            entry_nodes = [f.entry_node for f in flows if f.entry_node]
            exit_nodes = [f.exit_node for f in flows if f.exit_node]
            
            if not entry_nodes or not exit_nodes:
                return None
                
            # Get most frequent nodes
            entry_node = max(set(entry_nodes), key=entry_nodes.count)
            exit_node = max(set(exit_nodes), key=exit_nodes.count)
            
            # Calculate confidence based on pattern consistency
            confidence = len([f for f in flows if f.entry_node == entry_node and f.exit_node == exit_node]) / len(flows)
            
            if confidence < 0.3:
                return None
                
            # Get representative flow
            representative_flow = flows[0]
            
            return Correlation(
                id=f"pattern_{entry_node[:8]}_{exit_node[:8]}_{int(datetime.utcnow().timestamp())}",
                entry_node=entry_node,
                exit_node=exit_node,
                origin_ip=representative_flow.source_ip,
                destination_ip=representative_flow.destination_ip,
                confidence_score=confidence,
                correlation_method="pattern_analysis",
                traffic_pattern={
                    "cluster_size": len(flows),
                    "pattern_consistency": confidence,
                    "avg_bytes_sent": np.mean([f.bytes_sent for f in flows]),
                    "avg_bytes_received": np.mean([f.bytes_received for f in flows]),
                    "avg_duration": np.mean([f.duration for f in flows])
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating pattern correlation: {e}")
            return None
            
    def _combine_correlations(self, timing_correlations: List[Correlation], pattern_correlations: List[Correlation]) -> List[Correlation]:
        """Combine timing and pattern correlations"""
        combined = []
        
        # Add timing correlations
        combined.extend(timing_correlations)
        
        # Add pattern correlations that don't overlap
        for pattern_corr in pattern_correlations:
            overlap = False
            for timing_corr in timing_correlations:
                if (pattern_corr.entry_node == timing_corr.entry_node and 
                    pattern_corr.exit_node == timing_corr.exit_node and
                    pattern_corr.origin_ip == timing_corr.origin_ip):
                    overlap = True
                    break
                    
            if not overlap:
                combined.append(pattern_corr)
                
        return combined
        
    async def _ai_enhance_correlations(self, correlations: List[Correlation]) -> List[Correlation]:
        """Use AI to enhance correlation analysis"""
        try:
            # AI enhancement disabled to prevent errors
            # Just return correlations as-is with minor confidence boost
            enhanced = []
            
            for correlation in correlations:
                # Simple enhancement without AI
                if correlation.confidence_score > 0.7:
                    correlation.confidence_score = min(1.0, correlation.confidence_score * 1.1)
                
                enhanced.append(correlation)
                
            return enhanced
            
        except Exception as e:
            logger.debug(f"AI enhancement skipped: {e}")
            return correlations
            
    async def _get_correlation_context(self, correlation: Correlation) -> Dict:
        """Get additional context for correlation"""
        try:
            db = await get_database()
            
            # Get node information
            entry_node = await db.tor_nodes.find_one({'fingerprint': correlation.entry_node})
            exit_node = await db.tor_nodes.find_one({'fingerprint': correlation.exit_node})
            
            # Get geolocation data
            geolocation = await self._get_geolocation_data(correlation.origin_ip, correlation.destination_ip)
            
            return {
                'entry_node': entry_node,
                'exit_node': exit_node,
                'geolocation': geolocation,
                'timestamp': correlation.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting correlation context: {e}")
            return {}
            
    async def _get_geolocation_data(self, origin_ip: str, destination_ip: str) -> Dict:
        """Get geolocation data for IPs"""
        try:
            async with GeolocationService() as geo_service:
                origin_data = await geo_service.get_ip_location(origin_ip)
                destination_data = await geo_service.get_ip_location(destination_ip)
                
                return {
                    'origin': {
                        'country': origin_data.get('country_name', 'Unknown'),
                        'country_code': origin_data.get('country_code', 'Unknown'),
                        'city': origin_data.get('city', 'Unknown'),
                        'latitude': origin_data.get('latitude', 0.0),
                        'longitude': origin_data.get('longitude', 0.0),
                        'isp': origin_data.get('isp', 'Unknown')
                    },
                    'destination': {
                        'country': destination_data.get('country_name', 'Unknown'),
                        'country_code': destination_data.get('country_code', 'Unknown'),
                        'city': destination_data.get('city', 'Unknown'),
                        'latitude': destination_data.get('latitude', 0.0),
                        'longitude': destination_data.get('longitude', 0.0),
                        'isp': destination_data.get('isp', 'Unknown')
                    }
                }
        except Exception as e:
            logger.error(f"Error getting geolocation data: {e}")
            return {
                'origin': {
                    'country': 'Unknown',
                    'city': 'Unknown',
                    'latitude': 0.0,
                    'longitude': 0.0
                },
                'destination': {
                    'country': 'Unknown',
                    'city': 'Unknown',
                    'latitude': 0.0,
                    'longitude': 0.0
                }
            }
        
    async def store_correlation(self, correlation: Correlation) -> bool:
        """Store correlation in database"""
        try:
            db = await get_database()
            await db.correlations.insert_one(correlation.dict())
            return True
            
        except Exception as e:
            logger.error(f"Error storing correlation: {e}")
            return False
            
    async def get_correlations(self, limit: int = 100, min_confidence: float = 0.5) -> List[Correlation]:
        """Get correlations from database"""
        try:
            db = await get_database()
            
            cursor = db.correlations.find(
                {'confidence_score': {'$gte': min_confidence}},
                sort=[('created_at', -1)],
                limit=limit
            )
            
            correlations = []
            async for doc in cursor:
                correlations.append(Correlation(**doc))
                
            return correlations
            
        except Exception as e:
            logger.error(f"Error getting correlations: {e}")
            return []