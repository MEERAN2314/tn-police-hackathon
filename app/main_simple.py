from fastapi import FastAPI, Request, HTTPException, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
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

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

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

# Authentication helpers
def get_current_user(request: Request):
    """Get current user from session"""
    return request.session.get("user")

def require_auth(request: Request):
    """Require authentication, redirect to login if not authenticated"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return user

# Demo credentials
DEMO_USERS = {
    "admin": "admin123",
    "user": "password123"
}

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
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "title": "TOR Analysis Dashboard",
            "page": "dashboard",
            "stats": MOCK_STATS,
            "user": user
        }
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "title": "TOR Analysis Dashboard",
            "page": "dashboard",
            "stats": MOCK_STATS,
            "user": user
        }
    )

@app.get("/network", response_class=HTMLResponse)
async def network_topology(request: Request):
    """Network topology page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "network/topology.html",
        {
            "request": request,
            "title": "Network Topology",
            "page": "network",
            "user": user
        }
    )

@app.get("/correlations", response_class=HTMLResponse)
async def correlations_page(request: Request):
    """Correlations page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "correlations/index.html",
        {
            "request": request,
            "title": "Traffic Correlations",
            "page": "correlations",
            "user": user
        }
    )

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Analysis page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "analysis/dashboard.html",
        {
            "request": request,
            "title": "Analysis Tools",
            "page": "analysis",
            "user": user
        }
    )

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "reports/dashboard.html",
        {
            "request": request,
            "title": "Reports",
            "page": "reports",
            "user": user
        }
    )

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

# Authentication routes
@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    # If already logged in, redirect to dashboard
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "title": "Login - TOR Analysis System"
        }
    )

@app.post("/auth/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login form submission"""
    # Check credentials
    if username in DEMO_USERS and DEMO_USERS[username] == password:
        # Set session
        request.session["user"] = {
            "username": username,
            "login_time": datetime.utcnow().isoformat()
        }
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        # Login failed
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Login - TOR Analysis System",
                "error": "Invalid username or password"
            }
        )

@app.get("/auth/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)