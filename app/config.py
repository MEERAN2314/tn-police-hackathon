import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    redis_url: str = "redis://localhost:6379"
    database_name: str = "tor_analysis"
    
    # API Keys
    gemini_api_key: Optional[str] = None
    ipgeolocation_api_key: Optional[str] = None
    use_free_geolocation: bool = True
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    max_workers: int = 4
    
    # TOR Configuration
    tor_control_port: int = 9051
    tor_socks_port: int = 9050
    tor_data_refresh_interval: int = 300
    
    # External APIs
    tor_metrics_api: str = "https://metrics.torproject.org"
    onionoo_api: str = "https://onionoo.torproject.org"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()