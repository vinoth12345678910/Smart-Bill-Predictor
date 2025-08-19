import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class BillSimulationEngine:
    """
    Multi-Month Bill Simulation Engine
    Predicts future bills using historical data, weather patterns, and scenario modeling
    """
    
    def __init__(self):
        self.historical_data = pd.DataFrame()
        self.weather_data = {}
        self.simulation_model = None
        self.scaler = StandardScaler()
        self.emission_factors = {}
        
        # Default emission factors (kg CO2 per kWh) by region
        self.default_emission_factors = {
            'US': {
                'northeast': 0.35,      # NY, MA, CT - mix of nuclear, hydro, gas
                'west_coast': 0.25,     # CA, WA, OR - high renewable mix
                'southwest': 0.45,      # TX, AZ, NM - high coal/gas
                'southeast': 0.50,      # FL, GA, NC, SC - high coal
                'midwest': 0.55,        # IL, OH, MI, IN - high coal
                'mountain': 0.40,       # CO, UT, ID, MT - mix of coal and gas
                'default': 0.42
            },
            'EU': {
                'nordic': 0.15,         # Norway, Sweden - high hydro/nuclear
                'central': 0.35,        # Germany, France - mix of nuclear/renewables
                'southern': 0.45,       # Italy, Spain - mix of gas/renewables
                'eastern': 0.60,        # Poland, Czech Republic - high coal
                'default': 0.35
            },
            'default': 0.42
        }
        
        # Seasonal usage patterns (multipliers by month)
        self.seasonal_patterns = {
            'northern_hemisphere': {
                1: 1.25,   # January - Winter peak
                2: 1.20,   # February - Winter
                3: 1.10,   # March - Spring
                4: 0.95,   # April - Spring
                5: 0.90,   # May - Spring
                6: 1.05,   # June - Summer start
                7: 1.30,   # July - Summer peak
                8: 1.35,   # August - Summer peak
                9: 1.15,   # September - Summer
                10: 1.00,  # October - Fall
                11: 1.05,  # November - Fall
                12: 1.20   # December - Winter
            },
            'southern_hemisphere': {
                1: 1.30,   # January - Summer peak
                2: 1.25,   # February - Summer
                3: 1.15,   # March - Summer
                4: 1.00,   # April - Fall
                5: 0.90,   # May - Fall
                6: 0.85,   # June - Winter start
                7: 1.20,   # July - Winter peak
                8: 1.25,   # August - Winter peak
                9: 1.10,   # September - Winter
                10: 1.00,  # October - Spring
                11: 0.95,  # November - Spring
                12: 1.05   # December - Spring
            }
        }
    
    def load_historical_data(self, data_source: str = 'sample'):
        """
        Load historical usage data from various sources
        """
        if data_source == 'sample':
            # Generate sample historical data
            self.historical_data = self._generate_sample_data()
        elif data_source == 'csv':
            # Load from CSV file
            try:
                self.historical_data = pd.read_csv('historical_usage.csv')
            except FileNotFoundError:
                print("⚠️  CSV file not found, generating sample data")
                self.historical_data = self._generate_sample_data()
        
        print(f"✅ Loaded {len(self.historical_data)} historical records")
        return self.historical_data
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample historical usage data"""
        np.random.seed(42)
        
        # Generate 2 years of monthly data
        start_date = datetime(2022, 1, 1)
        dates = []
        usage = []
        bills = []
        temperatures = []
        
        base_usage = 1000  # kWh per month
        
        for i in range(24):  # 24 months
            date = start_date + timedelta(days=30*i)
            dates.append(date)
            
            # Add seasonal variation
            month = date.month
            seasonal_factor = self.seasonal_patterns['northern_hemisphere'][month]
            
            # Add temperature correlation
            if month in [6, 7, 8]:  # Summer
                temp = np.random.normal(28, 5)  # Hot summer
                ac_factor = 1.3 if temp > 25 else 1.1
            elif month in [12, 1, 2]:  # Winter
                temp = np.random.normal(5, 8)   # Cold winter
                heating_factor = 1.4 if temp < 0 else 1.2
            else:  # Spring/Fall
                temp = np.random.normal(18, 8)  # Mild weather
                ac_factor = heating_factor = 1.0
            
            # Calculate usage with seasonal and temperature factors
            if month in [6, 7, 8]:
                monthly_usage = base_usage * seasonal_factor * ac_factor
            elif month in [12, 1, 2]:
                monthly_usage = base_usage * seasonal_factor * heating_factor
            else:
                monthly_usage = base_usage * seasonal_factor
            
            # Add some randomness
            monthly_usage += np.random.normal(0, monthly_usage * 0.1)
            monthly_usage = max(monthly_usage, 200)  # Minimum usage
            
            usage.append(round(monthly_usage, 1))
            temperatures.append(round(temp, 1))
            
            # Calculate bill (assume $0.15/kWh base rate)
            base_rate = 0.15
            seasonal_rate = base_rate * (1.15 if month in [6, 7, 8] else 1.0)
            bill = monthly_usage * seasonal_rate
            bills.append(round(bill, 2))
        
        df = pd.DataFrame({
            'date': dates,
            'month': [d.month for d in dates],
            'year': [d.year for d in dates],
            'usage_kwh': usage,
            'bill_amount': bills,
            'avg_temperature': temperatures
        })
        
        return df
    
    def get_weather_forecast(self, location: Dict, months_ahead: int = 12) -> Dict:
        """
        Get weather forecast for bill simulation
        """
        try:
            # Use OpenWeatherMap API for forecast (if available)
            if hasattr(self, 'api_keys') and self.api_keys.get('openweather'):
                return self._fetch_weather_forecast(location, months_ahead)
            else:
                return self._generate_weather_forecast(location, months_ahead)
        except Exception as e:
            print(f"⚠️  Weather forecast failed: {e}")
            return self._generate_weather_forecast(location, months_ahead)
    
    def _generate_weather_forecast(self, location: Dict, months_ahead: int) -> Dict:
        """Generate weather forecast based on historical patterns"""
        forecast = {}
        current_date = datetime.now()
        
        for i in range(months_ahead):
            future_date = current_date + timedelta(days=30*i)
            month = future_date.month
            
            # Get seasonal temperature patterns
            if month in [6, 7, 8]:  # Summer
                temp = np.random.normal(28, 5)
                humidity = np.random.normal(70, 15)
            elif month in [12, 1, 2]:  # Winter
                temp = np.random.normal(5, 8)
                humidity = np.random.normal(60, 20)
            else:  # Spring/Fall
                temp = np.random.normal(18, 8)
                humidity = np.random.normal(65, 15)
            
            forecast[future_date.strftime('%Y-%m')] = {
                'avg_temperature': round(temp, 1),
                'avg_humidity': round(humidity, 1),
                'season': 'summer' if month in [6, 7, 8] else 'winter' if month in [12, 1, 2] else 'spring'
            }
        
        return forecast
    
    def train_simulation_model(self, features: List[str] = None):
        """
        Train the bill simulation model
        """
        if self.historical_data.empty:
            print("❌ No historical data available")
            return False
        
        if not features:
            features = ['month', 'avg_temperature', 'year']
        
        # Prepare features
        X = self.historical_data[features].copy()
        y = self.historical_data['usage_kwh']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model (Random Forest for better performance)
        self.simulation_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.simulation_model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.simulation_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"   MAE: {mae:.1f} kWh")
        print(f"   R²: {r2:.3f}")
        
        return True
    
    def simulate_bills(self, months_ahead: int = 12, scenarios: Dict = None) -> Dict:
        """
        Simulate future bills with scenario modeling
        """
        if not self.simulation_model:
            print("❌ Model not trained. Please train the model first.")
            return {}
        
        if not scenarios:
            scenarios = {
                'appliance_changes': {},
                'tariff_changes': {},
                'efficiency_improvements': 0.0
            }
        
        print(f"🚀 Simulating bills for {months_ahead} months ahead...")
        
        # Generate future dates
        current_date = datetime.now()
        future_dates = []
        for i in range(months_ahead):
            future_date = current_date + timedelta(days=30*i)
            future_dates.append(future_date)
        
        # Prepare features for prediction
        features = []
        for date in future_dates:
            month = date.month
            year = date.year
            
            # Estimate temperature based on seasonal patterns
            if month in [6, 7, 8]:  # Summer
                temp = 28
            elif month in [12, 1, 2]:  # Winter
                temp = 5
            else:  # Spring/Fall
                temp = 18
            
            features.append([month, temp, year])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict base usage
        base_predictions = self.simulation_model.predict(features_scaled)
        
        # Apply scenario modifications
        scenario_results = []
        for i, (date, base_usage) in enumerate(zip(future_dates, base_predictions)):
            modified_usage = self._apply_scenarios(base_usage, scenarios, date)
            
            # Calculate bill with tariff changes
            base_rate = 0.15
            if 'tariff_changes' in scenarios:
                for tariff_change in scenarios['tariff_changes']:
                    if tariff_change['start_date'] <= date.strftime('%Y-%m'):
                        base_rate = tariff_change['new_rate']
            
            bill_amount = modified_usage * base_rate
            
            scenario_results.append({
                'date': date.strftime('%Y-%m'),
                'base_usage_kwh': round(base_usage, 1),
                'modified_usage_kwh': round(modified_usage, 1),
                'bill_amount': round(bill_amount, 2),
                'temperature': features[i][1],
                'season': self._get_season(date.month)
            })
        
        # Calculate summary statistics
        total_usage = sum(r['modified_usage_kwh'] for r in scenario_results)
        total_bill = sum(r['bill_amount'] for r in scenario_results)
        avg_monthly_bill = total_bill / months_ahead
        
        # Compare with historical average
        historical_avg = self.historical_data['bill_amount'].mean()
        bill_change = ((avg_monthly_bill - historical_avg) / historical_avg) * 100
        
        simulation_results = {
            'scenarios_applied': scenarios,
            'months_simulated': months_ahead,
            'monthly_breakdown': scenario_results,
            'summary': {
                'total_usage_kwh': round(total_usage, 1),
                'total_bill_amount': round(total_bill, 2),
                'avg_monthly_bill': round(avg_monthly_bill, 2),
                'historical_avg_monthly_bill': round(historical_avg, 2),
                'bill_change_percentage': round(bill_change, 1),
                'bill_change_direction': 'increase' if bill_change > 0 else 'decrease'
            },
            'recommendations': self._generate_simulation_recommendations(scenarios, bill_change)
        }
        
        print(f"✅ Simulation completed! Average monthly bill: ${avg_monthly_bill:.2f}")
        return simulation_results
    
    def _apply_scenarios(self, base_usage: float, scenarios: Dict, date: datetime) -> float:
        """Apply scenario modifications to base usage"""
        modified_usage = base_usage
        
        # Appliance changes
        if 'appliance_changes' in scenarios:
            for change in scenarios['appliance_changes']:
                if change['start_date'] <= date.strftime('%Y-%m'):
                    if change['type'] == 'add':
                        modified_usage += change['usage_kwh']
                    elif change['type'] == 'remove':
                        modified_usage -= change['usage_kwh']
                    elif change['type'] == 'replace':
                        modified_usage = modified_usage - change['old_usage'] + change['new_usage']
        
        # Efficiency improvements
        if 'efficiency_improvements' in scenarios:
            efficiency_gain = scenarios['efficiency_improvements']
            modified_usage *= (1 - efficiency_gain)
        
        return max(modified_usage, 100)  # Minimum usage
    
    def _get_season(self, month: int) -> str:
        """Get season from month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def _generate_simulation_recommendations(self, scenarios: Dict, bill_change: float) -> List[str]:
        """Generate recommendations based on simulation results"""
        recommendations = []
        
        if bill_change > 20:
            recommendations.append("⚠️  Significant bill increase expected - consider energy efficiency measures")
        elif bill_change > 10:
            recommendations.append("📈 Moderate bill increase expected - review usage patterns")
        elif bill_change < -10:
            recommendations.append("📉 Bill decrease expected - efficiency measures working well")
        
        if 'efficiency_improvements' in scenarios and scenarios['efficiency_improvements'] > 0:
            recommendations.append("✅ Efficiency improvements applied - monitor actual savings")
        
        if 'appliance_changes' in scenarios and scenarios['appliance_changes']:
            recommendations.append("🔌 Appliance changes applied - verify new usage patterns")
        
        recommendations.append("📊 Review monthly breakdown for seasonal patterns")
        recommendations.append("🌡️  Temperature variations significantly impact usage")
        
        return recommendations
    
    def get_carbon_footprint(self, usage_kwh: float, location: Dict = None) -> Dict:
        """
        Calculate carbon footprint from electricity usage
        """
        if not location:
            location = {'country': 'US', 'region': 'default'}
        
        country = location.get('country', 'US')
        region = location.get('region', 'default')
        
        # Get emission factor
        if country in self.default_emission_factors:
            if region in self.default_emission_factors[country]:
                emission_factor = self.default_emission_factors[country][region]
            else:
                emission_factor = self.default_emission_factors[country]['default']
        else:
            emission_factor = self.default_emission_factors['default']
        
        # Calculate CO2 emissions
        co2_kg = usage_kwh * emission_factor
        
        # Calculate offset equivalents
        trees_needed = co2_kg / 22  # Average tree absorbs 22kg CO2 per year
        renewable_credits = co2_kg / 1000  # 1 credit = 1 ton CO2
        
        return {
            'usage_kwh': usage_kwh,
            'emission_factor_kg_co2_per_kwh': emission_factor,
            'total_co2_kg': round(co2_kg, 2),
            'offset_equivalents': {
                'trees_needed': round(trees_needed, 1),
                'renewable_credits': round(renewable_credits, 3),
                'car_miles': round(co2_kg * 2.3, 1),  # 1 kg CO2 ≈ 2.3 car miles
                'flight_hours': round(co2_kg / 90, 2)  # 1 kg CO2 ≈ 0.01 flight hours
            },
            'location': location
        }
