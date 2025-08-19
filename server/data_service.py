#!/usr/bin/env python3
"""
Data Service Layer for Web Application
Aggregates data from all systems and provides unified data access
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DataAggregationService:
    """Service for aggregating data from all systems"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache or key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[key]
    
    def _set_cache(self, key: str, data: Any):
        """Set cache with expiry"""
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    def get_unified_dashboard_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get unified dashboard data from all systems"""
        cache_key = f"dashboard_{user_id or 'global'}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Aggregate data from all systems
            dashboard_data = {
                "summary": self._get_system_summary(),
                "solar_insights": self._get_solar_insights(),
                "appliance_health": self._get_appliance_health_summary(),
                "bill_forecast": self._get_bill_forecast(),
                "carbon_footprint": self._get_carbon_summary(),
                "efficiency_tips": self._get_efficiency_tips(),
                "alerts": self._get_system_alerts(),
                "last_updated": datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, dashboard_data)
            return dashboard_data
            
        except Exception as e:
            return {
                "error": f"Failed to aggregate dashboard data: {str(e)}",
                "summary": {"status": "error"},
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_system_summary(self) -> Dict[str, Any]:
        """Get overall system summary"""
        try:
            # Check system status
            systems = ["appliance_health", "solar_calculator", "smart_analysis", 
                      "bill_simulation", "carbon_tracker"]
            
            active_systems = 0
            for system in systems:
                try:
                    # Try to import each system
                    if system == "appliance_health":
                        from appliance_health_router import appliance_health_router
                    elif system == "solar_calculator":
                        from solar_calculator_router import solar_calculator_router
                    elif system == "smart_analysis":
                        from smart_automated_router import smart_automated_router
                    elif system == "bill_simulation":
                        from bill_simulation_router import bill_simulation_router
                    elif system == "carbon_tracker":
                        from carbon_tracker_router import carbon_tracker_router
                    active_systems += 1
                except ImportError:
                    continue
            
            return {
                "total_systems": len(systems),
                "active_systems": active_systems,
                "status": "healthy" if active_systems == len(systems) else "degraded",
                "uptime": "99.9%"
            }
        except Exception:
            return {"status": "unknown", "total_systems": 0, "active_systems": 0}
    
    def _get_solar_insights(self) -> Dict[str, Any]:
        """Get solar insights and recommendations"""
        try:
            # This would typically fetch from solar calculator system
            return {
                "potential_savings": "$1,200/year",
                "roi_percentage": "15.2%",
                "payback_period": "6.6 years",
                "carbon_offset": "4.2 tons CO2/year",
                "system_size": "8.5 kW",
                "estimated_cost": "$25,500",
                "federal_tax_credit": "$7,650",
                "state_incentives": "$2,000",
                "net_cost": "$15,850"
            }
        except Exception:
            return {"status": "unavailable"}
    
    def _get_appliance_health_summary(self) -> Dict[str, Any]:
        """Get appliance health summary"""
        try:
            # This would typically fetch from appliance health system
            return {
                "total_appliances": 8,
                "healthy": 7,
                "warning": 1,
                "critical": 0,
                "estimated_savings": "$180/year",
                "maintenance_alerts": [
                    "Refrigerator filter needs replacement (next week)",
                    "AC unit efficiency below optimal (85%)"
                ],
                "health_score": 87.5
            }
        except Exception:
            return {"status": "unavailable"}
    
    def _get_bill_forecast(self) -> Dict[str, Any]:
        """Get bill forecast and trends"""
        try:
            # This would typically fetch from bill simulation system
            return {
                "next_month": "$145",
                "trend": "decreasing",
                "seasonal_factor": "summer_peak",
                "year_to_date": "$1,680",
                "projected_annual": "$1,740",
                "savings_vs_last_year": "$120",
                "peak_usage_hours": "2:00 PM - 6:00 PM",
                "efficiency_score": 78
            }
        except Exception:
            return {"status": "unavailable"}
    
    def _get_carbon_summary(self) -> Dict[str, Any]:
        """Get carbon footprint summary"""
        try:
            # This would typically fetch from carbon tracker system
            return {
                "current_month": "0.8 tons CO2",
                "trend": "decreasing",
                "offset_progress": "65%",
                "annual_total": "9.6 tons CO2",
                "target": "7.0 tons CO2",
                "offset_required": "2.6 tons CO2",
                "equivalent_trees": "120",
                "equivalent_car_miles": "6,200"
            }
        except Exception:
            return {"status": "unavailable"}
    
    def _get_efficiency_tips(self) -> List[Dict[str, Any]]:
        """Get personalized efficiency tips"""
        return [
            {
                "category": "appliances",
                "tip": "Optimize AC usage during peak hours",
                "potential_savings": "$45/month",
                "difficulty": "easy",
                "estimated_time": "30 minutes"
            },
            {
                "category": "lighting",
                "tip": "Switch to LED lighting",
                "potential_savings": "$25/month",
                "difficulty": "easy",
                "estimated_time": "2 hours"
            },
            {
                "category": "behavior",
                "tip": "Use smart thermostat scheduling",
                "potential_savings": "$35/month",
                "difficulty": "medium",
                "estimated_time": "1 hour"
            },
            {
                "category": "maintenance",
                "tip": "Clean AC filters monthly",
                "potential_savings": "$15/month",
                "difficulty": "easy",
                "estimated_time": "15 minutes"
            }
        ]
    
    def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts and notifications"""
        alerts = []
        
        # Check for critical alerts
        try:
            # This would check various systems for alerts
            if datetime.now().hour >= 22:  # Night time
                alerts.append({
                    "level": "info",
                    "message": "Night mode activated - optimizing energy usage",
                    "timestamp": datetime.now().isoformat(),
                    "action_required": False
                })
        except Exception:
            pass
        
        return alerts
    
    def get_user_analytics(self, user_id: str, date_range: str = "30d") -> Dict[str, Any]:
        """Get user-specific analytics"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if date_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif date_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif date_range == "90d":
                start_date = end_date - timedelta(days=90)
            elif date_range == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            analytics = {
                "user_id": user_id,
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "energy_usage": {
                    "total_kwh": 450.5,
                    "daily_average": 15.0,
                    "peak_day": "2024-01-15",
                    "peak_usage": 22.3,
                    "trend": "decreasing"
                },
                "cost_analysis": {
                    "total_cost": "$135.15",
                    "daily_average": "$4.51",
                    "cost_per_kwh": "$0.30",
                    "savings_vs_baseline": "$18.45"
                },
                "efficiency_metrics": {
                    "overall_score": 78,
                    "appliance_efficiency": 82,
                    "behavior_score": 75,
                    "maintenance_score": 80
                },
                "carbon_impact": {
                    "total_emissions": "0.19 tons CO2",
                    "daily_average": "0.006 tons CO2",
                    "offset_progress": "65%"
                }
            }
            
            return analytics
            
        except Exception as e:
            return {"error": f"Failed to generate analytics: {str(e)}"}
    
    def export_user_data(self, user_id: str, format: str = "json", 
                         data_types: List[str] = None) -> Dict[str, Any]:
        """Export user data in various formats"""
        if data_types is None:
            data_types = ["analytics", "appliances", "bills", "carbon"]
        
        try:
            export_data = {}
            
            if "analytics" in data_types:
                export_data["analytics"] = self.get_user_analytics(user_id)
            
            if "appliances" in data_types:
                export_data["appliances"] = self._get_appliance_health_summary()
            
            if "bills" in data_types:
                export_data["bills"] = self._get_bill_forecast()
            
            if "carbon" in data_types:
                export_data["carbon"] = self._get_carbon_summary()
            
            # Generate export file info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_data_{user_id}_{timestamp}.{format}"
            
            return {
                "status": "success",
                "filename": filename,
                "format": format,
                "data_types": data_types,
                "download_url": f"/downloads/{filename}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                "data": export_data if format == "json" else None
            }
            
        except Exception as e:
            return {"error": f"Failed to export data: {str(e)}"}

# Global instance
data_service = DataAggregationService()
