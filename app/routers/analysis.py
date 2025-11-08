from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Optional
import logging

from app.database import get_database
from app.models import APIResponse
from app.routers.auth import get_optional_user, User
from app.services.correlation_service import CorrelationService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def analysis_dashboard(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """Analysis dashboard page"""
    return templates.TemplateResponse(
        "analysis/dashboard.html",
        {
            "request": request,
            "title": "Analysis Dashboard",
            "page": "analysis",
            "user": user
        }
    )

@router.get("/correlation", response_class=HTMLResponse)
async def correlation_analysis(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """Correlation analysis page"""
    return templates.TemplateResponse(
        "analysis/correlation.html",
        {
            "request": request,
            "title": "Correlation Analysis",
            "page": "analysis",
            "user": user
        }
    )

@router.get("/pattern", response_class=HTMLResponse)
async def pattern_analysis(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """Pattern analysis page"""
    return templates.TemplateResponse(
        "analysis/pattern.html",
        {
            "request": request,
            "title": "Pattern Analysis",
            "page": "analysis",
            "user": user
        }
    )

@router.get("/ai", response_class=HTMLResponse)
async def ai_analysis(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """AI-powered analysis page"""
    return templates.TemplateResponse(
        "analysis/ai.html",
        {
            "request": request,
            "title": "AI Analysis",
            "page": "analysis",
            "user": user
        }
    )