from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from bill_simulation import BillSimulationEngine

# Initialize the router
bill_simulation_router = APIRouter(prefix="/bill-simulation", tags=["Bill Simulation & Carbon Tracking"])

# Initialize the simulation engine
simulation_engine = BillSimulationEngine()

# Pydantic models for request/response
class SimulationRequest(BaseModel):
    """Request model for bill simulation"""
    months_ahead: int = 12
    scenarios: Optional[Dict] = None
    location: Optional[Dict] = None

class ApplianceChange(BaseModel):
    """Model for appliance changes in scenarios"""
    type: str  # 'add', 'remove', 'replace'
    start_date: str  # YYYY-MM format
    usage_kwh: float
    old_usage: Optional[float] = None  # For replacement scenarios
    new_usage: Optional[float] = None  # For replacement scenarios

class TariffChange(BaseModel):
    """Model for tariff changes in scenarios"""
    start_date: str  # YYYY-MM format
    new_rate: float  # New rate per kWh

class ScenarioConfig(BaseModel):
    """Complete scenario configuration"""
    appliance_changes: Optional[List[ApplianceChange]] = []
    tariff_changes: Optional[List[TariffChange]] = []
    efficiency_improvements: float = 0.0  # Percentage improvement (0.0 to 1.0)

class CarbonFootprintRequest(BaseModel):
    """Request model for carbon footprint calculation"""
    usage_kwh: float
    location: Optional[Dict] = None

class HistoricalDataRequest(BaseModel):
    """Request model for loading historical data"""
    data_source: str = 'sample'  # 'sample' or 'csv'
    csv_file_path: Optional[str] = None

# API Endpoints

@bill_simulation_router.post("/load-data")
async def load_historical_data(request: HistoricalDataRequest):
    """Load historical usage data for simulation"""
    try:
        data = simulation_engine.load_historical_data(request.data_source)
        return {
            "message": "Historical data loaded successfully",
            "records_count": len(data),
            "data_preview": data.head().to_dict('records') if not data.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

@bill_simulation_router.post("/train-model")
async def train_simulation_model(features: Optional[List[str]] = None):
    """Train the bill simulation model"""
    try:
        if simulation_engine.historical_data.empty:
            # Load sample data if none available
            simulation_engine.load_historical_data('sample')
        
        success = simulation_engine.train_simulation_model(features)
        
        if success:
            return {
                "message": "Model trained successfully",
                "model_type": "Random Forest Regressor",
                "features_used": features or ['month', 'avg_temperature', 'year'],
                "historical_records": len(simulation_engine.historical_data)
            }
        else:
            raise HTTPException(status_code=500, detail="Model training failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@bill_simulation_router.post("/simulate")
async def simulate_bills(request: SimulationRequest):
    """Run bill simulation with scenarios"""
    try:
        if not simulation_engine.simulation_model:
            # Auto-train model if not trained
            simulation_engine.load_historical_data('sample')
            simulation_engine.train_simulation_model()
        
        # Convert Pydantic models to dict for simulation
        scenarios_dict = None
        if request.scenarios:
            scenarios_dict = request.scenarios.dict()
        
        results = simulation_engine.simulate_bills(
            months_ahead=request.months_ahead,
            scenarios=scenarios_dict
        )
        
        return {
            "message": "Simulation completed successfully",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@bill_simulation_router.post("/carbon-footprint")
async def calculate_carbon_footprint(request: CarbonFootprintRequest):
    """Calculate carbon footprint from electricity usage"""
    try:
        footprint = simulation_engine.get_carbon_footprint(
            usage_kwh=request.usage_kwh,
            location=request.location
        )
        
        return {
            "message": "Carbon footprint calculated successfully",
            "footprint": footprint
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@bill_simulation_router.get("/scenarios/examples")
async def get_scenario_examples():
    """Get example scenario configurations"""
    examples = {
        "appliance_changes": [
            {
                "type": "add",
                "start_date": "2024-06",
                "usage_kwh": 200,
                "description": "Add new air conditioner"
            },
            {
                "type": "replace",
                "start_date": "2024-09",
                "old_usage": 150,
                "new_usage": 80,
                "description": "Replace old refrigerator with energy-efficient model"
            }
        ],
        "tariff_changes": [
            {
                "start_date": "2024-07",
                "new_rate": 0.18,
                "description": "Summer rate increase"
            }
        ],
        "efficiency_improvements": [
            {
                "value": 0.15,
                "description": "15% efficiency improvement from insulation upgrade"
            }
        ]
    }
    
    return {
        "message": "Example scenarios",
        "examples": examples
    }

@bill_simulation_router.get("/historical-data/summary")
async def get_historical_summary():
    """Get summary of loaded historical data"""
    try:
        if simulation_engine.historical_data.empty:
            return {
                "message": "No historical data loaded",
                "data_available": False
            }
        
        data = simulation_engine.historical_data
        
        summary = {
            "total_records": len(data),
            "date_range": {
                "start": data['date'].min().strftime('%Y-%m-%d'),
                "end": data['date'].max().strftime('%Y-%m-%d')
            },
            "usage_statistics": {
                "total_kwh": round(data['usage_kwh'].sum(), 1),
                "avg_monthly_kwh": round(data['usage_kwh'].mean(), 1),
                "min_monthly_kwh": round(data['usage_kwh'].min(), 1),
                "max_monthly_kwh": round(data['usage_kwh'].max(), 1)
            },
            "bill_statistics": {
                "total_bills": round(data['bill_amount'].sum(), 2),
                "avg_monthly_bill": round(data['bill_amount'].mean(), 2),
                "min_monthly_bill": round(data['bill_amount'].min(), 2),
                "max_monthly_bill": round(data['bill_amount'].max(), 2)
            },
            "seasonal_patterns": {
                "winter_avg": round(data[data['month'].isin([12, 1, 2])]['usage_kwh'].mean(), 1),
                "spring_avg": round(data[data['month'].isin([3, 4, 5])]['usage_kwh'].mean(), 1),
                "summer_avg": round(data[data['month'].isin([6, 7, 8])]['usage_kwh'].mean(), 1),
                "fall_avg": round(data[data['month'].isin([9, 10, 11])]['usage_kwh'].mean(), 1)
            }
        }
        
        return {
            "message": "Historical data summary",
            "data_available": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@bill_simulation_router.get("/weather-forecast")
async def get_weather_forecast(location: Optional[Dict] = None, months_ahead: int = 12):
    """Get weather forecast for simulation"""
    try:
        if not location:
            location = {'country': 'US', 'region': 'default'}
        
        forecast = simulation_engine.get_weather_forecast(location, months_ahead)
        
        return {
            "message": "Weather forecast retrieved",
            "location": location,
            "months_ahead": months_ahead,
            "forecast": forecast
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")

@bill_simulation_router.get("/emission-factors")
async def get_emission_factors():
    """Get available emission factors by region"""
    try:
        factors = simulation_engine.default_emission_factors
        
        return {
            "message": "Emission factors by region",
            "factors": factors,
            "note": "Values in kg CO2 per kWh"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emission factors: {str(e)}")

@bill_simulation_router.get("/health")
async def health_check():
    """Health check for the bill simulation service"""
    try:
        model_status = "trained" if simulation_engine.simulation_model else "not_trained"
        data_status = "loaded" if not simulation_engine.historical_data.empty else "not_loaded"
        
        return {
            "service": "Bill Simulation Engine",
            "status": "healthy",
            "model_status": model_status,
            "data_status": data_status,
            "historical_records": len(simulation_engine.historical_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
