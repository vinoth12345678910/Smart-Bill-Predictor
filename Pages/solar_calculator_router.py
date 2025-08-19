from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from solar_calculator import SolarFeasibilityCalculator

# Initialize the router
solar_calculator_router = APIRouter(prefix="/solar-calculator", tags=["Solar Feasibility & ROI Calculator"])

# Initialize the calculator
calculator = SolarFeasibilityCalculator()

# Pydantic models for request/response
class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    city: str
    country: str = "US"

class PanelSpecsRequest(BaseModel):
    panel_type: str = "monocrystalline"
    custom_efficiency: Optional[float] = None
    custom_cost: Optional[float] = None

class TariffRequest(BaseModel):
    electricity_rate: float
    rate_escalation: float = 0.03

class SystemAnalysisRequest(BaseModel):
    roof_area: float
    panel_type: str = "monocrystalline"
    installation_type: str = "residential_medium"
    years: int = 25

class NRELRequest(BaseModel):
    api_key: str

# Endpoints
@solar_calculator_router.post("/location", response_model=Dict)
async def set_location(location: LocationRequest):
    """Set location for solar calculations"""
    try:
        calculator.set_location(
            latitude=location.latitude,
            longitude=location.longitude,
            city=location.city,
            country=location.country
        )
        
        return {
            "message": "Location set successfully",
            "location": {
                "city": location.city,
                "country": location.country,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/irradiance/nrel", response_model=Dict)
async def fetch_nrel_data(request: NRELRequest):
    """Fetch solar irradiance data from NREL API"""
    try:
        irradiance_data = calculator.fetch_solar_irradiance_nrel(request.api_key)
        
        return {
            "message": "Solar irradiance data fetched successfully",
            "data": irradiance_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/panels", response_model=Dict)
async def set_panel_specifications(specs: PanelSpecsRequest):
    """Set solar panel specifications"""
    try:
        calculator.set_panel_specifications(
            panel_type=specs.panel_type,
            custom_efficiency=specs.custom_efficiency,
            custom_cost=specs.custom_cost
        )
        
        return {
            "message": "Panel specifications set successfully",
            "panel_type": specs.panel_type,
            "efficiency": calculator.panel_efficiency_data.get('efficiency'),
            "cost_per_watt": calculator.panel_efficiency_data.get('cost_per_watt')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/tariff", response_model=Dict)
async def set_tariff_data(tariff: TariffRequest):
    """Set electricity tariff data for ROI calculations"""
    try:
        calculator.set_tariff_data(
            electricity_rate=tariff.electricity_rate,
            rate_escalation=tariff.rate_escalation
        )
        
        return {
            "message": "Tariff data set successfully",
            "current_rate": tariff.electricity_rate,
            "escalation_rate": tariff.rate_escalation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/system-size", response_model=Dict)
async def calculate_system_size(request: SystemAnalysisRequest):
    """Calculate optimal solar system size based on roof area"""
    try:
        system_size = calculator.calculate_system_size(
            roof_area=request.roof_area,
            panel_type=request.panel_type
        )
        
        return {
            "message": "System size calculated successfully",
            "system_size": system_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/energy-production", response_model=Dict)
async def calculate_energy_production(request: SystemAnalysisRequest):
    """Calculate energy production and degradation over time"""
    try:
        # First calculate system size
        system_size = calculator.calculate_system_size(
            roof_area=request.roof_area,
            panel_type=request.panel_type
        )
        
        # Then calculate energy production
        production = calculator.calculate_energy_production(
            system_capacity_kw=system_size['effective_capacity_kw'],
            panel_type=request.panel_type,
            years=request.years
        )
        
        return {
            "message": "Energy production calculated successfully",
            "system_size": system_size,
            "energy_production": production
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/costs", response_model=Dict)
async def calculate_costs(request: SystemAnalysisRequest):
    """Calculate total system costs including installation and maintenance"""
    try:
        # First calculate system size
        system_size = calculator.calculate_system_size(
            roof_area=request.roof_area,
            panel_type=request.panel_type
        )
        
        # Then calculate costs
        costs = calculator.calculate_costs(
            system_capacity_kw=system_size['effective_capacity_kw'],
            installation_type=request.installation_type
        )
        
        return {
            "message": "Costs calculated successfully",
            "system_size": system_size,
            "costs": costs
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/roi", response_model=Dict)
async def calculate_roi(request: SystemAnalysisRequest):
    """Calculate ROI, payback period, and cash flow analysis"""
    try:
        # First calculate system size
        system_size = calculator.calculate_system_size(
            roof_area=request.roof_area,
            panel_type=request.panel_type
        )
        
        # Then calculate ROI
        roi = calculator.calculate_roi(
            system_capacity_kw=system_size['effective_capacity_kw'],
            installation_type=request.installation_type,
            years=request.years
        )
        
        return {
            "message": "ROI analysis completed successfully",
            "system_size": system_size,
            "roi_analysis": roi
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.post("/report", response_model=Dict)
async def generate_comprehensive_report(request: SystemAnalysisRequest):
    """Generate comprehensive solar feasibility report"""
    try:
        report = calculator.generate_report(
            roof_area=request.roof_area,
            panel_type=request.panel_type,
            installation_type=request.installation_type
        )
        
        return {
            "message": "Comprehensive report generated successfully",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.get("/available-panels", response_model=Dict)
async def get_available_panel_types():
    """Get available solar panel types and specifications"""
    try:
        return {
            "message": "Available panel types retrieved successfully",
            "panel_types": calculator.default_panels
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.get("/installation-types", response_model=Dict)
async def get_installation_types():
    """Get available installation types and costs"""
    try:
        return {
            "message": "Installation types retrieved successfully",
            "installation_types": calculator.installation_costs
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.get("/current-config", response_model=Dict)
async def get_current_configuration():
    """Get current calculator configuration"""
    try:
        return {
            "message": "Current configuration retrieved successfully",
            "configuration": {
                "location": calculator.location_data,
                "solar_data": calculator.solar_irradiance_data,
                "panel_specs": calculator.panel_efficiency_data,
                "tariff_data": calculator.tariff_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@solar_calculator_router.get("/health")
async def health_check():
    """Health check for the solar calculator service"""
    return {
        "status": "healthy",
        "service": "solar_calculator",
        "location_set": bool(calculator.location_data),
        "panels_set": bool(calculator.panel_efficiency_data),
        "tariff_set": bool(calculator.tariff_data)
    }
