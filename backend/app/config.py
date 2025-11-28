"""
Configuration module for the AI Deadline Forecasting Agent.
Loads environment variables and provides app-wide settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_deadline")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # External APIs
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678")
    
    # App Info
    APP_NAME: str = "AI Deadline Forecasting Agent"
    APP_VERSION: str = "1.0.0"
    
    @property
    def allowed_origins(self):
        """Get list of allowed CORS origins"""
        return [
            self.FRONTEND_URL,
            "http://localhost:5173",
            "http://localhost:3000",
        ]

settings = Settings()
