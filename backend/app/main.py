"""
Main FastAPI application.
Configures middleware, routes, and startup/shutdown events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered deadline forecasting system for project management"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns application status and version.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/")
async def root():
    """
    Root endpoint.
    Provides basic API information.
    """
    return {
        "message": "Welcome to AI Deadline Forecasting Agent API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers
from app.routers import auth, projects, tasks, forecasts, simulations, automation_logs, webhooks

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(forecasts.router)
app.include_router(simulations.router)
app.include_router(automation_logs.router)
app.include_router(webhooks.router)

@app.on_event("startup")
async def startup_event():
    """
    Runs on application startup.
    Can be used for initialization tasks.
    """
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"🌐 CORS enabled for: {', '.join(settings.allowed_origins)}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs on application shutdown.
    Can be used for cleanup tasks.
    """
    print(f"👋 {settings.APP_NAME} shutting down...")
