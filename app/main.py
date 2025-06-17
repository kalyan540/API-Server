from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from app.middleware import limiter, rate_limit_handler
from app.database import create_tables
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.devices.routes import router as devices_router
from slowapi import Limiter
import os

# Create FastAPI app
app = FastAPI(
    title="IoT Platform API",
    description="Secure, scalable FastAPI-based backend for IoT device management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add custom rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(devices_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IoT Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iot-platform-api"
    }

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    create_tables()
    print("🚀 IoT Platform API started successfully!")
    print("📖 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 