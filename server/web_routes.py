#!/usr/bin/env python3
"""
Web Application Specific Routes
Handles frontend communication, data aggregation, and user interactions
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize router
web_router = APIRouter(prefix="/web", tags=["Web Application Routes"])

# Pydantic models for web requests
class DashboardRequest(BaseModel):
    """Request for dashboard data"""
    user_id: Optional[str] = None
    include_solar: bool = True
    include_appliance_health: bool = True
    include_bill_simulation: bool = True
    include_carbon_tracking: bool = True

class UserPreferences(BaseModel):
    """User preferences and settings"""
    location: Optional[str] = None
    energy_company: Optional[str] = None
    monthly_budget: Optional[float] = None
    solar_interest: bool = True
    appliance_monitoring: bool = True
    carbon_tracking: bool = True

class DataExportRequest(BaseModel):
    """Request for data export"""
    format: str = "json"  # json, csv, pdf
    data_type: str = "all"  # all, solar, appliance, bills, carbon
    date_range: Optional[str] = None

# Dashboard endpoint
@web_router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data for frontend"""
    try:
        dashboard_data = {
            "summary": {
                "total_systems": 5,
                "active_systems": 5,
                "last_updated": "2024-01-01T00:00:00Z"
            },
            "solar_insights": {
                "potential_savings": "$1,200/year",
                "roi_percentage": "15.2%",
                "payback_period": "6.6 years",
                "carbon_offset": "4.2 tons CO2/year"
            },
            "appliance_health": {
                "total_appliances": 8,
                "healthy": 7,
                "warning": 1,
                "critical": 0,
                "estimated_savings": "$180/year"
            },
            "bill_forecast": {
                "next_month": "$145",
                "trend": "decreasing",
                "seasonal_factor": "summer_peak",
                "efficiency_tips": [
                    "Optimize AC usage during peak hours",
                    "Consider smart thermostat installation",
                    "Check for phantom loads"
                ]
            },
            "carbon_footprint": {
                "current_month": "0.8 tons CO2",
                "trend": "decreasing",
                "offset_progress": "65%",
                "suggestions": [
                    "Switch to LED lighting",
                    "Use energy-efficient appliances",
                    "Consider renewable energy options"
                ]
            }
        }
        
        return JSONResponse(content=dashboard_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

# User preferences endpoint
@web_router.post("/preferences")
async def update_user_preferences(preferences: UserPreferences):
    """Update user preferences and settings"""
    try:
        # In a real application, this would save to a database
        # For now, we'll just return the preferences
        return {
            "message": "Preferences updated successfully",
            "preferences": preferences.dict(),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

# Data export endpoint
@web_router.post("/export")
async def export_data(export_request: DataExportRequest):
    """Export data in various formats"""
    try:
        # In a real application, this would generate actual export files
        export_info = {
            "format": export_request.format,
            "data_type": export_request.data_type,
            "date_range": export_request.date_range,
            "download_url": f"/downloads/export_{export_request.data_type}_{export_request.format}.{export_request.format}",
            "expires_at": "2024-01-02T00:00:00Z"
        }
        
        return JSONResponse(content=export_info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

# System integration status
@web_router.get("/integration-status")
async def get_integration_status():
    """Get status of all integrated systems"""
    try:
        # Check if various systems are available
        systems = {}
        
        # Check appliance health system
        try:
            from appliance_health_router import appliance_health_router
            systems["appliance_health"] = {
                "status": "active",
                "endpoints": ["/appliance-health/*"],
                "features": ["anomaly_detection", "health_prediction", "maintenance_alerts"]
            }
        except ImportError:
            systems["appliance_health"] = {
                "status": "inactive",
                "error": "Module not found"
            }
        
        # Check solar calculator system
        try:
            from solar_calculator_router import solar_calculator_router
            systems["solar_calculator"] = {
                "status": "active",
                "endpoints": ["/solar-calculator/*"],
                "features": ["feasibility_analysis", "roi_calculation", "cost_breakdown"]
            }
        except ImportError:
            systems["solar_calculator"] = {
                "status": "inactive",
                "error": "Module not found"
            }
        
        # Check smart analysis system
        try:
            from smart_automated_router import smart_automated_router
            systems["smart_analysis"] = {
                "status": "active",
                "endpoints": ["/smart-analysis/*"],
                "features": ["automated_detection", "one_click_analysis", "real_time_data"]
            }
        except ImportError:
            systems["smart_analysis"] = {
                "status": "inactive",
                "error": "Module not found"
            }
        
        # Check bill simulation system
        try:
            from bill_simulation_router import bill_simulation_router
            systems["bill_simulation"] = {
                "status": "active",
                "endpoints": ["/bill-simulation/*"],
                "features": ["usage_prediction", "scenario_modeling", "seasonal_analysis"]
            }
        except ImportError:
            systems["bill_simulation"] = {
                "status": "inactive",
                "error": "Module not found"
            }
        
        # Check carbon tracker system
        try:
            from carbon_tracker_router import carbon_tracker_router
            systems["carbon_tracker"] = {
                "status": "active",
                "endpoints": ["/carbon-tracker/*"],
                "features": ["emission_tracking", "offset_calculation", "progress_reporting"]
            }
        except ImportError:
            systems["carbon_tracker"] = {
                "status": "inactive",
                "error": "Module not found"
            }
        
        return {
            "overall_status": "healthy" if all(s.get("status") == "active" for s in systems.values()) else "degraded",
            "systems": systems,
            "total_systems": len(systems),
            "active_systems": sum(1 for s in systems.values() if s.get("status") == "active"),
            "inactive_systems": sum(1 for s in systems.values() if s.get("status") != "active")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

# Frontend configuration endpoint
@web_router.get("/config")
async def get_frontend_config():
    """Get frontend configuration and feature flags"""
    try:
        config = {
            "features": {
                "solar_calculator": True,
                "appliance_health": True,
                "smart_analysis": True,
                "bill_simulation": True,
                "carbon_tracking": True,
                "data_export": True,
                "user_preferences": True
            },
            "ui": {
                "theme": "light",
                "language": "en",
                "currency": "USD",
                "units": "imperial"
            },
            "api": {
                "base_url": "/",
                "version": "1.0.0",
                "timeout": 30000,
                "retry_attempts": 3
            },
            "integrations": {
                "weather_api": True,
                "utility_api": False,
                "smart_home": False,
                "iot_devices": False
            }
        }
        
        return JSONResponse(content=config)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

# Health check for web routes
@web_router.get("/health")
async def web_health_check():
    """Health check specifically for web routes"""
    return {
        "status": "healthy",
        "service": "web_routes",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": [
            "/web/dashboard",
            "/web/preferences",
            "/web/export",
            "/web/integration-status",
            "/web/config",
            "/web/health"
        ]
    }

# Frontend development helper endpoints
@web_router.get("/dev/endpoints")
async def get_all_endpoints():
    """Get all available endpoints for frontend development"""
    try:
        all_endpoints = {
            "core": {
                "root": "/",
                "health": "/health",
                "status": "/status",
                "docs": "/docs"
            },
            "web_application": {
                "dashboard": "/web/dashboard",
                "preferences": "/web/preferences",
                "export": "/web/export",
                "integration_status": "/web/integration-status",
                "config": "/web/config",
                "health": "/web/health"
            },
            "energy_systems": {
                "appliance_health": "/appliance-health/*",
                "solar_calculator": "/solar-calculator/*",
                "smart_analysis": "/smart-analysis/*",
                "bill_simulation": "/bill-simulation/*",
                "carbon_tracker": "/carbon-tracker/*"
            }
        }
        
        return {
            "message": "All available endpoints",
            "endpoints": all_endpoints,
            "total_endpoints": sum(len(endpoints) for endpoints in all_endpoints.values()),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get endpoints: {str(e)}")

@web_router.get("/dev/sample-data")
async def get_sample_data():
    """Get sample data for frontend development and testing"""
    try:
        sample_data = {
            "user_profile": {
                "id": "user_123",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "location": "New York, NY",
                "energy_company": "ConEdison",
                "monthly_budget": 150.0
            },
            "appliances": [
                {
                    "id": "app_001",
                    "name": "Refrigerator",
                    "type": "kitchen",
                    "power_rating": 150,
                    "health_score": 85,
                    "last_maintenance": "2024-01-01",
                    "next_maintenance": "2024-04-01"
                },
                {
                    "id": "app_002",
                    "name": "Air Conditioner",
                    "type": "hvac",
                    "power_rating": 3500,
                    "health_score": 92,
                    "last_maintenance": "2024-01-15",
                    "next_maintenance": "2024-07-15"
                }
            ],
            "energy_usage": {
                "current_month": 450.5,
                "previous_month": 480.2,
                "trend": "decreasing",
                "daily_average": 15.0,
                "peak_hours": "2:00 PM - 6:00 PM"
            },
            "solar_potential": {
                "roof_area": 1200,
                "sunlight_hours": 4.5,
                "estimated_savings": 1200,
                "payback_period": 6.6,
                "roi_percentage": 15.2
            }
        }
        
        return {
            "message": "Sample data for frontend development",
            "data": sample_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sample data: {str(e)}")

@web_router.post("/dev/test-connection")
async def test_frontend_connection():
    """Test endpoint for frontend connection verification"""
    return {
        "message": "Frontend connection successful!",
        "status": "connected",
        "timestamp": "2024-01-01T00:00:00Z",
        "server_info": {
            "name": "Smart Energy Management System",
            "version": "1.0.0",
            "environment": "development"
        }
    }

@web_router.get("/dev/error-test")
async def test_error_handling():
    """Test endpoint to verify error handling in frontend"""
    import random
    
    # Randomly return different error types for testing
    error_types = [
        {"status_code": 400, "message": "Bad Request - Invalid parameters"},
        {"status_code": 404, "message": "Not Found - Resource doesn't exist"},
        {"status_code": 500, "message": "Internal Server Error - Something went wrong"}
    ]
    
    error = random.choice(error_types)
    raise HTTPException(status_code=error["status_code"], detail=error["message"])
