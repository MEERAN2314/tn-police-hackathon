from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NodeType(str, Enum):
    GUARD = "guard"
    MIDDLE = "middle"
    EXIT = "exit"
    BRIDGE = "bridge"

class TORNode(BaseModel):
    fingerprint: str = Field(..., description="Unique node fingerprint")
    nickname: str = Field(..., description="Node nickname")
    address: str = Field(..., description="IP address")
    or_port: int = Field(..., description="OR port")
    dir_port: Optional[int] = Field(None, description="Directory port")
    country: str = Field(..., description="Country code")
    country_name: str = Field(..., description="Full country name")
    region_name: Optional[str] = Field(None, description="Region/state name")
    city_name: Optional[str] = Field(None, description="City name")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    bandwidth: int = Field(..., description="Advertised bandwidth")
    observed_bandwidth: int = Field(..., description="Observed bandwidth")
    consensus_weight: int = Field(..., description="Consensus weight")
    flags: List[str] = Field(default_factory=list, description="Node flags")
    type: NodeType = Field(..., description="Node type")
    first_seen: datetime = Field(..., description="First seen timestamp")
    last_seen: datetime = Field(..., description="Last seen timestamp")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")
    contact: Optional[str] = Field(None, description="Contact information")
    platform: Optional[str] = Field(None, description="Platform information")
    version: Optional[str] = Field(None, description="TOR version")
    
class TrafficFlow(BaseModel):
    id: str = Field(..., description="Unique flow ID")
    timestamp: datetime = Field(..., description="Flow timestamp")
    source_ip: str = Field(..., description="Source IP address")
    destination_ip: str = Field(..., description="Destination IP address")
    source_port: int = Field(..., description="Source port")
    destination_port: int = Field(..., description="Destination port")
    protocol: str = Field(..., description="Protocol (TCP/UDP)")
    bytes_sent: int = Field(default=0, description="Bytes sent")
    bytes_received: int = Field(default=0, description="Bytes received")
    duration: float = Field(..., description="Flow duration in seconds")
    entry_node: Optional[str] = Field(None, description="Entry node fingerprint")
    exit_node: Optional[str] = Field(None, description="Exit node fingerprint")
    circuit_id: Optional[str] = Field(None, description="Circuit ID")

class Correlation(BaseModel):
    id: str = Field(..., description="Unique correlation ID")
    entry_node: str = Field(..., description="Entry node fingerprint")
    exit_node: str = Field(..., description="Exit node fingerprint")
    middle_nodes: List[str] = Field(default_factory=list, description="Middle node fingerprints")
    origin_ip: str = Field(..., description="Probable origin IP")
    destination_ip: str = Field(..., description="Destination IP")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    correlation_method: str = Field(..., description="Correlation method used")
    timing_analysis: Dict[str, Any] = Field(default_factory=dict, description="Timing analysis data")
    traffic_pattern: Dict[str, Any] = Field(default_factory=dict, description="Traffic pattern data")
    geolocation_data: Dict[str, Any] = Field(default_factory=dict, description="Geolocation information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    status: str = Field(default="active", description="Correlation status")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting evidence")

class NetworkTopology(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_nodes: int = Field(..., description="Total number of nodes")
    guard_nodes: int = Field(..., description="Number of guard nodes")
    middle_nodes: int = Field(..., description="Number of middle nodes")
    exit_nodes: int = Field(..., description="Number of exit nodes")
    bridge_nodes: int = Field(..., description="Number of bridge nodes")
    countries: List[str] = Field(default_factory=list, description="Countries with nodes")
    total_bandwidth: int = Field(..., description="Total network bandwidth")
    consensus_weight: int = Field(..., description="Total consensus weight")

class AnalysisReport(BaseModel):
    id: str = Field(..., description="Report ID")
    title: str = Field(..., description="Report title")
    description: str = Field(..., description="Report description")
    correlations: List[Correlation] = Field(default_factory=list)
    network_topology: NetworkTopology = Field(..., description="Network topology snapshot")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis time period")
    total_correlations: int = Field(..., description="Total correlations found")
    high_confidence_correlations: int = Field(..., description="High confidence correlations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Generated by user/system")
    export_formats: List[str] = Field(default_factory=list, description="Available export formats")

class User(BaseModel):
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    role: str = Field(default="analyst", description="User role")
    is_active: bool = Field(default=True, description="Account status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class DashboardStats(BaseModel):
    total_nodes: int = 0
    active_correlations: int = 0
    high_confidence_matches: int = 0
    countries_monitored: int = 0
    total_bandwidth: str = "0 MB/s"
    uptime_percentage: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)