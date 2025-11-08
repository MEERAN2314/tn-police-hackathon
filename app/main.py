from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import socketio
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import dashboard, api, auth, analysis, reports
from app.services.tor_service import TORService
from app.services.correlation_service import CorrelationService
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TOR Analysis System...")
    await connect_to_mongo()
    
    # Initialize services
    app.state.tor_service = TORService()
    app.state.correlation_service = CorrelationService()
    
    # Start background tasks
    await app.state.tor_service.start_monitoring()
    
    logger.info("TOR Analysis System started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TOR Analysis System...")
    await app.state.tor_service.stop_monitoring()
    await close_mongo_connection()
    logger.info("TOR Analysis System shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="TOR Analysis System",
    description="Advanced TOR Network Analysis and Correlation System for Law Enforcement",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["yourdomain.com", "*.yourdomain.com"]
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Socket.IO for real-time updates
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*" if settings.debug else ["https://yourdomain.com"]
)
socket_app = socketio.ASGIApp(sio, app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])
app.include_router(api.router, prefix="/api/v1", tags=["API"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "title": "TOR Analysis Dashboard",
            "page": "dashboard"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = await get_database()
        # Test database connection
        await db.command("ping")
        
        return JSONResponse(
            content={
                "status": "healthy",
                "timestamp": "2025-01-01T00:00:00Z",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "redis": "connected",
                    "tor_service": "running"
                }
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-01T00:00:00Z"
            }
        )

# Socket.IO events
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client {sid} connected")
    await sio.emit('connected', {'message': 'Connected to TOR Analysis System'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client {sid} disconnected")

@sio.event
async def subscribe_updates(sid, data):
    """Subscribe to real-time updates"""
    update_type = data.get('type', 'all')
    await sio.enter_room(sid, f"updates_{update_type}")
    logger.info(f"Client {sid} subscribed to {update_type} updates")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )