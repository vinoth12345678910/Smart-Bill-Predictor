from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from carbon_tracker import CarbonFootprintTracker
import pandas as pd

# Initialize the router
carbon_tracker_router = APIRouter(prefix="/carbon-tracker", tags=["Carbon Footprint Tracking"])

# Initialize the carbon tracker
carbon_tracker = CarbonFootprintTracker()

# Pydantic models for request/response
class ConsumptionDataRequest(BaseModel):
    """Request model for adding consumption data"""
    date: str  # YYYY-MM-DD format
    usage_kwh: float
    location: Optional[Dict] = None
    energy_source: str = 'grid_mix'
    additional_data: Optional[Dict] = None

class TransportationDataRequest(BaseModel):
    """Request model for adding transportation data"""
    date: str  # YYYY-MM-DD format
    transport_type: str  # car_gasoline, car_electric, bus, train, plane_domestic, etc.
    distance_miles: float
    passengers: int = 1
    location: Optional[Dict] = None

class LifestyleDataRequest(BaseModel):
    """Request model for adding lifestyle data"""
    date: str  # YYYY-MM-DD format
    lifestyle_choice: str  # meat_heavy, vegetarian, vegan, fast_fashion, etc.
    quantity: int = 1
    location: Optional[Dict] = None

class CarbonSummaryRequest(BaseModel):
    """Request model for getting carbon summary"""
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None    # YYYY-MM-DD format

class OffsetStrategyRequest(BaseModel):
    """Request model for offset strategy suggestions"""
    target_reduction: Optional[float] = None  # kg CO2

class ProgressReportRequest(BaseModel):
    """Request model for progress reports"""
    baseline_date: Optional[str] = None  # YYYY-MM format

# API Endpoints

@carbon_tracker_router.post("/consumption")
async def add_consumption_data(request: ConsumptionDataRequest):
    """Add electricity consumption data for carbon tracking"""
    try:
        record = carbon_tracker.add_consumption_data(
            date=request.date,
            usage_kwh=request.usage_kwh,
            location=request.location,
            energy_source=request.energy_source,
            additional_data=request.additional_data
        )
        
        return {
            "message": "Consumption data added successfully",
            "record": record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add consumption data: {str(e)}")

@carbon_tracker_router.post("/transportation")
async def add_transportation_data(request: TransportationDataRequest):
    """Add transportation emissions data"""
    try:
        record = carbon_tracker.add_transportation_data(
            date=request.date,
            transport_type=request.transport_type,
            distance_miles=request.distance_miles,
            passengers=request.passengers,
            location=request.location
        )
        
        if record:
            return {
                "message": "Transportation data added successfully",
                "record": record
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid transport type")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add transportation data: {str(e)}")

@carbon_tracker_router.post("/lifestyle")
async def add_lifestyle_data(request: LifestyleDataRequest):
    """Add lifestyle emissions data"""
    try:
        record = carbon_tracker.add_lifestyle_data(
            date=request.date,
            lifestyle_choice=request.lifestyle_choice,
            quantity=request.quantity,
            location=request.location
        )
        
        if record:
            return {
                "message": "Lifestyle data added successfully",
                "record": record
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid lifestyle choice")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add lifestyle data: {str(e)}")

@carbon_tracker_router.post("/summary")
async def get_carbon_summary(request: CarbonSummaryRequest):
    """Get comprehensive carbon footprint summary"""
    try:
        summary = carbon_tracker.get_carbon_summary(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "message": "Carbon summary generated successfully",
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@carbon_tracker_router.post("/offset-strategy")
async def suggest_offset_strategy(request: OffsetStrategyRequest):
    """Suggest optimal offset strategy based on current footprint"""
    try:
        strategy = carbon_tracker.suggest_offset_strategy(
            target_reduction=request.target_reduction
        )
        
        return {
            "message": "Offset strategy generated successfully",
            "strategy": strategy
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate strategy: {str(e)}")

@carbon_tracker_router.post("/progress-report")
async def get_progress_report(request: ProgressReportRequest):
    """Generate progress report comparing current vs baseline"""
    try:
        report = carbon_tracker.get_progress_report(
            baseline_date=request.baseline_date
        )
        
        return {
            "message": "Progress report generated successfully",
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@carbon_tracker_router.get("/emission-factors")
async def get_emission_factors():
    """Get available emission factors by region and energy source"""
    try:
        factors = carbon_tracker.emission_factors
        
        return {
            "message": "Emission factors retrieved successfully",
            "factors": factors,
            "note": "Values in kg CO2 per kWh"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emission factors: {str(e)}")

@carbon_tracker_router.get("/transport-factors")
async def get_transport_factors():
    """Get transportation emission factors"""
    try:
        factors = carbon_tracker.transport_factors
        
        return {
            "message": "Transport factors retrieved successfully",
            "factors": factors,
            "note": "Values in kg CO2 per mile"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transport factors: {str(e)}")

@carbon_tracker_router.get("/lifestyle-factors")
async def get_lifestyle_factors():
    """Get lifestyle emission factors"""
    try:
        factors = carbon_tracker.lifestyle_factors
        
        return {
            "message": "Lifestyle factors retrieved successfully",
            "factors": factors,
            "note": "Values in kg CO2 per unit"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lifestyle factors: {str(e)}")

@carbon_tracker_router.get("/offset-projects")
async def get_offset_projects():
    """Get available offset project types and their effectiveness"""
    try:
        projects = carbon_tracker.offset_projects
        
        return {
            "message": "Offset projects retrieved successfully",
            "projects": projects
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get offset projects: {str(e)}")

@carbon_tracker_router.post("/export")
async def export_tracking_data(format: str = 'json', filename: str = None):
    """Export tracking data in various formats"""
    try:
        result = carbon_tracker.export_data(format=format, filename=filename)
        
        return {
            "message": "Data exported successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

@carbon_tracker_router.get("/tracking-history")
async def get_tracking_history(limit: int = 100):
    """Get recent tracking history"""
    try:
        if not carbon_tracker.tracking_history:
            return {
                "message": "No tracking data available",
                "history": []
            }
        
        # Get most recent records
        history = carbon_tracker.tracking_history[-limit:] if limit > 0 else carbon_tracker.tracking_history
        
        return {
            "message": "Tracking history retrieved successfully",
            "total_records": len(carbon_tracker.tracking_history),
            "returned_records": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@carbon_tracker_router.get("/quick-calculate")
async def quick_calculate_emissions(usage_kwh: float, location_country: str = 'US', 
                                  location_region: str = 'default', energy_source: str = 'grid_mix'):
    """Quick calculation of emissions without storing data"""
    try:
        location = {'country': location_country, 'region': location_region}
        emissions = carbon_tracker.calculate_emissions(usage_kwh, location, energy_source)
        
        return {
            "message": "Quick calculation completed",
            "calculation": emissions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate emissions: {str(e)}")

@carbon_tracker_router.get("/examples")
async def get_data_examples():
    """Get example data entries for testing"""
    examples = {
        "consumption": {
            "date": "2024-01-15",
            "usage_kwh": 1200,
            "location": {"country": "US", "region": "northeast"},
            "energy_source": "grid_mix",
            "additional_data": {"peak_hours": 8, "off_peak_hours": 16}
        },
        "transportation": {
            "date": "2024-01-15",
            "transport_type": "car_gasoline",
            "distance_miles": 25,
            "passengers": 1,
            "location": {"country": "US", "region": "northeast"}
        },
        "lifestyle": {
            "date": "2024-01-15",
            "lifestyle_choice": "meat_moderate",
            "quantity": 1,
            "location": {"country": "US", "region": "northeast"}
        }
    }
    
    return {
        "message": "Example data entries",
        "examples": examples,
        "note": "Use these as templates for adding real data"
    }

@carbon_tracker_router.get("/health")
async def health_check():
    """Health check for the carbon tracker service"""
    try:
        tracking_records = len(carbon_tracker.tracking_history)
        data_status = "has_data" if tracking_records > 0 else "no_data"
        
        return {
            "service": "Carbon Footprint Tracker",
            "status": "healthy",
            "tracking_records": tracking_records,
            "data_status": data_status,
            "features": [
                "Electricity consumption tracking",
                "Transportation emissions",
                "Lifestyle choices",
                "Offset strategy suggestions",
                "Progress reporting",
                "Data export"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@carbon_tracker_router.delete("/clear-data")
async def clear_tracking_data():
    """Clear all tracking data (use with caution)"""
    try:
        record_count = len(carbon_tracker.tracking_history)
        carbon_tracker.tracking_history = []
        carbon_tracker.consumption_data = pd.DataFrame()
        
        return {
            "message": "All tracking data cleared successfully",
            "records_cleared": record_count,
            "warning": "This action cannot be undone"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")
