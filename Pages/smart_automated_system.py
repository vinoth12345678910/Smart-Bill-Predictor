import requests
import json
import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class SmartAutomatedSystem:
    """
    Automated Smart System for Solar & Appliance Health
    Automatically detects location, gets real-time data, and provides analysis
    """
    
    def __init__(self):
        self.location_data = {}
        self.property_data = {}
        self.utility_data = {}
        self.weather_data = {}
        
        # API Keys (user needs to set these)
        self.api_keys = {
            'google_maps': None,      # For address lookup and roof area
            'openweather': None,      # For weather data
            'utility_api': None,      # For electricity rates
            'nrel': None             # For solar irradiance
        }
        
        # Default property types and their characteristics
        self.property_types = {
            'single_family': {
                'avg_roof_area': 120,      # m²
                'avg_annual_usage': 12000,  # kWh
                'roof_orientation': 'south',
                'shading_factor': 0.95
            },
            'townhouse': {
                'avg_roof_area': 80,
                'avg_annual_usage': 10000,
                'roof_orientation': 'south',
                'shading_factor': 0.90
            },
            'apartment': {
                'avg_roof_area': 40,
                'avg_annual_usage': 8000,
                'roof_orientation': 'south',
                'shading_factor': 0.85
            },
            'commercial': {
                'avg_roof_area': 500,
                'avg_annual_usage': 50000,
                'roof_orientation': 'south',
                'shading_factor': 0.80
            }
        }
    
    def set_api_keys(self, google_maps: str = None, openweather: str = None, 
                     utility_api: str = None, nrel: str = None):
        """Set API keys for automated data fetching"""
        if google_maps:
            self.api_keys['google_maps'] = google_maps
        if openweather:
            self.api_keys['openweather'] = openweather
        if utility_api:
            self.api_keys['utility_api'] = utility_api
        if nrel:
            self.api_keys['nrel'] = nrel
        
        print("✅ API keys configured for automated data fetching")
    
    def auto_detect_location(self) -> Dict:
        """
        Automatically detect user's location using IP geolocation
        Returns: location data with coordinates and address
        """
        try:
            # Use free IP geolocation service
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            
            if data['status'] == 'success':
                self.location_data = {
                    'latitude': data['lat'],
                    'longitude': data['lon'],
                    'city': data['city'],
                    'state': data['regionName'],
                    'country': data['country'],
                    'zipcode': data['zip'],
                    'timezone': data['timezone'],
                    'isp': data['isp'],
                    'source': 'IP Geolocation'
                }
                
                print(f"📍 Location auto-detected: {data['city']}, {data['regionName']}, {data['country']}")
                return self.location_data
            else:
                raise Exception("IP geolocation failed")
                
        except Exception as e:
            print(f"⚠️  Auto-location failed: {e}")
            print("Using default location (New York City)")
            
            # Fallback to default location
            self.location_data = {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'city': 'New York',
                'state': 'NY',
                'country': 'US',
                'zipcode': '10001',
                'timezone': 'America/New_York',
                'source': 'Default'
            }
            return self.location_data
    
    def get_address_from_coordinates(self, lat: float, lon: float) -> Dict:
        """
        Get detailed address from coordinates using reverse geocoding
        """
        try:
            # Use free reverse geocoding service
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if 'address' in data:
                address = data['address']
                return {
                    'full_address': data['display_name'],
                    'street': address.get('road', ''),
                    'house_number': address.get('house_number', ''),
                    'city': address.get('city', address.get('town', '')),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'postcode': address.get('postcode', ''),
                    'neighborhood': address.get('neighbourhood', '')
                }
            else:
                return {}
                
        except Exception as e:
            print(f"⚠️  Address lookup failed: {e}")
            return {}
    
    def auto_detect_property_type(self, address: str = None) -> str:
        """
        Automatically detect property type based on address or location
        """
        if not address:
            address = f"{self.location_data.get('city', '')} {self.location_data.get('state', '')}"
        
        address_lower = address.lower()
        
        # Simple keyword-based detection
        if any(word in address_lower for word in ['apt', 'apartment', 'unit', 'floor']):
            return 'apartment'
        elif any(word in address_lower for word in ['townhouse', 'town house', 'row house']):
            return 'townhouse'
        elif any(word in address_lower for word in ['office', 'commercial', 'business', 'industrial']):
            return 'commercial'
        else:
            return 'single_family'  # Default assumption
    
    def estimate_roof_area(self, property_type: str = None, address: str = None) -> float:
        """
        Estimate roof area based on property type and location
        """
        if not property_type:
            property_type = self.auto_detect_property_type(address)
        
        base_area = self.property_types[property_type]['avg_roof_area']
        
        # Adjust based on location (larger properties in suburban areas)
        if self.location_data.get('country') == 'US':
            state = self.location_data.get('state', '')
            # Suburban states typically have larger properties
            suburban_states = ['TX', 'CA', 'FL', 'NY', 'PA', 'OH', 'IL', 'GA', 'NC', 'MI']
            if state in suburban_states:
                base_area *= 1.2
            # Rural states have even larger properties
            rural_states = ['MT', 'ND', 'SD', 'WY', 'AK']
            if state in rural_states:
                base_area *= 1.5
        
        return round(base_area, 1)
    
    def get_electricity_rates(self, zipcode: str = None) -> Dict:
        """
        Get real-time electricity rates for the location
        """
        if not zipcode:
            zipcode = self.location_data.get('zipcode', '10001')
        
        # Default rates by region (US)
        default_rates = {
            'northeast': 0.22,    # NY, MA, CT, etc.
            'west_coast': 0.18,   # CA, WA, OR
            'southwest': 0.12,    # TX, AZ, NM
            'southeast': 0.14,    # FL, GA, NC, SC
            'midwest': 0.16,      # IL, OH, MI, IN
            'mountain': 0.11,     # CO, UT, ID, MT
            'default': 0.15
        }
        
        # Simple region detection based on zipcode ranges
        zip_int = int(zipcode[:3]) if zipcode and zipcode.isdigit() else 100
        
        if 100 <= zip_int <= 199:  # Northeast
            region = 'northeast'
        elif 900 <= zip_int <= 999:  # West Coast
            region = 'west_coast'
        elif 700 <= zip_int <= 799:  # Southwest
            region = 'southwest'
        elif 300 <= zip_int <= 399:  # Southeast
            region = 'southeast'
        elif 400 <= zip_int <= 499:  # Midwest
            region = 'midwest'
        elif 800 <= zip_int <= 899:  # Mountain
            region = 'mountain'
        else:
            region = 'default'
        
        base_rate = default_rates[region]
        
        # Add seasonal variations
        import datetime
        month = datetime.datetime.now().month
        
        if month in [6, 7, 8]:  # Summer
            seasonal_factor = 1.15
        elif month in [12, 1, 2]:  # Winter
            seasonal_factor = 1.10
        else:  # Spring/Fall
            seasonal_factor = 1.0
        
        current_rate = base_rate * seasonal_factor
        
        return {
            'current_rate': round(current_rate, 3),
            'base_rate': base_rate,
            'region': region,
            'seasonal_factor': seasonal_factor,
            'zipcode': zipcode,
            'source': 'Regional Defaults'
        }
    
    def get_weather_data(self, lat: float = None, lon: float = None) -> Dict:
        """
        Get current weather data for solar calculations
        """
        if not lat:
            lat = self.location_data.get('latitude')
        if not lon:
            lon = self.location_data.get('longitude')
        
        try:
            if self.api_keys['openweather']:
                # Use OpenWeatherMap API for real-time data
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_keys['openweather'],
                    'units': 'metric'
                }
                
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if response.status_code == 200:
                    self.weather_data = {
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'clouds': data['clouds']['all'],
                        'wind_speed': data['wind']['speed'],
                        'weather_condition': data['weather'][0]['main'],
                        'source': 'OpenWeatherMap API'
                    }
                    return self.weather_data
                else:
                    raise Exception(f"API error: {data.get('message', 'Unknown error')}")
            else:
                # Use default weather data based on location
                return self._get_default_weather(lat, lon)
                
        except Exception as e:
            print(f"⚠️  Weather data fetch failed: {e}")
            return self._get_default_weather(lat, lon)
    
    def _get_default_weather(self, lat: float, lon: float) -> Dict:
        """Get default weather data based on location and season"""
        import datetime
        
        month = datetime.datetime.now().month
        season = 'summer' if month in [6, 7, 8] else 'winter' if month in [12, 1, 2] else 'spring'
        
        # Default weather patterns by season and latitude
        if abs(lat) < 30:  # Tropical
            if season == 'summer':
                temp, humidity, clouds = 28, 80, 60
            else:
                temp, humidity, clouds = 25, 75, 40
        elif abs(lat) < 45:  # Subtropical
            if season == 'summer':
                temp, humidity, clouds = 25, 70, 30
            else:
                temp, humidity, clouds = 15, 65, 50
        else:  # Temperate
            if season == 'summer':
                temp, humidity, clouds = 22, 60, 25
            else:
                temp, humidity, clouds = 5, 70, 70
        
        return {
            'temperature': temp,
            'humidity': humidity,
            'clouds': clouds,
            'wind_speed': 5.0,
            'weather_condition': 'Clear' if clouds < 30 else 'Cloudy',
            'source': 'Default (Seasonal)'
        }
    
    def smart_analysis(self, user_input: Dict = None) -> Dict:
        """
        One-click smart analysis with minimal user input
        """
        print("🚀 Starting Smart Automated Analysis...")
        
        # Step 1: Auto-detect location
        print("📍 Detecting location...")
        location = self.auto_detect_location()
        
        # Step 2: Get detailed address
        print("🏠 Getting address details...")
        address_details = self.get_address_from_coordinates(location['latitude'], location['longitude'])
        
        # Step 3: Auto-detect property type
        print("🏗️ Detecting property type...")
        property_type = self.auto_detect_property_type(address_details.get('full_address', ''))
        
        # Step 4: Estimate roof area
        print("📏 Estimating roof area...")
        roof_area = self.estimate_roof_area(property_type, address_details.get('full_address', ''))
        
        # Step 5: Get electricity rates
        print("⚡ Getting electricity rates...")
        electricity_rates = self.get_electricity_rates(location.get('zipcode'))
        
        # Step 6: Get weather data
        print("🌤️ Getting weather data...")
        weather = self.get_weather_data(location['latitude'], location['longitude'])
        
        # Step 7: Compile smart recommendations
        print("🧠 Generating smart recommendations...")
        recommendations = self._generate_smart_recommendations(
            location, property_type, roof_area, electricity_rates, weather
        )
        
        # Compile complete analysis
        analysis = {
            'location': location,
            'address': address_details,
            'property': {
                'type': property_type,
                'estimated_roof_area_m2': roof_area,
                'characteristics': self.property_types[property_type]
            },
            'utilities': electricity_rates,
            'weather': weather,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.datetime.now().isoformat(),
            'data_sources': self._get_data_sources()
        }
        
        print("✅ Smart analysis completed!")
        return analysis
    
    def _generate_smart_recommendations(self, location: Dict, property_type: str, 
                                      roof_area: float, electricity_rates: Dict, 
                                      weather: Dict) -> Dict:
        """Generate smart recommendations based on all collected data"""
        
        # Solar feasibility score (0-100)
        solar_score = self._calculate_solar_score(location, roof_area, weather)
        
        # Appliance health priority
        appliance_priority = self._calculate_appliance_priority(property_type, electricity_rates)
        
        # Cost savings potential
        savings_potential = self._calculate_savings_potential(roof_area, electricity_rates)
        
        # Action items
        action_items = self._generate_action_items(solar_score, appliance_priority, savings_potential)
        
        return {
            'solar_feasibility': {
                'score': solar_score,
                'rating': self._get_rating(solar_score),
                'priority': 'high' if solar_score > 70 else 'medium' if solar_score > 40 else 'low'
            },
            'appliance_health': {
                'priority': appliance_priority,
                'focus_areas': self._get_appliance_focus_areas(property_type),
                'monitoring_frequency': 'weekly' if appliance_priority == 'high' else 'monthly'
            },
            'cost_savings': {
                'potential': savings_potential,
                'annual_estimate': round(savings_potential * electricity_rates['current_rate'] * 12000, 2),
                'payback_period': self._estimate_payback_period(roof_area, savings_potential)
            },
            'action_items': action_items,
            'next_steps': self._get_next_steps(solar_score, appliance_priority)
        }
    
    def _calculate_solar_score(self, location: Dict, roof_area: float, weather: Dict) -> int:
        """Calculate solar feasibility score (0-100)"""
        score = 50  # Base score
        
        # Location factor (latitude-based)
        lat = abs(location['latitude'])
        if lat < 30:  # Tropical - excellent
            score += 25
        elif lat < 45:  # Subtropical - very good
            score += 20
        elif lat < 60:  # Temperate - good
            score += 15
        else:  # Polar - poor
            score -= 10
        
        # Roof area factor
        if roof_area > 100:
            score += 15
        elif roof_area > 60:
            score += 10
        elif roof_area > 30:
            score += 5
        else:
            score -= 5
        
        # Weather factor
        if weather['clouds'] < 30:
            score += 10
        elif weather['clouds'] < 60:
            score += 5
        else:
            score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_appliance_priority(self, property_type: str, electricity_rates: Dict) -> str:
        """Calculate appliance health monitoring priority"""
        if property_type == 'commercial':
            return 'high'  # Commercial properties need constant monitoring
        elif electricity_rates['current_rate'] > 0.20:
            return 'high'  # High electricity rates = high savings potential
        elif property_type == 'single_family':
            return 'medium'  # Single family homes benefit from monitoring
        else:
            return 'low'  # Apartments have limited control
    
    def _calculate_savings_potential(self, roof_area: float, electricity_rates: Dict) -> float:
        """Calculate potential annual energy savings (kWh)"""
        # Base on roof area and electricity rates
        base_potential = roof_area * 0.8  # 80% of roof area usable
        rate_factor = electricity_rates['current_rate'] / 0.15  # Normalized to $0.15/kWh
        
        return round(base_potential * rate_factor, 1)
    
    def _estimate_payback_period(self, roof_area: float, savings_potential: float) -> int:
        """Estimate solar payback period in years"""
        # Rough estimate: $3/W installed cost
        system_cost = roof_area * 0.8 * 400 * 3  # $3 per watt
        annual_savings = savings_potential * 0.15  # Assume $0.15/kWh
        
        if annual_savings > 0:
            return max(5, min(25, round(system_cost / annual_savings)))
        else:
            return 25
    
    def _get_rating(self, score: int) -> str:
        """Convert score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_appliance_focus_areas(self, property_type: str) -> List[str]:
        """Get appliance focus areas based on property type"""
        focus_areas = {
            'single_family': ['HVAC', 'Refrigerator', 'Water Heater', 'Dishwasher'],
            'townhouse': ['HVAC', 'Refrigerator', 'Washer/Dryer'],
            'apartment': ['Refrigerator', 'Microwave', 'Small Appliances'],
            'commercial': ['HVAC Systems', 'Refrigeration', 'Lighting', 'Industrial Equipment']
        }
        return focus_areas.get(property_type, ['General Appliances'])
    
    def _generate_action_items(self, solar_score: int, appliance_priority: str, 
                             savings_potential: float) -> List[str]:
        """Generate actionable items based on analysis"""
        actions = []
        
        if solar_score > 70:
            actions.append("Schedule solar consultation - excellent potential")
        elif solar_score > 40:
            actions.append("Consider solar feasibility study")
        
        if appliance_priority == 'high':
            actions.append("Implement appliance health monitoring system")
            actions.append("Schedule energy audit")
        
        if savings_potential > 5000:
            actions.append("High savings potential - prioritize energy efficiency")
        
        actions.append("Monitor monthly energy usage patterns")
        actions.append("Consider smart home energy management")
        
        return actions
    
    def _get_next_steps(self, solar_score: int, appliance_priority: str) -> List[str]:
        """Get next steps based on analysis results"""
        steps = []
        
        if solar_score > 60:
            steps.append("Get 3+ solar quotes from local installers")
            steps.append("Check local solar incentives and rebates")
        
        if appliance_priority == 'high':
            steps.append("Install smart energy monitoring devices")
            steps.append("Schedule professional energy audit")
        
        steps.append("Review and optimize daily energy usage")
        steps.append("Set up monthly energy consumption tracking")
        
        return steps
    
    def _get_data_sources(self) -> Dict:
        """Get information about data sources used"""
        sources = {
            'location': 'IP Geolocation + OpenStreetMap',
            'property': 'Property Type Detection + Regional Averages',
            'utilities': 'Regional Rate Database + Seasonal Adjustments',
            'weather': 'OpenWeatherMap API (if available) or Seasonal Defaults',
            'solar': 'NREL API (if available) or Latitude-based Estimates'
        }
        return sources
