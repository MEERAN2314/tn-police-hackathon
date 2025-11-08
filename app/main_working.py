from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TOR Analysis System",
    description="Advanced TOR Network Analysis and Correlation System for Law Enforcement",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Mock data for demo
MOCK_STATS = {
    "total_nodes": 1247,
    "active_correlations": 89,
    "high_confidence_matches": 23,
    "countries_monitored": 67,
    "total_bandwidth": "2.4 GB/s",
    "uptime_percentage": 99.2,
    "last_updated": datetime.utcnow()
}

MOCK_NODES = [
    {
        "fingerprint": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0",
        "nickname": "TorRelay001",
        "address": "192.168.1.100",
        "or_port": 9001,
        "country": "US",
        "country_name": "United States",
        "bandwidth": 1024000,
        "type": "guard",
        "flags": ["Guard", "Fast", "Running", "Stable", "Valid"]
    },
    {
        "fingerprint": "B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0A1",
        "nickname": "ExitNode42",
        "address": "10.0.0.50",
        "or_port": 9001,
        "country": "DE",
        "country_name": "Germany",
        "bandwidth": 512000,
        "type": "exit",
        "flags": ["Exit", "Fast", "Running", "Valid"]
    }
]

MOCK_CORRELATIONS = [
    {
        "id": "corr_001",
        "entry_node": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0",
        "exit_node": "B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0A1",
        "origin_ip": "192.168.1.10",
        "destination_ip": "203.0.113.5",
        "confidence_score": 0.85,
        "correlation_method": "timing_analysis",
        "created_at": datetime.utcnow()
    }
]

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "title": "TOR Analysis Dashboard",
            "page": "dashboard",
            "stats": MOCK_STATS
        }
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "title": "TOR Analysis Dashboard",
            "page": "dashboard",
            "stats": MOCK_STATS
        }
    )

@app.get("/network", response_class=HTMLResponse)
async def network_topology(request: Request):
    """Network topology page"""
    return templates.TemplateResponse(
        "network/topology.html",
        {
            "request": request,
            "title": "Network Topology",
            "page": "network"
        }
    )

@app.get("/correlations", response_class=HTMLResponse)
async def correlations_page(request: Request):
    """Correlations page"""
    return templates.TemplateResponse(
        "correlations/index.html",
        {
            "request": request,
            "title": "Traffic Correlations",
            "page": "correlations"
        }
    )

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Analysis page"""
    return templates.TemplateResponse(
        "analysis/dashboard.html",
        {
            "request": request,
            "title": "Analysis Tools",
            "page": "analysis"
        }
    )

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page"""
    return templates.TemplateResponse(
        "reports/dashboard.html",
        {
            "request": request,
            "title": "Reports",
            "page": "reports"
        }
    )

# Authentication routes (simplified)
@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse(
        "auth/login_simple.html",
        {
            "request": request,
            "title": "Login - TOR Analysis System"
        }
    )

@app.post("/auth/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Simple login - check credentials and redirect"""
    try:
        # Simple credential check
        if username == "admin" and password == "admin123":
            # Successful login - redirect to dashboard
            return RedirectResponse(url="/dashboard", status_code=302)
        else:
            # Failed login - return to login page with error
            return templates.TemplateResponse(
                "auth/login_simple.html",
                {
                    "request": request,
                    "title": "Login - TOR Analysis System",
                    "error": "Invalid username or password. Use admin/admin123"
                }
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(
            "auth/login_simple.html",
            {
                "request": request,
                "title": "Login - TOR Analysis System",
                "error": "Login failed. Please try again."
            }
        )

@app.post("/auth/logout")
async def logout():
    """Logout user"""
    return RedirectResponse(url="/auth/login", status_code=302)

# API Routes
@app.get("/api/v1/nodes")
async def get_nodes(limit: int = 100):
    """Get TOR nodes"""
    return MOCK_NODES[:limit]

@app.get("/api/v1/correlations")
async def get_correlations(limit: int = 100):
    """Get correlations"""
    return MOCK_CORRELATIONS[:limit]

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Dashboard statistics retrieved",
            "data": {
                "nodes": {
                    "total": MOCK_STATS["total_nodes"],
                    "guard": 450,
                    "middle": 520,
                    "exit": 200,
                    "bridge": 77
                },
                "correlations": {
                    "total": MOCK_STATS["active_correlations"],
                    "high_confidence": MOCK_STATS["high_confidence_matches"],
                    "medium_confidence": 35,
                    "recent": 12
                },
                "geographic": {
                    "countries": MOCK_STATS["countries_monitored"],
                    "top_countries": [
                        {"country": "US", "country_name": "United States", "count": 245},
                        {"country": "DE", "country_name": "Germany", "count": 189},
                        {"country": "FR", "country_name": "France", "count": 156}
                    ]
                },
                "activity": {
                    "last_update": MOCK_STATS["last_updated"].isoformat(),
                    "status": "active"
                }
            }
        }
    )

@app.post("/api/v1/correlations/analyze")
async def analyze_correlations():
    """Start correlation analysis"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Correlation analysis started",
            "data": {"status": "running", "task_id": "mock_task_123"}
        }
    )

@app.get("/api/v1/export/correlations")
async def export_correlations(format: str = "json"):
    """Export correlations"""
    if format == "csv":
        csv_data = "ID,Entry Node,Exit Node,Origin IP,Destination IP,Confidence Score\n"
        for corr in MOCK_CORRELATIONS:
            csv_data += f"{corr['id']},{corr['entry_node']},{corr['exit_node']},{corr['origin_ip']},{corr['destination_ip']},{corr['confidence_score']}\n"
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Data exported as CSV",
                "data": {"csv": csv_data}
            }
        )
    else:
        return JSONResponse(
            content={
                "success": True,
                "message": "Data exported as JSON",
                "data": MOCK_CORRELATIONS
            }
        )

@app.get("/health")
async def health_check():
    """Health check"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected",
                "redis": "connected",
                "tor_service": "running"
            }
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": f"An error occurred: {str(exc)}",
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)