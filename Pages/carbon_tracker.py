import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class CarbonFootprintTracker:
    """
    Carbon Footprint Tracker
    Monitors environmental impact and provides offset calculations
    """
    
    def __init__(self):
        self.consumption_data = pd.DataFrame()
        self.emission_factors = {}
        self.offset_projects = {}
        self.tracking_history = []
        
        # Comprehensive emission factors (kg CO2 per kWh) by region and energy source
        self.emission_factors = {
            'US': {
                'northeast': {
                    'grid_mix': 0.35,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'west_coast': {
                    'grid_mix': 0.25,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'southwest': {
                    'grid_mix': 0.45,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'southeast': {
                    'grid_mix': 0.50,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'midwest': {
                    'grid_mix': 0.55,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'mountain': {
                    'grid_mix': 0.40,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                }
            },
            'EU': {
                'nordic': {
                    'grid_mix': 0.15,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'central': {
                    'grid_mix': 0.35,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'southern': {
                    'grid_mix': 0.45,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                },
                'eastern': {
                    'grid_mix': 0.60,
                    'coal': 0.95,
                    'natural_gas': 0.45,
                    'nuclear': 0.0,
                    'hydro': 0.0,
                    'wind': 0.0,
                    'solar': 0.0,
                    'biomass': 0.45
                }
            },
            'default': {
                'grid_mix': 0.42,
                'coal': 0.95,
                'natural_gas': 0.45,
                'nuclear': 0.0,
                'hydro': 0.0,
                'wind': 0.0,
                'solar': 0.0,
                'biomass': 0.45
            }
        }
        
        # Offset project types and their effectiveness
        self.offset_projects = {
            'tree_planting': {
                'co2_per_unit': 22,  # kg CO2 per tree per year
                'cost_per_unit': 5,   # USD per tree
                'lifespan_years': 40,
                'maintenance_cost': 0.5,  # USD per tree per year
                'description': 'Tree planting and forest restoration'
            },
            'renewable_energy': {
                'co2_per_unit': 1000,  # kg CO2 per MWh
                'cost_per_unit': 50,    # USD per MWh
                'lifespan_years': 25,
                'maintenance_cost': 2,   # USD per MWh per year
                'description': 'Renewable energy credits (RECs)'
            },
            'carbon_capture': {
                'co2_per_unit': 1000,  # kg CO2 per ton
                'cost_per_unit': 100,   # USD per ton
                'lifespan_years': 100,
                'maintenance_cost': 0,   # No ongoing maintenance
                'description': 'Direct air capture and storage'
            },
            'ocean_restoration': {
                'co2_per_unit': 500,   # kg CO2 per project
                'cost_per_unit': 25,    # USD per project
                'lifespan_years': 20,
                'maintenance_cost': 1,   # USD per project per year
                'description': 'Ocean cleanup and restoration'
            },
            'soil_carbon': {
                'co2_per_unit': 200,   # kg CO2 per acre
                'cost_per_unit': 15,    # USD per acre
                'lifespan_years': 30,
                'maintenance_cost': 0.5, # USD per acre per year
                'description': 'Soil carbon sequestration'
            }
        }
        
        # Transportation emission factors (kg CO2 per unit)
        self.transport_factors = {
            'car_gasoline': 2.3,      # per mile
            'car_electric': 0.5,      # per mile (grid dependent)
            'bus': 0.14,              # per mile
            'train': 0.14,            # per mile
            'plane_domestic': 0.25,   # per mile
            'plane_international': 0.18, # per mile
            'ship': 0.04              # per mile
        }
        
        # Lifestyle emission factors
        self.lifestyle_factors = {
            'meat_heavy': 2.5,        # kg CO2 per day
            'meat_moderate': 1.5,     # kg CO2 per day
            'vegetarian': 0.8,        # kg CO2 per day
            'vegan': 0.5,             # kg CO2 per day
            'fast_fashion': 0.3,      # kg CO2 per item
            'sustainable_fashion': 0.1, # kg CO2 per item
            'single_use_plastics': 0.02, # kg CO2 per item
            'reusable_items': 0.005   # kg CO2 per item
        }
    
    def add_consumption_data(self, date: str, usage_kwh: float, location: Dict = None, 
                           energy_source: str = 'grid_mix', additional_data: Dict = None):
        """
        Add consumption data for tracking
        """
        if not location:
            location = {'country': 'US', 'region': 'default'}
        
        # Calculate emissions
        emissions = self.calculate_emissions(usage_kwh, location, energy_source)
        
        # Create record
        record = {
            'date': date,
            'usage_kwh': usage_kwh,
            'energy_source': energy_source,
            'location': location,
            'emissions_kg_co2': emissions['total_co2_kg'],
            'emission_factor': emissions['emission_factor_kg_co2_per_kwh'],
            'additional_data': additional_data or {}
        }
        
        # Add to tracking history
        self.tracking_history.append(record)
        
        # Update consumption dataframe
        df_record = pd.DataFrame([record])
        if self.consumption_data.empty:
            self.consumption_data = df_record
        else:
            self.consumption_data = pd.concat([self.consumption_data, df_record], ignore_index=True)
        
        print(f"✅ Added consumption data: {date} - {usage_kwh} kWh = {emissions['total_co2_kg']:.2f} kg CO2")
        return record
    
    def calculate_emissions(self, usage_kwh: float, location: Dict = None, 
                          energy_source: str = 'grid_mix') -> Dict:
        """
        Calculate CO2 emissions from electricity usage
        """
        if not location:
            location = {'country': 'US', 'region': 'default'}
        
        country = location.get('country', 'US')
        region = location.get('region', 'default')
        
        # Get emission factor
        if country in self.emission_factors:
            if region in self.emission_factors[country]:
                if energy_source in self.emission_factors[country][region]:
                    emission_factor = self.emission_factors[country][region][energy_source]
                else:
                    emission_factor = self.emission_factors[country][region]['grid_mix']
            else:
                emission_factor = self.emission_factors[country].get('default', 0.42)
        else:
            emission_factor = self.emission_factors['default']['grid_mix']
        
        # Calculate CO2 emissions
        co2_kg = usage_kwh * emission_factor
        
        # Calculate offset equivalents
        offset_equivalents = self._calculate_offset_equivalents(co2_kg)
        
        return {
            'usage_kwh': usage_kwh,
            'energy_source': energy_source,
            'emission_factor_kg_co2_per_kwh': emission_factor,
            'total_co2_kg': round(co2_kg, 2),
            'location': location,
            'offset_equivalents': offset_equivalents
        }
    
    def _calculate_offset_equivalents(self, co2_kg: float) -> Dict:
        """Calculate various offset equivalents"""
        return {
            'trees_needed': round(co2_kg / self.offset_projects['tree_planting']['co2_per_unit'], 1),
            'renewable_credits': round(co2_kg / self.offset_projects['renewable_energy']['co2_per_unit'], 3),
            'car_miles': round(co2_kg / self.transport_factors['car_gasoline'], 1),
            'flight_hours': round(co2_kg / (self.transport_factors['plane_domestic'] * 500), 2),  # Assume 500 mph
            'bus_rides': round(co2_kg / (self.transport_factors['bus'] * 10), 1),  # Assume 10 mile rides
            'plastic_items': round(co2_kg / self.lifestyle_factors['single_use_plastics'], 1)
        }
    
    def add_transportation_data(self, date: str, transport_type: str, distance_miles: float, 
                              passengers: int = 1, location: Dict = None):
        """
        Add transportation emissions data
        """
        if transport_type not in self.transport_factors:
            print(f"❌ Unknown transport type: {transport_type}")
            return None
        
        # Calculate emissions
        emission_factor = self.transport_factors[transport_type]
        total_emissions = (distance_miles * emission_factor) / passengers  # Per passenger
        
        # Create record
        record = {
            'date': date,
            'transport_type': transport_type,
            'distance_miles': distance_miles,
            'passengers': passengers,
            'emissions_kg_co2': round(total_emissions, 2),
            'emission_factor': emission_factor,
            'location': location or {'country': 'US', 'region': 'default'},
            'category': 'transportation'
        }
        
        # Add to tracking history
        self.tracking_history.append(record)
        
        print(f"✅ Added transport data: {date} - {transport_type} {distance_miles} miles = {total_emissions:.2f} kg CO2")
        return record
    
    def add_lifestyle_data(self, date: str, lifestyle_choice: str, quantity: int = 1, 
                          location: Dict = None):
        """
        Add lifestyle emissions data
        """
        if lifestyle_choice not in self.lifestyle_factors:
            print(f"❌ Unknown lifestyle choice: {lifestyle_choice}")
            return None
        
        # Calculate emissions
        emission_factor = self.lifestyle_factors[lifestyle_choice]
        total_emissions = quantity * emission_factor
        
        # Create record
        record = {
            'date': date,
            'lifestyle_choice': lifestyle_choice,
            'quantity': quantity,
            'emissions_kg_co2': round(total_emissions, 2),
            'emission_factor': emission_factor,
            'location': location or {'country': 'US', 'region': 'default'},
            'category': 'lifestyle'
        }
        
        # Add to tracking history
        self.tracking_history.append(record)
        
        print(f"✅ Added lifestyle data: {date} - {lifestyle_choice} x{quantity} = {total_emissions:.2f} kg CO2")
        return record
    
    def get_carbon_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get comprehensive carbon footprint summary
        """
        if not self.tracking_history:
            return {"message": "No tracking data available"}
        
        # Filter by date range if specified
        if start_date and end_date:
            filtered_data = [
                record for record in self.tracking_history
                if start_date <= record['date'] <= end_date
            ]
        else:
            filtered_data = self.tracking_history
        
        if not filtered_data:
            return {"message": "No data in specified date range"}
        
        # Calculate totals by category
        total_emissions = sum(record['emissions_kg_co2'] for record in filtered_data)
        
        categories = {}
        for record in filtered_data:
            category = record.get('category', 'electricity')
            if category not in categories:
                categories[category] = {
                    'total_emissions': 0,
                    'record_count': 0,
                    'details': []
                }
            
            categories[category]['total_emissions'] += record['emissions_kg_co2']
            categories[category]['record_count'] += 1
            categories[category]['details'].append(record)
        
        # Calculate offset requirements
        offset_requirements = self._calculate_offset_requirements(total_emissions)
        
        # Calculate trends
        trends = self._calculate_emission_trends(filtered_data)
        
        return {
            'date_range': {
                'start': start_date or 'all',
                'end': end_date or 'all'
            },
            'total_emissions_kg_co2': round(total_emissions, 2),
            'categories': categories,
            'offset_requirements': offset_requirements,
            'trends': trends,
            'recommendations': self._generate_recommendations(categories, total_emissions)
        }
    
    def _calculate_offset_requirements(self, total_emissions: float) -> Dict:
        """Calculate offset requirements for different project types"""
        requirements = {}
        
        for project_type, project_data in self.offset_projects.items():
            units_needed = total_emissions / project_data['co2_per_unit']
            total_cost = units_needed * project_data['cost_per_unit']
            annual_maintenance = units_needed * project_data['maintenance_cost']
            
            requirements[project_type] = {
                'units_needed': round(units_needed, 1),
                'total_cost_usd': round(total_cost, 2),
                'annual_maintenance_usd': round(annual_maintenance, 2),
                'description': project_data['description'],
                'effectiveness': f"{project_data['co2_per_unit']} kg CO2 per unit"
            }
        
        return requirements
    
    def _calculate_emission_trends(self, data: List[Dict]) -> Dict:
        """Calculate emission trends over time"""
        if not data:
            return {}
        
        # Group by date and calculate daily totals
        daily_emissions = {}
        for record in data:
            date = record['date']
            if date not in daily_emissions:
                daily_emissions[date] = 0
            daily_emissions[date] += record['emissions_kg_co2']
        
        # Calculate trend metrics
        dates = sorted(daily_emissions.keys())
        emissions = [daily_emissions[date] for date in dates]
        
        if len(emissions) > 1:
            # Simple linear trend
            trend_slope = (emissions[-1] - emissions[0]) / len(emissions)
            trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
            
            # Calculate moving average
            window = min(7, len(emissions))  # 7-day moving average
            moving_avg = []
            for i in range(len(emissions)):
                start = max(0, i - window + 1)
                moving_avg.append(sum(emissions[start:i+1]) / (i - start + 1))
            
            return {
                'trend_direction': trend_direction,
                'trend_slope': round(trend_slope, 3),
                'daily_average': round(sum(emissions) / len(emissions), 2),
                'peak_day': {
                    'date': max(daily_emissions, key=daily_emissions.get),
                    'emissions': round(max(daily_emissions.values()), 2)
                },
                'lowest_day': {
                    'date': min(daily_emissions, key=daily_emissions.get),
                    'emissions': round(min(daily_emissions.values()), 2)
                },
                'moving_average': [round(avg, 2) for avg in moving_avg[-5:]]  # Last 5 days
            }
        else:
            return {
                'trend_direction': 'insufficient_data',
                'daily_average': round(emissions[0], 2) if emissions else 0
            }
    
    def _generate_recommendations(self, categories: Dict, total_emissions: float) -> List[str]:
        """Generate recommendations based on carbon footprint analysis"""
        recommendations = []
        
        # Electricity recommendations
        if 'electricity' in categories:
            elec_emissions = categories['electricity']['total_emissions']
            if elec_emissions > total_emissions * 0.7:  # >70% of total
                recommendations.append("⚡ Electricity is your largest emissions source - consider solar panels or energy efficiency upgrades")
        
        # Transportation recommendations
        if 'transportation' in categories:
            transport_emissions = categories['transportation']['total_emissions']
            if transport_emissions > total_emissions * 0.3:  # >30% of total
                recommendations.append("🚗 Transportation emissions are significant - consider public transport, carpooling, or electric vehicles")
        
        # Lifestyle recommendations
        if 'lifestyle' in categories:
            lifestyle_emissions = categories['lifestyle']['total_emissions']
            if lifestyle_emissions > total_emissions * 0.2:  # >20% of total
                recommendations.append("🌱 Lifestyle choices contribute to emissions - consider plant-based diet and sustainable products")
        
        # General recommendations based on total emissions
        if total_emissions > 1000:  # >1 ton CO2
            recommendations.append("🌍 Your carbon footprint is above average - focus on high-impact changes first")
        elif total_emissions < 500:  # <0.5 ton CO2
            recommendations.append("🎉 Excellent! Your carbon footprint is below average - consider offsetting remaining emissions")
        
        # Offset recommendations
        recommendations.append("🌳 Consider carbon offset projects to neutralize your emissions")
        recommendations.append("📊 Track your progress monthly to see improvement trends")
        
        return recommendations
    
    def suggest_offset_strategy(self, target_reduction: float = None) -> Dict:
        """
        Suggest optimal offset strategy based on current footprint
        """
        if not self.tracking_history:
            return {"message": "No tracking data available"}
        
        # Get current footprint
        summary = self.get_carbon_summary()
        current_emissions = summary.get('total_emissions_kg_co2', 0)
        
        if not target_reduction:
            target_reduction = current_emissions * 0.1  # 10% reduction
        
        # Calculate offset requirements
        offset_requirements = self._calculate_offset_requirements(target_reduction)
        
        # Rank projects by cost-effectiveness
        cost_effectiveness = []
        for project_type, project_data in offset_requirements.items():
            cost_per_kg = project_data['total_cost_usd'] / target_reduction
            cost_effectiveness.append({
                'project_type': project_type,
                'cost_per_kg_co2': cost_per_kg,
                'total_cost': project_data['total_cost_usd'],
                'description': project_data['description']
            })
        
        # Sort by cost-effectiveness
        cost_effectiveness.sort(key=lambda x: x['cost_per_kg_co2'])
        
        return {
            'current_emissions_kg_co2': current_emissions,
            'target_reduction_kg_co2': target_reduction,
            'offset_requirements': offset_requirements,
            'recommended_strategy': cost_effectiveness,
            'budget_options': {
                'low_budget': cost_effectiveness[0] if cost_effectiveness else None,
                'medium_budget': cost_effectiveness[len(cost_effectiveness)//2] if cost_effectiveness else None,
                'high_budget': cost_effectiveness[-1] if cost_effectiveness else None
            }
        }
    
    def export_data(self, format: str = 'json', filename: str = None) -> str:
        """
        Export tracking data in various formats
        """
        if not self.tracking_history:
            return "No data to export"
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"carbon_tracking_{timestamp}"
        
        if format.lower() == 'json':
            filepath = f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(self.tracking_history, f, indent=2)
            return f"Data exported to {filepath}"
        
        elif format.lower() == 'csv':
            filepath = f"{filename}.csv"
            df = pd.DataFrame(self.tracking_history)
            df.to_csv(filepath, index=False)
            return f"Data exported to {filepath}"
        
        else:
            return f"Unsupported format: {format}"
    
    def get_progress_report(self, baseline_date: str = None) -> Dict:
        """
        Generate progress report comparing current vs baseline
        """
        if not self.tracking_history:
            return {"message": "No tracking data available"}
        
        if not baseline_date:
            # Use first month as baseline
            dates = sorted(set(record['date'][:7] for record in self.tracking_history))  # YYYY-MM
            baseline_date = dates[0] if dates else None
        
        if not baseline_date:
            return {"message": "Cannot determine baseline date"}
        
        # Get baseline month data
        baseline_data = [
            record for record in self.tracking_history
            if record['date'].startswith(baseline_date)
        ]
        
        # Get current month data
        current_date = datetime.now().strftime('%Y-%m')
        current_data = [
            record for record in self.tracking_history
            if record['date'].startswith(current_date)
        ]
        
        if not baseline_data or not current_data:
            return {"message": "Insufficient data for comparison"}
        
        baseline_emissions = sum(record['emissions_kg_co2'] for record in baseline_data)
        current_emissions = sum(record['emissions_kg_co2'] for record in current_data)
        
        change = current_emissions - baseline_emissions
        change_percentage = (change / baseline_emissions) * 100 if baseline_emissions > 0 else 0
        
        return {
            'baseline_month': baseline_date,
            'current_month': current_date,
            'baseline_emissions_kg_co2': round(baseline_emissions, 2),
            'current_emissions_kg_co2': round(current_emissions, 2),
            'change_kg_co2': round(change, 2),
            'change_percentage': round(change_percentage, 1),
            'trend': 'improving' if change < 0 else 'worsening' if change > 0 else 'stable',
            'progress_message': self._get_progress_message(change_percentage)
        }
    
    def _get_progress_message(self, change_percentage: float) -> str:
        """Get human-readable progress message"""
        if change_percentage <= -20:
            return "🎉 Outstanding progress! You've significantly reduced your carbon footprint."
        elif change_percentage <= -10:
            return "👍 Great work! You're making steady progress toward sustainability."
        elif change_percentage <= 0:
            return "✅ Good job! You're maintaining or slightly improving your footprint."
        elif change_percentage <= 10:
            return "⚠️  Your emissions have increased slightly. Review recent changes."
        else:
            return "🚨 Significant increase in emissions. Time to reassess your energy usage."
