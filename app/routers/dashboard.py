from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
import logging

from app.database import get_database
from app.services.tor_service import TORService
from app.services.correlation_service import CorrelationService
from app.models import DashboardStats

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    try:
        # Get dashboard statistics
        stats = await get_dashboard_stats()
        
        return templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "title": "TOR Analysis Dashboard",
                "page": "dashboard",
                "stats": stats
            }
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

@router.get("/network", response_class=HTMLResponse)
async def network_topology(request: Request):
    """Network topology visualization page"""
    return templates.TemplateResponse(
        "network/topology.html",
        {
            "request": request,
            "title": "Network Topology",
            "page": "network"
        }
    )

@router.get("/correlations", response_class=HTMLResponse)
async def correlations_page(request: Request):
    """Correlations analysis page"""
    return templates.TemplateResponse(
        "correlations/index.html",
        {
            "request": request,
            "title": "Traffic Correlations",
            "page": "correlations"
        }
    )

@router.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Analysis tools page"""
    return templates.TemplateResponse(
        "analysis/index.html",
        {
            "request": request,
            "title": "Analysis Tools",
            "page": "analysis"
        }
    )

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page"""
    return templates.TemplateResponse(
        "reports/index.html",
        {
            "request": request,
            "title": "Reports",
            "page": "reports"
        }
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    return templates.TemplateResponse(
        "settings/index.html",
        {
            "request": request,
            "title": "Settings",
            "page": "settings"
        }
    )

async def get_dashboard_stats() -> DashboardStats:
    """Get dashboard statistics"""
    try:
        db = await get_database()
        
        # Get total nodes count
        total_nodes = await db.tor_nodes.count_documents({})
        
        # Get active correlations count
        active_correlations = await db.correlations.count_documents({"status": "active"})
        
        # Get high confidence matches
        high_confidence_matches = await db.correlations.count_documents({
            "confidence_score": {"$gte": 0.8},
            "status": "active"
        })
        
        # Get unique countries
        countries = await db.tor_nodes.distinct("country")
        countries_monitored = len(countries)
        
        # Get total bandwidth (mock calculation)
        pipeline = [
            {"$group": {"_id": None, "total_bandwidth": {"$sum": "$bandwidth"}}}
        ]
        bandwidth_result = await db.tor_nodes.aggregate(pipeline).to_list(1)
        total_bandwidth_kb = bandwidth_result[0]["total_bandwidth"] if bandwidth_result else 0
        total_bandwidth = f"{total_bandwidth_kb / 1024:.1f} MB/s"
        
        # Calculate uptime percentage (mock)
        uptime_percentage = 99.2
        
        return DashboardStats(
            total_nodes=total_nodes,
            active_correlations=active_correlations,
            high_confidence_matches=high_confidence_matches,
            countries_monitored=countries_monitored,
            total_bandwidth=total_bandwidth,
            uptime_percentage=uptime_percentage
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return DashboardStats()