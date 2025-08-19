#!/usr/bin/env python3
"""
Main Server Application for Web Application Backend
Integrates all systems: Appliance Health, Solar Calculator, Smart Analysis, Bill Simulation, and Carbon Tracking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize FastAPI app
app = FastAPI(
    title="Smart Energy Management System",
    description="Comprehensive backend for appliance health, solar feasibility, bill simulation, and carbon tracking",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global status tracking
system_status = {
    "appliance_health": False,
    "solar_calculator": False,
    "smart_analysis": False,
    "bill_simulation": False,
    "carbon_tracker": False
}

# Try to load all system routers
print("🚀 Loading Smart Energy Management System...")

# Try to load appliance health system
try:
    from appliance_health_router import appliance_health_router
    app.include_router(appliance_health_router)
    system_status["appliance_health"] = True
    print("✅ Appliance health router loaded successfully")
except ImportError as e:
    print(f"⚠️  Appliance health router not loaded: {e}")

# Try to load solar calculator system
try:
    from solar_calculator_router import solar_calculator_router
    app.include_router(solar_calculator_router)
    system_status["solar_calculator"] = True
    print("✅ Solar calculator router loaded successfully")
except ImportError as e:
    print(f"⚠️  Solar calculator router not loaded: {e}")

# Try to load smart automated system
try:
    from smart_automated_router import smart_automated_router
    app.include_router(smart_automated_router)
    system_status["smart_analysis"] = True
    print("✅ Smart automated system router loaded successfully")
except ImportError as e:
    print(f"⚠️  Smart automated system router not loaded: {e}")

# Try to load bill simulation system
try:
    from bill_simulation_router import bill_simulation_router
    app.include_router(bill_simulation_router)
    system_status["bill_simulation"] = True
    print("✅ Bill simulation router loaded successfully")
except ImportError as e:
    print(f"⚠️  Bill simulation router not loaded: {e}")

# Try to load carbon tracker system
try:
    from carbon_tracker_router import carbon_tracker_router
    app.include_router(carbon_tracker_router)
    system_status["carbon_tracker"] = True
    print("✅ Carbon tracker router loaded successfully")
except ImportError as e:
    print(f"⚠️  Carbon tracker router not loaded: {e}")

# Load web application routes
try:
    from server.web_routes import web_router
    app.include_router(web_router)
    print("✅ Web application routes loaded successfully")
except ImportError as e:
    print(f"⚠️  Web application routes not loaded: {e}")

print(f"🎯 System Status: {system_status}")

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint with system overview"""
    return {
        "message": "Smart Energy Management System Backend",
        "status": "running",
        "version": "1.0.0",
        "systems": system_status,
        "available_endpoints": {
            "root": "/",
            "docs": "/docs",
            "health": "/health",
            "status": "/status",
            "appliance_health": "/appliance-health/*",
            "solar_calculator": "/solar-calculator/*",
            "smart_analysis": "/smart-analysis/*",
            "bill_simulation": "/bill-simulation/*",
            "carbon_tracker": "/carbon-tracker/*",
            "web_application": "/web/*"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "systems": system_status
    }

# System status endpoint
@app.get("/status")
def get_system_status():
    """Detailed system status and health information"""
    return {
        "overall_status": "healthy" if all(system_status.values()) else "degraded",
        "systems": system_status,
        "total_systems": len(system_status),
        "active_systems": sum(system_status.values()),
        "inactive_systems": len(system_status) - sum(system_status.values())
    }

# Error handler for 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": [
                "/",
                "/docs",
                "/health",
                "/status",
                "/appliance-health/*",
                "/solar-calculator/*",
                "/smart-analysis/*",
                "/bill-simulation/*",
                "/carbon-tracker/*",
                "/web/*"
            ]
        }
    )

# Error handler for 500
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Smart Energy Management System Server...")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Health check available at: http://localhost:8000/health")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
