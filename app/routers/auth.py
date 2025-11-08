from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import logging
import jwt
from passlib.context import CryptContext

from app.config import settings
from app.database import get_database
from app.models import User, APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "analyst"

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "title": "Login - TOR Analysis System"
        }
    )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Authenticate user and return token"""
    try:
        # Authenticate user
        user = await authenticate_user(username, password)
        if not user:
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "title": "Login - TOR Analysis System",
                    "error": "Invalid username or password"
                }
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        # Redirect to dashboard with token in cookie
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        # Update last login
        await update_last_login(user.username)
        
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Login - TOR Analysis System",
                "error": "Login failed. Please try again."
            }
        )

@router.post("/api/login", response_model=TokenResponse)
async def api_login(login_request: LoginRequest):
    """API login endpoint"""
    try:
        user = await authenticate_user(login_request.username, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.username})
        
        # Update last login
        await update_last_login(user.username)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "title": "Register - TOR Analysis System"
        }
    )

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Register new user"""
    try:
        # Validate passwords match
        if password != confirm_password:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "title": "Register - TOR Analysis System",
                    "error": "Passwords do not match"
                }
            )
        
        # Check if user exists
        existing_user = await get_user_by_username(username)
        if existing_user:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "title": "Register - TOR Analysis System",
                    "error": "Username already exists"
                }
            )
        
        # Create user
        user_data = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            password=password
        )
        
        await create_user(user_data)
        
        # Redirect to login
        return RedirectResponse(url="/auth/login?registered=true", status_code=302)
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "title": "Register - TOR Analysis System",
                "error": "Registration failed. Please try again."
            }
        )

@router.post("/api/register", response_model=APIResponse)
async def api_register(user_data: UserCreate):
    """API registration endpoint"""
    try:
        # Check if user exists
        existing_user = await get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Create user
        await create_user(user_data)
        
        return APIResponse(
            success=True,
            message="User registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    try:
        user = await get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.get("hashed_password", "")):
            return None
        
        return User(**user)
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

async def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    try:
        db = await get_database()
        user = await db.users.find_one({"username": username})
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None

async def create_user(user_data: UserCreate) -> bool:
    """Create new user"""
    try:
        db = await get_database()
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "role": user_data.role,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        await db.users.insert_one(user_doc)
        return True
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False

async def update_last_login(username: str):
    """Update user's last login timestamp"""
    try:
        db = await get_database()
        await db.users.update_one(
            {"username": username},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except Exception as e:
        logger.error(f"Error updating last login: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return User(**user)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Optional dependency for pages that don't require authentication
async def get_optional_user(request: Request) -> Optional[User]:
    """Get user from cookie if available"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        # Remove "Bearer " prefix
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user_data = await get_user_by_username(username)
        if user_data is None:
            return None
        
        return User(**user_data)
        
    except Exception as e:
        logger.debug(f"Optional user authentication failed: {e}")
        return None

# Create default admin user on startup
async def create_default_admin():
    """Create default admin user if none exists"""
    try:
        db = await get_database()
        
        # Check if any admin user exists
        admin_count = await db.users.count_documents({"role": "admin"})
        
        if admin_count == 0:
            # Create default admin
            admin_data = UserCreate(
                username="admin",
                email="admin@toranalysis.local",
                full_name="System Administrator",
                password="admin123",  # Change this in production!
                role="admin"
            )
            
            await create_user(admin_data)
            logger.info("Default admin user created: admin/admin123")
            
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")