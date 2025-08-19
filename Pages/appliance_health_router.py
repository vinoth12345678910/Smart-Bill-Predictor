from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
from appliance_health_prediction import ApplianceHealthPredictor

# Initialize the router
appliance_health_router = APIRouter(prefix="/appliance-health", tags=["Appliance Health Prediction"])

# Initialize the predictor
predictor = ApplianceHealthPredictor()

# Pydantic models for request/response
class ApplianceCreate(BaseModel):
    appliance_id: str
    brand: str
    model: str
    power_rating: float
    category: str
    installation_date: str

class SensorReading(BaseModel):
    appliance_id: str
    timestamp: str
    energy_usage: float
    power_factor: float = 1.0
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    noise_level: Optional[float] = None

class ManualReading(BaseModel):
    appliance_id: str
    energy_usage: float
    power_factor: float = 1.0
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    noise_level: Optional[float] = None
    notes: Optional[str] = None

class HealthStatus(BaseModel):
    appliance_id: str
    timestamp: str
    is_anomaly: bool
    anomaly_score: float
    health_score: float
    recommendations: List[str]
    severity: str

class FailurePrediction(BaseModel):
    appliance_id: str
    failure_probability: float
    time_to_failure: str
    age_years: float
    energy_trend: float
    health_trend: float

# In-memory storage for demo purposes (in production, use a database)
appliances = {}
readings_history = {}

@appliance_health_router.post("/appliances", response_model=Dict)
async def create_appliance(appliance: ApplianceCreate):
    """Add a new appliance to the health monitoring system"""
    try:
        predictor.add_appliance(
            appliance_id=appliance.appliance_id,
            brand=appliance.brand,
            model=appliance.model,
            power_rating=appliance.power_rating,
            category=appliance.category,
            installation_date=appliance.installation_date
        )
        
        # Store in memory
        appliances[appliance.appliance_id] = appliance.dict()
        
        return {
            "message": "Appliance added successfully",
            "appliance_id": appliance.appliance_id,
            "status": "monitoring_active"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.get("/appliances", response_model=List[Dict])
async def list_appliances():
    """List all monitored appliances"""
    return list(appliances.values())

@appliance_health_router.get("/appliances/{appliance_id}", response_model=Dict)
async def get_appliance_status(appliance_id: str):
    """Get current status and health information for an appliance"""
    try:
        status = predictor.get_appliance_status(appliance_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@appliance_health_router.post("/readings/iot", response_model=List[HealthStatus])
async def record_iot_reading(reading: SensorReading):
    """Record sensor reading from IoT device/smart plug"""
    try:
        # Validate appliance exists
        if reading.appliance_id not in appliances:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Record the reading
        reading_record = predictor.record_reading(
            appliance_id=reading.appliance_id,
            timestamp=reading.timestamp,
            energy_usage=reading.energy_usage,
            power_factor=reading.power_factor,
            temperature=reading.temperature,
            vibration=reading.vibration,
            noise_level=reading.noise_level
        )
        
        # Store in history
        if reading.appliance_id not in readings_history:
            readings_history[reading.appliance_id] = []
        readings_history[reading.appliance_id].append(reading_record)
        
        # Detect anomalies if model is trained
        if predictor.is_trained:
            anomalies = predictor.detect_anomalies([reading_record])
            return anomalies
        else:
            # Return basic reading info if model not trained
            return [{
                "appliance_id": reading.appliance_id,
                "timestamp": reading.timestamp,
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "health_score": 100.0,
                "recommendations": ["Model not yet trained"],
                "severity": "Unknown"
            }]
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.post("/readings/manual", response_model=List[HealthStatus])
async def record_manual_reading(reading: ManualReading):
    """Record manual reading input by user"""
    try:
        # Validate appliance exists
        if reading.appliance_id not in appliances:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Use current timestamp
        timestamp = datetime.now().isoformat()
        
        # Record the reading
        reading_record = predictor.record_reading(
            appliance_id=reading.appliance_id,
            timestamp=timestamp,
            energy_usage=reading.energy_usage,
            power_factor=reading.power_factor,
            temperature=reading.temperature,
            vibration=reading.vibration,
            noise_level=reading.noise_level
        )
        
        # Store in history
        if reading.appliance_id not in readings_history:
            readings_history[reading.appliance_id] = []
        readings_history[reading.appliance_id].append(reading_record)
        
        # Detect anomalies if model is trained
        if predictor.is_trained:
            anomalies = predictor.detect_anomalies([reading_record])
            return anomalies
        else:
            # Return basic reading info if model not trained
            return [{
                "appliance_id": reading.appliance_id,
                "timestamp": timestamp,
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "health_score": 100.0,
                "recommendations": ["Model not yet trained"],
                "severity": "Unknown"
            }]
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.post("/train", response_model=Dict)
async def train_model():
    """Train the anomaly detection model on historical data"""
    try:
        # Collect all historical readings
        all_readings = []
        for appliance_readings in readings_history.values():
            all_readings.extend(appliance_readings)
        
        if len(all_readings) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient data for training. Need at least 10 readings."
            )
        
        # Train the model
        predictor.train_anomaly_detector(all_readings)
        
        return {
            "message": "Model trained successfully",
            "training_samples": len(all_readings),
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.get("/health/{appliance_id}", response_model=List[HealthStatus])
async def get_appliance_health_history(appliance_id: str, limit: int = 50):
    """Get health history for an appliance"""
    if appliance_id not in readings_history:
        raise HTTPException(status_code=404, detail="No readings found for appliance")
    
    # Get recent readings
    recent_readings = readings_history[appliance_id][-limit:]
    
    if not predictor.is_trained:
        # Return basic info if model not trained
        return [{
            "appliance_id": appliance_id,
            "timestamp": r["timestamp"],
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "health_score": 100.0,
            "recommendations": ["Model not yet trained"],
            "severity": "Unknown"
        } for r in recent_readings]
    
    # Detect anomalies
    anomalies = predictor.detect_anomalies(recent_readings)
    return anomalies

@appliance_health_router.get("/predict/{appliance_id}", response_model=FailurePrediction)
async def predict_failure(appliance_id: str, days_back: int = 30):
    """Predict failure probability for an appliance"""
    try:
        if appliance_id not in readings_history:
            raise HTTPException(status_code=404, detail="No readings found for appliance")
        
        # Get recent readings within specified time period
        recent_readings = readings_history[appliance_id]
        
        # Filter by time if needed (simplified for demo)
        if len(recent_readings) > days_back:
            recent_readings = recent_readings[-days_back:]
        
        # Predict failure
        prediction = predictor.predict_failure_probability(appliance_id, recent_readings)
        
        return FailurePrediction(
            appliance_id=appliance_id,
            **prediction
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.get("/dashboard", response_model=Dict)
async def get_health_dashboard():
    """Get overall health dashboard for all appliances"""
    try:
        dashboard = {
            "total_appliances": len(appliances),
            "monitoring_active": len([a for a in appliances.values() if a.get("status") == "monitoring_active"]),
            "appliances": []
        }
        
        for appliance_id in appliances:
            try:
                status = predictor.get_appliance_status(appliance_id)
                
                # Get recent health score
                recent_health = 100.0
                if appliance_id in readings_history and readings_history[appliance_id]:
                    recent_reading = readings_history[appliance_id][-1]
                    if predictor.is_trained:
                        anomalies = predictor.detect_anomalies([recent_reading])
                        if anomalies:
                            recent_health = anomalies[0]["health_score"]
                
                appliance_summary = {
                    "appliance_id": appliance_id,
                    "brand": status["brand"],
                    "model": status["model"],
                    "category": status["category"],
                    "current_health_score": recent_health,
                    "status": "Good" if recent_health >= 80 else "Fair" if recent_health >= 60 else "Poor",
                    "last_reading": readings_history.get(appliance_id, [{}])[-1].get("timestamp") if appliance_id in readings_history else None
                }
                
                dashboard["appliances"].append(appliance_summary)
                
            except Exception as e:
                # Skip appliances with errors
                continue
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@appliance_health_router.post("/maintenance/{appliance_id}")
async def record_maintenance(appliance_id: str, maintenance_date: str, notes: str = ""):
    """Record maintenance performed on an appliance"""
    try:
        if appliance_id not in appliances:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Update appliance metadata
        if appliance_id in predictor.appliance_metadata:
            predictor.appliance_metadata[appliance_id]["last_maintenance"] = maintenance_date
            predictor.appliance_metadata[appliance_id]["health_score"] = 100.0  # Reset health after maintenance
        
        return {
            "message": "Maintenance recorded successfully",
            "appliance_id": appliance_id,
            "maintenance_date": maintenance_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@appliance_health_router.delete("/appliances/{appliance_id}")
async def remove_appliance(appliance_id: str):
    """Remove an appliance from monitoring"""
    try:
        if appliance_id not in appliances:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Remove from storage
        del appliances[appliance_id]
        if appliance_id in readings_history:
            del readings_history[appliance_id]
        
        return {
            "message": "Appliance removed successfully",
            "appliance_id": appliance_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check endpoint
@appliance_health_router.get("/health")
async def health_check():
    """Health check for the appliance health prediction service"""
    return {
        "status": "healthy",
        "service": "appliance_health_prediction",
        "model_trained": predictor.is_trained,
        "total_appliances": len(appliances),
        "total_readings": sum(len(readings) for readings in readings_history.values())
    }
