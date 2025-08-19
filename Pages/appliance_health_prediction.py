import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ApplianceHealthPredictor:
    """
    Appliance Health Prediction System using Isolation Forest and LSTM
    for anomaly detection and failure prediction
    """
    
    def __init__(self):
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.appliance_metadata = {}
        self.health_thresholds = {}
        self.is_trained = False
        
    def add_appliance(self, appliance_id: str, brand: str, model: str, 
                     power_rating: float, category: str, installation_date: str):
        """
        Add appliance metadata to the system
        """
        self.appliance_metadata[appliance_id] = {
            'brand': brand,
            'model': model,
            'power_rating': power_rating,  # in watts
            'category': category,  # refrigerator, washing_machine, etc.
            'installation_date': installation_date,
            'last_maintenance': None,
            'expected_lifespan': self._get_expected_lifespan(category),
            'health_score': 100.0
        }
        
        # Set health thresholds based on appliance type
        self.health_thresholds[appliance_id] = self._get_health_thresholds(category)
        
    def _get_expected_lifespan(self, category: str) -> int:
        """Get expected lifespan in years for appliance category"""
        lifespans = {
            'refrigerator': 15,
            'washing_machine': 12,
            'dishwasher': 10,
            'microwave': 8,
            'oven': 15,
            'air_conditioner': 12,
            'water_heater': 10,
            'dryer': 12,
            'freezer': 18,
            'other': 10
        }
        return lifespans.get(category, 10)
    
    def _get_health_thresholds(self, category: str) -> Dict:
        """Get health thresholds for anomaly detection"""
        base_thresholds = {
            'energy_anomaly_threshold': 0.15,  # 15% deviation from normal
            'power_factor_threshold': 0.85,
            'vibration_threshold': 0.1,
            'temperature_threshold': 0.2,
            'noise_threshold': 0.25
        }
        
        # Adjust thresholds based on appliance type
        if category == 'refrigerator':
            base_thresholds['temperature_threshold'] = 0.1
        elif category == 'washing_machine':
            base_thresholds['vibration_threshold'] = 0.15
        elif category == 'air_conditioner':
            base_thresholds['energy_anomaly_threshold'] = 0.2
            
        return base_thresholds
    
    def record_reading(self, appliance_id: str, timestamp: str, 
                      energy_usage: float, power_factor: float = 1.0,
                      temperature: float = None, vibration: float = None,
                      noise_level: float = None):
        """
        Record a new sensor reading for an appliance
        """
        if appliance_id not in self.appliance_metadata:
            raise ValueError(f"Appliance {appliance_id} not found")
            
        # Create reading record
        reading = {
            'appliance_id': appliance_id,
            'timestamp': timestamp,
            'energy_usage': energy_usage,
            'power_factor': power_factor,
            'temperature': temperature,
            'vibration': vibration,
            'noise_level': noise_level,
            'normalized_energy': energy_usage / self.appliance_metadata[appliance_id]['power_rating']
        }
        
        return reading
    
    def train_anomaly_detector(self, historical_data: List[Dict]):
        """
        Train the Isolation Forest model on historical appliance data
        """
        if not historical_data:
            raise ValueError("Historical data is required for training")
            
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Prepare features for anomaly detection
        feature_columns = ['energy_usage', 'power_factor', 'normalized_energy']
        if 'temperature' in df.columns:
            feature_columns.append('temperature')
        if 'vibration' in df.columns:
            feature_columns.append('vibration')
        if 'noise_level' in df.columns:
            feature_columns.append('noise_level')
            
        # Remove rows with missing values
        df_clean = df[feature_columns].dropna()
        
        if len(df_clean) < 10:
            raise ValueError("Insufficient data for training (need at least 10 samples)")
            
        # Scale features
        X_scaled = self.scaler.fit_transform(df_clean)
        
        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        
        self.isolation_forest.fit(X_scaled)
        self.is_trained = True
        
        print(f"Anomaly detector trained on {len(df_clean)} samples")
        
    def detect_anomalies(self, readings: List[Dict]) -> List[Dict]:
        """
        Detect anomalies in appliance readings
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before anomaly detection")
            
        results = []
        
        for reading in readings:
            appliance_id = reading['appliance_id']
            
            # Prepare features
            features = [reading['energy_usage'], reading['power_factor'], reading['normalized_energy']]
            if reading.get('temperature') is not None:
                features.append(reading['temperature'])
            if reading.get('vibration') is not None:
                features.append(reading['vibration'])
            if reading.get('noise_level') is not None:
                features.append(reading['noise_level'])
                
            # Pad features if needed
            while len(features) < self.scaler.n_features_in_:
                features.append(0.0)
                
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict anomaly (-1 for anomaly, 1 for normal)
            is_anomaly = self.isolation_forest.predict(features_scaled)[0]
            anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
            
            # Calculate health score
            health_score = self._calculate_health_score(reading, appliance_id, anomaly_score)
            
            result = {
                'appliance_id': appliance_id,
                'timestamp': reading['timestamp'],
                'is_anomaly': bool(is_anomaly == -1),
                'anomaly_score': float(anomaly_score),
                'health_score': health_score,
                'recommendations': self._get_recommendations(reading, appliance_id, health_score),
                'severity': self._get_severity_level(health_score)
            }
            
            results.append(result)
            
        return results
    
    def _calculate_health_score(self, reading: Dict, appliance_id: str, anomaly_score: float) -> float:
        """Calculate appliance health score (0-100)"""
        base_score = 100.0
        thresholds = self.health_thresholds[appliance_id]
        
        # Energy usage deviation
        expected_energy = self.appliance_metadata[appliance_id]['power_rating'] / 1000  # kWh
        energy_deviation = abs(reading['energy_usage'] - expected_energy) / expected_energy
        if energy_deviation > thresholds['energy_anomaly_threshold']:
            base_score -= 20
            
        # Power factor penalty
        if reading['power_factor'] < thresholds['power_factor_threshold']:
            base_score -= 15
            
        # Temperature penalty
        if reading.get('temperature') is not None:
            temp_deviation = abs(reading['temperature'] - 25) / 25  # Assuming 25°C is normal
            if temp_deviation > thresholds['temperature_threshold']:
                base_score -= 10
                
        # Vibration penalty
        if reading.get('vibration') is not None:
            if reading['vibration'] > thresholds['vibration_threshold']:
                base_score -= 15
                
        # Noise penalty
        if reading.get('noise_level') is not None:
            if reading['noise_level'] > thresholds['noise_threshold']:
                base_score -= 10
                
        # Anomaly score penalty
        if anomaly_score < -0.5:
            base_score -= 25
        elif anomaly_score < -0.2:
            base_score -= 15
            
        return max(0.0, base_score)
    
    def _get_recommendations(self, reading: Dict, appliance_id: str, health_score: float) -> List[str]:
        """Get maintenance recommendations based on health score"""
        recommendations = []
        
        if health_score < 30:
            recommendations.append("Immediate maintenance required - appliance may fail soon")
        elif health_score < 50:
            recommendations.append("Schedule maintenance within 1 week")
        elif health_score < 70:
            recommendations.append("Schedule maintenance within 1 month")
            
        # Specific recommendations based on readings
        if reading['power_factor'] < 0.9:
            recommendations.append("Check electrical connections and power quality")
            
        if reading.get('vibration', 0) > 0.1:
            recommendations.append("Check for loose parts or mechanical issues")
            
        if reading.get('temperature', 25) > 30:
            recommendations.append("Check cooling system and ventilation")
            
        return recommendations
    
    def _get_severity_level(self, health_score: float) -> str:
        """Get severity level based on health score"""
        if health_score >= 80:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        elif health_score >= 20:
            return "Critical"
        else:
            return "Emergency"
    
    def predict_failure_probability(self, appliance_id: str, 
                                  recent_readings: List[Dict]) -> Dict:
        """
        Predict probability of appliance failure based on recent readings
        """
        if appliance_id not in self.appliance_metadata:
            raise ValueError(f"Appliance {appliance_id} not found")
            
        if not recent_readings:
            return {"failure_probability": 0.0, "time_to_failure": "Unknown"}
            
        # Calculate trend indicators
        energy_trend = self._calculate_trend([r['energy_usage'] for r in recent_readings])
        health_trend = self._calculate_trend([r.get('health_score', 100) for r in recent_readings])
        
        # Base failure probability
        base_probability = 0.1
        
        # Age factor
        installation_date = datetime.strptime(
            self.appliance_metadata[appliance_id]['installation_date'], 
            '%Y-%m-%d'
        )
        age_years = (datetime.now() - installation_date).days / 365.25
        expected_lifespan = self.appliance_metadata[appliance_id]['expected_lifespan']
        
        if age_years > expected_lifespan * 0.8:
            base_probability += 0.3
        elif age_years > expected_lifespan * 0.6:
            base_probability += 0.2
            
        # Trend factors
        if energy_trend > 0.1:  # Increasing energy usage
            base_probability += 0.2
            
        if health_trend < -0.1:  # Declining health
            base_probability += 0.3
            
        # Recent anomaly factor
        recent_anomalies = sum(1 for r in recent_readings if r.get('is_anomaly', False))
        if recent_anomalies > 0:
            base_probability += 0.2 * min(recent_anomalies, 3)
            
        # Estimate time to failure
        if base_probability > 0.7:
            time_to_failure = "1-2 weeks"
        elif base_probability > 0.5:
            time_to_failure = "1-2 months"
        elif base_probability > 0.3:
            time_to_failure = "3-6 months"
        else:
            time_to_failure = "6+ months"
            
        return {
            "failure_probability": min(base_probability, 0.95),
            "time_to_failure": time_to_failure,
            "age_years": age_years,
            "energy_trend": energy_trend,
            "health_trend": health_trend
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0.0
            
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Normalize by the mean value
        mean_val = np.mean(values)
        if mean_val == 0:
            return 0.0
            
        return slope / mean_val
    
    def save_model(self, filepath: str):
        """Save the trained model and metadata"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
            
        model_data = {
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'appliance_metadata': self.appliance_metadata,
            'health_thresholds': self.health_thresholds,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model and metadata"""
        model_data = joblib.load(filepath)
        
        self.isolation_forest = model_data['isolation_forest']
        self.scaler = model_data['scaler']
        self.appliance_metadata = model_data['appliance_metadata']
        self.health_thresholds = model_data['health_thresholds']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
    
    def get_appliance_status(self, appliance_id: str) -> Dict:
        """Get current status and health information for an appliance"""
        if appliance_id not in self.appliance_metadata:
            raise ValueError(f"Appliance {appliance_id} not found")
            
        metadata = self.appliance_metadata[appliance_id]
        
        return {
            'appliance_id': appliance_id,
            'brand': metadata['brand'],
            'model': metadata['model'],
            'power_rating': metadata['power_rating'],
            'category': metadata['category'],
            'installation_date': metadata['installation_date'],
            'last_maintenance': metadata['last_maintenance'],
            'expected_lifespan': metadata['expected_lifespan'],
            'current_health_score': metadata['health_score'],
            'status': 'Active' if metadata['health_score'] > 50 else 'Maintenance Required'
        }
