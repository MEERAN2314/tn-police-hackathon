from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.database import get_database
from app.models import TORNode, Correlation, APIResponse, NetworkTopology, TrafficFlow
from app.services.tor_service import TORService
from app.services.correlation_service import CorrelationService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get services
async def get_tor_service() -> TORService:
    return TORService()

async def get_correlation_service() -> CorrelationService:
    return CorrelationService()

async def get_ai_service() -> AIService:
    return AIService()

@router.get("/nodes", response_model=List[TORNode])
async def get_tor_nodes(
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
    tor_service: TORService = Depends(get_tor_service)
):
    """Get TOR nodes with optional filtering"""
    try:
        db = await get_database()
        
        # Build filter
        filter_dict = {}
        if country:
            filter_dict["country"] = country
        if node_type:
            filter_dict["type"] = node_type
            
        # Query database
        cursor = db.tor_nodes.find(filter_dict).limit(limit).sort("bandwidth", -1)
        nodes = []
        
        async for doc in cursor:
            nodes.append(TORNode(**doc))
            
        return nodes
        
    except Exception as e:
        logger.error(f"Error getting TOR nodes: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve nodes")

@router.get("/nodes/search")
async def search_nodes(
    query: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    tor_service: TORService = Depends(get_tor_service)
):
    """Search TOR nodes"""
    try:
        nodes = await tor_service.search_nodes(query, limit)
        return APIResponse(
            success=True,
            message=f"Found {len(nodes)} nodes",
            data=nodes
        )
    except Exception as e:
        logger.error(f"Error searching nodes: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/network/topology")
async def get_network_topology():
    """Get current network topology"""
    try:
        db = await get_database()
        
        # Get latest topology data
        topology = await db.network_topology.find_one(
            {},
            sort=[("timestamp", -1)]
        )
        
        if not topology:
            raise HTTPException(status_code=404, detail="No topology data available")
            
        return APIResponse(
            success=True,
            message="Network topology retrieved",
            data=topology
        )
        
    except Exception as e:
        logger.error(f"Error getting network topology: {e}")
        raise HTTPException(status_code=500, detail="Failed to get topology")

@router.get("/network/stats")
async def get_network_stats(tor_service: TORService = Depends(get_tor_service)):
    """Get network statistics"""
    try:
        stats = await tor_service.get_network_statistics()
        return APIResponse(
            success=True,
            message="Network statistics retrieved",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting network stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.get("/correlations", response_model=List[Correlation])
async def get_correlations(
    limit: int = Query(100, ge=1, le=1000),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    correlation_service: CorrelationService = Depends(get_correlation_service)
):
    """Get traffic correlations"""
    try:
        correlations = await correlation_service.get_correlations(limit, min_confidence)
        return correlations
    except Exception as e:
        logger.error(f"Error getting correlations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve correlations")

@router.post("/correlations/analyze")
async def analyze_correlations(
    background_tasks: BackgroundTasks,
    time_window: int = Query(300, description="Time window in seconds"),
    correlation_service: CorrelationService = Depends(get_correlation_service)
):
    """Trigger correlation analysis"""
    try:
        # Add background task for analysis
        background_tasks.add_task(run_correlation_analysis, correlation_service, time_window)
        
        return APIResponse(
            success=True,
            message="Correlation analysis started",
            data={"status": "running", "time_window": time_window}
        )
    except Exception as e:
        logger.error(f"Error starting correlation analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")

async def run_correlation_analysis(correlation_service: CorrelationService, time_window: int):
    """Background task for correlation analysis"""
    try:
        # Get recent traffic flows (mock data for demo)
        traffic_flows = await get_mock_traffic_flows(time_window)
        
        # Analyze correlations
        correlations = await correlation_service.analyze_traffic_correlation(traffic_flows)
        
        # Store results
        for correlation in correlations:
            await correlation_service.store_correlation(correlation)
            
        logger.info(f"Correlation analysis completed: {len(correlations)} correlations found")
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")

async def get_mock_traffic_flows(time_window: int) -> List[TrafficFlow]:
    """Generate mock traffic flows for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    flows = []
    base_time = datetime.utcnow() - timedelta(seconds=time_window)
    
    # Generate mock flows
    for i in range(50):
        flow = TrafficFlow(
            id=f"flow_{i}",
            timestamp=base_time + timedelta(seconds=random.randint(0, time_window)),
            source_ip=f"192.168.1.{random.randint(1, 254)}",
            destination_ip=f"10.0.0.{random.randint(1, 254)}",
            source_port=random.randint(1024, 65535),
            destination_port=random.choice([80, 443, 22, 25, 53]),
            protocol="TCP",
            bytes_sent=random.randint(1000, 100000),
            bytes_received=random.randint(1000, 100000),
            duration=random.uniform(1.0, 30.0),
            entry_node=f"entry_node_{random.randint(1, 10)}",
            exit_node=f"exit_node_{random.randint(1, 10)}",
            circuit_id=f"circuit_{random.randint(1000, 9999)}"
        )
        flows.append(flow)
        
    return flows

@router.get("/analysis/ai")
async def get_ai_analysis(
    analysis_type: str = Query(..., description="Type of analysis"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get AI-powered analysis"""
    try:
        if analysis_type == "network_patterns":
            # Get recent nodes for analysis
            db = await get_database()
            cursor = db.tor_nodes.find({}).limit(100)
            nodes = []
            async for doc in cursor:
                nodes.append(TORNode(**doc))
                
            analysis = await ai_service.analyze_network_patterns(nodes)
            
        elif analysis_type == "threat_assessment":
            # Mock threat assessment
            analysis = {
                "threat_level": "medium",
                "indicators": ["Unusual traffic patterns", "Geographic anomalies"],
                "recommendations": ["Increase monitoring", "Investigate specific nodes"]
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
            
        return APIResponse(
            success=True,
            message=f"AI analysis completed: {analysis_type}",
            data=analysis
        )
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        raise HTTPException(status_code=500, detail="AI analysis failed")

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    try:
        db = await get_database()
        
        # Get various statistics
        stats = {
            "nodes": {
                "total": await db.tor_nodes.count_documents({}),
                "guard": await db.tor_nodes.count_documents({"type": "guard"}),
                "middle": await db.tor_nodes.count_documents({"type": "middle"}),
                "exit": await db.tor_nodes.count_documents({"type": "exit"}),
                "bridge": await db.tor_nodes.count_documents({"type": "bridge"})
            },
            "correlations": {
                "total": await db.correlations.count_documents({}),
                "high_confidence": await db.correlations.count_documents({"confidence_score": {"$gte": 0.8}}),
                "medium_confidence": await db.correlations.count_documents({"confidence_score": {"$gte": 0.5, "$lt": 0.8}}),
                "recent": await db.correlations.count_documents({
                    "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                })
            },
            "geographic": {
                "countries": len(await db.tor_nodes.distinct("country")),
                "top_countries": await get_top_countries()
            },
            "activity": {
                "last_update": datetime.utcnow().isoformat(),
                "status": "active"
            }
        }
        
        return APIResponse(
            success=True,
            message="Dashboard statistics retrieved",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

async def get_top_countries() -> List[Dict[str, Any]]:
    """Get top countries by node count"""
    try:
        db = await get_database()
        
        pipeline = [
            {"$group": {
                "_id": "$country",
                "count": {"$sum": 1},
                "country_name": {"$first": "$country_name"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        results = await db.tor_nodes.aggregate(pipeline).to_list(10)
        
        return [
            {
                "country": result["_id"],
                "country_name": result.get("country_name", result["_id"]),
                "count": result["count"]
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting top countries: {e}")
        return []

@router.get("/export/correlations")
async def export_correlations(
    format: str = Query("json", description="Export format: json, csv"),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0)
):
    """Export correlations data"""
    try:
        db = await get_database()
        
        cursor = db.correlations.find(
            {"confidence_score": {"$gte": min_confidence}},
            sort=[("created_at", -1)]
        )
        
        correlations = []
        async for doc in cursor:
            correlations.append(doc)
            
        if format == "json":
            return APIResponse(
                success=True,
                message=f"Exported {len(correlations)} correlations",
                data=correlations
            )
        elif format == "csv":
            # Convert to CSV format
            csv_data = convert_to_csv(correlations)
            return APIResponse(
                success=True,
                message=f"Exported {len(correlations)} correlations as CSV",
                data={"csv": csv_data}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        logger.error(f"Error exporting correlations: {e}")
        raise HTTPException(status_code=500, detail="Export failed")

def convert_to_csv(correlations: List[Dict]) -> str:
    """Convert correlations to CSV format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Entry Node", "Exit Node", "Origin IP", "Destination IP",
        "Confidence Score", "Method", "Created At"
    ])
    
    # Write data
    for corr in correlations:
        writer.writerow([
            corr.get("id", ""),
            corr.get("entry_node", ""),
            corr.get("exit_node", ""),
            corr.get("origin_ip", ""),
            corr.get("destination_ip", ""),
            corr.get("confidence_score", 0),
            corr.get("correlation_method", ""),
            corr.get("created_at", "")
        ])
    
    return output.getvalue()