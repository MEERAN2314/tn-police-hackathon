from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
import logging

from app.routers.auth import get_optional_user, User

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def reports_dashboard(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """Reports dashboard page"""
    return templates.TemplateResponse(
        "reports/dashboard.html",
        {
            "request": request,
            "title": "Reports Dashboard",
            "page": "reports",
            "user": user
        }
    )

@router.get("/generate", response_class=HTMLResponse)
async def generate_report(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """Generate report page"""
    return templates.TemplateResponse(
        "reports/generate.html",
        {
            "request": request,
            "title": "Generate Report",
            "page": "reports",
            "user": user
        }
    )