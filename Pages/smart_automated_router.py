from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import json
from smart_automated_system import SmartAutomatedSystem

# Initialize the router
smart_automated_router = APIRouter(prefix="/smart-analysis", tags=["Smart Automated Analysis"])

# Initialize the smart system
smart_system = SmartAutomatedSystem()

# Pydantic models for request/response
class SmartAnalysisRequest(BaseModel):
    """Minimal user input for smart analysis"""
    # Optional: Override auto-detected location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    
    # Optional: Override auto-detected property type
    property_type: Optional[str] = None  # single_family, townhouse, apartment, commercial
    
    # Optional: Override auto-detected roof area
    roof_area_m2: Optional[float] = None
    
    # Optional: Override auto-detected electricity rate
    electricity_rate: Optional[float] = None
    
    # Optional: API keys for enhanced data
    google_maps_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    utility_api_key: Optional[str] = None
    nrel_api_key: Optional[str] = None

class SmartAnalysisResponse(BaseModel):
    """Complete smart analysis response"""
    success: bool
    message: str
    analysis: Dict
    recommendations: Dict
    next_steps: list

# Endpoints
@smart_automated_router.post("/one-click", response_model=SmartAnalysisResponse)
async def one_click_smart_analysis(request: SmartAnalysisRequest):
    """
    One-click smart analysis - automatically detects everything and provides recommendations
    """
    try:
        print("🚀 Starting One-Click Smart Analysis...")
        
        # Step 1: Configure API keys if provided
        if any([request.google_maps_api_key, request.openweather_api_key, 
                request.utility_api_key, request.nrel_api_key]):
            smart_system.set_api_keys(
                google_maps=request.google_maps_api_key,
                openweather=request.openweather_api_key,
                utility_api=request.utility_api_key,
                nrel=request.nrel_api_key
            )
        
        # Step 2: Override location if provided
        if request.latitude and request.longitude:
            smart_system.location_data = {
                'latitude': request.latitude,
                'longitude': request.longitude,
                'city': request.city or 'Unknown',
                'state': request.state or 'Unknown',
                'country': request.country or 'US',
                'source': 'User Provided'
            }
            print(f"📍 Using user-provided location: {request.city}, {request.state}")
        
        # Step 3: Run smart analysis
        analysis = smart_system.smart_analysis()
        
        # Step 4: Override auto-detected values if user provided them
        if request.property_type:
            analysis['property']['type'] = request.property_type
            analysis['property']['estimated_roof_area_m2'] = request.roof_area_m2 or analysis['property']['estimated_roof_area_m2']
        
        if request.roof_area_m2:
            analysis['property']['estimated_roof_area_m2'] = request.roof_area_m2
        
        if request.electricity_rate:
            analysis['utilities']['current_rate'] = request.electricity_rate
            analysis['utilities']['source'] = 'User Provided'
        
        # Step 5: Extract key information for response
        recommendations = analysis['recommendations']
        next_steps = analysis['recommendations']['next_steps']
        
        # Step 6: Format response
        response = SmartAnalysisResponse(
            success=True,
            message="Smart analysis completed successfully!",
            analysis=analysis,
            recommendations=recommendations,
            next_steps=next_steps
        )
        
        print("✅ One-click analysis completed successfully!")
        return response
        
    except Exception as e:
        print(f"❌ Error in smart analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Smart analysis failed: {str(e)}")

@smart_automated_router.get("/demo")
async def demo_smart_analysis():
    """
    Demo endpoint - shows what the smart analysis can do
    """
    try:
        # Run analysis with default settings
        analysis = smart_system.smart_analysis()
        
        return {
            "message": "Demo smart analysis completed",
            "demo_data": {
                "location": analysis['location'],
                "property_type": analysis['property']['type'],
                "roof_area": f"{analysis['property']['estimated_roof_area_m2']} m²",
                "electricity_rate": f"${analysis['utilities']['current_rate']}/kWh",
                "solar_score": f"{analysis['recommendations']['solar_feasibility']['score']}/100",
                "solar_rating": analysis['recommendations']['solar_feasibility']['rating'],
                "appliance_priority": analysis['recommendations']['appliance_health']['priority'],
                "annual_savings_potential": f"${analysis['recommendations']['cost_savings']['annual_estimate']}"
            },
            "sample_request": {
                "description": "Send this to /one-click for custom analysis",
                "example": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "city": "New York",
                    "property_type": "single_family",
                    "roof_area_m2": 120
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@smart_automated_router.get("/health")
async def health_check():
    """Health check for the smart automated system"""
    return {
        "status": "healthy",
        "service": "smart_automated_analysis",
        "features": [
            "Automatic location detection",
            "Property type detection",
            "Roof area estimation",
            "Electricity rate detection",
            "Weather data integration",
            "Smart recommendations",
            "One-click analysis"
        ],
        "data_sources": [
            "IP Geolocation (free)",
            "OpenStreetMap (free)",
            "Regional utility databases",
            "Seasonal weather patterns",
            "Property type databases"
        ]
    }

@smart_automated_router.get("/capabilities")
async def get_capabilities():
    """Get detailed information about system capabilities"""
    return {
        "automated_features": {
            "location_detection": {
                "method": "IP Geolocation",
                "accuracy": "City/State level",
                "fallback": "Default location (NYC)"
            },
            "property_analysis": {
                "detection_method": "Address keyword analysis",
                "supported_types": ["single_family", "townhouse", "apartment", "commercial"],
                "roof_estimation": "Based on property type + regional averages"
            },
            "utility_data": {
                "rate_detection": "Regional databases + seasonal adjustments",
                "coverage": "US regions (Northeast, West Coast, Southwest, etc.)",
                "seasonal_factors": "Summer/Winter rate variations"
            },
            "weather_integration": {
                "primary": "OpenWeatherMap API (if key provided)",
                "fallback": "Seasonal patterns based on latitude",
                "factors": "Temperature, humidity, cloud cover, wind"
            }
        },
        "analysis_outputs": {
            "solar_feasibility": "Score 0-100 with rating and priority",
            "appliance_health": "Priority level and focus areas",
            "cost_savings": "Annual potential and payback estimates",
            "recommendations": "Actionable items and next steps"
        },
        "user_input_options": {
            "minimal": "Just call /one-click with empty body",
            "custom_location": "Override auto-detected coordinates",
            "custom_property": "Specify property type and roof area",
            "custom_rates": "Override electricity rates",
            "enhanced_data": "Provide API keys for real-time data"
        }
    }
