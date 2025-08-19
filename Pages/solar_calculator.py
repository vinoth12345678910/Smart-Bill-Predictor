import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class SolarFeasibilityCalculator:
    """
    Solar Feasibility & ROI Calculator
    Calculates solar potential, costs, savings, and ROI for residential installations
    """
    
    def __init__(self):
        self.solar_irradiance_data = {}
        self.panel_efficiency_data = {}
        self.tariff_data = {}
        self.location_data = {}
        
        # Default solar panel specifications
        self.default_panels = {
            'monocrystalline': {
                'efficiency': 0.20,  # 20%
                'degradation_rate': 0.005,  # 0.5% per year
                'lifespan': 25,  # years
                'cost_per_watt': 0.8,  # USD per watt
                'temperature_coefficient': -0.004,  # -0.4% per °C
                'size_sqm': 1.6,  # square meters
                'weight_kg': 18.5  # kilograms
            },
            'polycrystalline': {
                'efficiency': 0.17,  # 17%
                'degradation_rate': 0.006,  # 0.6% per year
                'lifespan': 25,  # years
                'cost_per_watt': 0.6,  # USD per watt
                'temperature_coefficient': -0.004,  # -0.4% per °C
                'size_sqm': 1.6,  # square meters
                'weight_kg': 18.5  # kilograms
            },
            'thin_film': {
                'efficiency': 0.12,  # 12%
                'degradation_rate': 0.008,  # 0.8% per year
                'lifespan': 20,  # years
                'cost_per_watt': 0.4,  # USD per watt
                'temperature_coefficient': -0.002,  # -0.2% per °C
                'size_sqm': 1.6,  # square meters
                'weight_kg': 12.0  # kilograms
            }
        }
        
        # Default installation costs (USD per watt)
        self.installation_costs = {
            'residential_small': 2.5,      # < 5kW
            'residential_medium': 2.2,     # 5-10kW
            'residential_large': 2.0,      # > 10kW
            'commercial': 1.8,             # Commercial installations
            'utility_scale': 1.2           # Large utility installations
        }
        
        # Default maintenance costs
        self.maintenance_costs = {
            'annual_inspection': 150,      # USD per year
            'cleaning': 100,               # USD per year
            'inverter_replacement': 2000,  # USD every 10-15 years
            'panel_replacement': 5000      # USD every 25 years
        }
    
    def set_location(self, latitude: float, longitude: float, city: str, country: str = "US"):
        """Set location for solar calculations"""
        self.location_data = {
            'latitude': latitude,
            'longitude': longitude,
            'city': city,
            'country': country
        }
        print(f"📍 Location set: {city}, {country} ({latitude:.4f}, {longitude:.4f})")
    
    def fetch_solar_irradiance_nrel(self, api_key: str = None) -> Dict:
        """
        Fetch solar irradiance data from NREL API
        Requires NREL API key (free from https://developer.nrel.gov/)
        """
        if not self.location_data:
            raise ValueError("Location must be set before fetching irradiance data")
        
        if not api_key:
            print("⚠️  No NREL API key provided. Using default irradiance values.")
            return self._get_default_irradiance()
        
        try:
            # NREL API endpoint for solar resource data
            url = "https://developer.nrel.gov/api/solar/solar_resource/v1.json"
            params = {
                'api_key': api_key,
                'lat': self.location_data['latitude'],
                'lon': self.location_data['longitude'],
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'outputs' in data:
                irradiance = data['outputs']
                self.solar_irradiance_data = {
                    'annual_ghi': irradiance.get('avg_ghi', {}).get('annual', 0),  # Global Horizontal Irradiance
                    'annual_dni': irradiance.get('avg_dni', {}).get('annual', 0),  # Direct Normal Irradiance
                    'annual_dhi': irradiance.get('avg_dhi', {}).get('annual', 0),  # Diffuse Horizontal Irradiance
                    'monthly_ghi': irradiance.get('avg_ghi', {}).get('monthly', {}),
                    'source': 'NREL API'
                }
                print("✅ Solar irradiance data fetched from NREL API")
                return self.solar_irradiance_data
            else:
                print("⚠️  No irradiance data in NREL response. Using defaults.")
                return self._get_default_irradiance()
                
        except Exception as e:
            print(f"❌ Error fetching NREL data: {e}")
            return self._get_default_irradiance()
    
    def _get_default_irradiance(self) -> Dict:
        """Get default irradiance values based on latitude"""
        lat = abs(self.location_data['latitude'])
        
        # Default values based on latitude bands
        if lat < 30:  # Tropical
            annual_ghi = 5.5  # kWh/m²/day
        elif lat < 45:  # Subtropical
            annual_ghi = 4.8  # kWh/m²/day
        elif lat < 60:  # Temperate
            annual_ghi = 4.2  # kWh/m²/day
        else:  # Polar
            annual_ghi = 3.5  # kWh/m²/day
        
        # Monthly variations (simplified)
        monthly_ghi = {}
        for month in range(1, 13):
            if month in [6, 7, 8]:  # Summer months
                monthly_ghi[month] = annual_ghi * 1.2
            elif month in [12, 1, 2]:  # Winter months
                monthly_ghi[month] = annual_ghi * 0.8
            else:  # Spring/Fall
                monthly_ghi[month] = annual_ghi
        
        self.solar_irradiance_data = {
            'annual_ghi': annual_ghi,
            'annual_dni': annual_ghi * 0.7,
            'annual_dhi': annual_ghi * 0.3,
            'monthly_ghi': monthly_ghi,
            'source': 'Default (latitude-based)'
        }
        
        return self.solar_irradiance_data
    
    def set_panel_specifications(self, panel_type: str = 'monocrystalline', 
                               custom_efficiency: float = None,
                               custom_cost: float = None):
        """Set solar panel specifications"""
        if panel_type not in self.default_panels:
            raise ValueError(f"Panel type must be one of: {list(self.default_panels.keys())}")
        
        panel_specs = self.default_panels[panel_type].copy()
        
        if custom_efficiency:
            panel_specs['efficiency'] = custom_efficiency
        if custom_cost:
            panel_specs['cost_per_watt'] = custom_cost
        
        self.panel_efficiency_data = panel_specs
        print(f"✅ Panel specifications set: {panel_type} (Efficiency: {panel_specs['efficiency']:.1%})")
    
    def set_tariff_data(self, electricity_rate: float, rate_escalation: float = 0.03):
        """
        Set electricity tariff data for ROI calculations
        
        Args:
            electricity_rate: Current electricity rate in USD/kWh
            rate_escalation: Annual rate increase (default 3%)
        """
        self.tariff_data = {
            'current_rate': electricity_rate,
            'escalation_rate': rate_escalation,
            'annual_usage': 12000,  # Default kWh per year
            'peak_hours': 0.3,      # 30% of usage during peak hours
            'off_peak_rate': electricity_rate * 0.7  # 30% discount for off-peak
        }
        print(f"✅ Tariff data set: ${electricity_rate:.3f}/kWh (Escalation: {rate_escalation:.1%})")
    
    def calculate_system_size(self, roof_area: float, panel_type: str = 'monocrystalline') -> Dict:
        """
        Calculate optimal solar system size based on roof area
        
        Args:
            roof_area: Available roof area in square meters
            panel_type: Type of solar panel to use
        """
        if not self.panel_efficiency_data:
            self.set_panel_specifications(panel_type)
        
        panel_specs = self.panel_efficiency_data
        
        # Calculate how many panels can fit
        panel_area = panel_specs['size_sqm']
        max_panels = int(roof_area / panel_specs['size_sqm'])
        
        # Calculate system capacity
        panel_wattage = 400  # Standard residential panel
        system_capacity = max_panels * panel_wattage / 1000  # Convert to kW
        
        # Adjust for roof orientation and shading (typical factors)
        orientation_factor = 0.85  # South-facing with minimal shading
        shading_factor = 0.95     # Minimal shading
        
        effective_capacity = system_capacity * orientation_factor * shading_factor
        
        return {
            'roof_area': roof_area,
            'panel_area': panel_area,
            'max_panels': max_panels,
            'system_capacity_kw': system_capacity,
            'effective_capacity_kw': effective_capacity,
            'orientation_factor': orientation_factor,
            'shading_factor': shading_factor,
            'panel_wattage': panel_wattage
        }
    
    def calculate_energy_production(self, system_capacity_kw: float, 
                                  panel_type: str = 'monocrystalline',
                                  years: int = 25) -> Dict:
        """
        Calculate annual energy production and degradation over time
        
        Args:
            system_capacity_kw: System capacity in kilowatts
            panel_type: Type of solar panel
            years: Number of years to project
        """
        if not self.solar_irradiance_data:
            raise ValueError("Solar irradiance data not available. Set location first.")
        
        if not self.panel_efficiency_data:
            self.set_panel_specifications(panel_type)
        
        panel_specs = self.panel_efficiency_data
        irradiance = self.solar_irradiance_data
        
        # Calculate annual production
        annual_ghi = irradiance['annual_ghi']  # kWh/m²/day
        days_per_year = 365.25
        
        # System losses (typical residential)
        system_losses = {
            'inverter_efficiency': 0.96,      # 96% inverter efficiency
            'wiring_losses': 0.98,            # 2% wiring losses
            'soiling': 0.95,                  # 5% soiling losses
            'mismatch': 0.98,                 # 2% panel mismatch
            'temperature': 0.90               # 10% temperature losses
        }
        
        overall_efficiency = np.prod(list(system_losses.values()))
        
        # Annual energy production (kWh)
        annual_production = (system_capacity_kw * 1000 * annual_ghi * days_per_year * 
                           panel_specs['efficiency'] * overall_efficiency) / 1000
        
        # Calculate production over years with degradation
        yearly_production = []
        cumulative_production = 0
        
        for year in range(1, years + 1):
            degradation_factor = (1 - panel_specs['degradation_rate']) ** (year - 1)
            year_production = annual_production * degradation_factor
            yearly_production.append(year_production)
            cumulative_production += year_production
        
        return {
            'system_capacity_kw': system_capacity_kw,
            'annual_ghi': annual_ghi,
            'system_losses': system_losses,
            'overall_efficiency': overall_efficiency,
            'annual_production_kwh': annual_production,
            'yearly_production': yearly_production,
            'cumulative_production_kwh': cumulative_production,
            'degradation_rate': panel_specs['degradation_rate'],
            'projection_years': years
        }
    
    def calculate_costs(self, system_capacity_kw: float, 
                       installation_type: str = 'residential_medium') -> Dict:
        """
        Calculate total system costs including installation and maintenance
        
        Args:
            system_capacity_kw: System capacity in kilowatts
            installation_type: Type of installation
        """
        if installation_type not in self.installation_costs:
            raise ValueError(f"Installation type must be one of: {list(self.installation_costs.keys())}")
        
        # Panel costs
        panel_cost_per_watt = self.panel_efficiency_data['cost_per_watt']
        panel_cost = system_capacity_kw * 1000 * panel_cost_per_watt
        
        # Installation costs
        installation_cost_per_watt = self.installation_costs[installation_type]
        installation_cost = system_capacity_kw * 1000 * installation_cost_per_watt
        
        # Additional equipment costs
        inverter_cost = system_capacity_kw * 1000 * 0.3  # $0.30 per watt
        mounting_cost = system_capacity_kw * 1000 * 0.2  # $0.20 per watt
        electrical_cost = system_capacity_kw * 1000 * 0.15  # $0.15 per watt
        
        # Total upfront cost
        total_upfront_cost = panel_cost + installation_cost + inverter_cost + mounting_cost + electrical_cost
        
        # Maintenance costs over 25 years
        annual_maintenance = (self.maintenance_costs['annual_inspection'] + 
                            self.maintenance_costs['cleaning'])
        
        # Inverter replacement (every 10-15 years)
        inverter_replacements = int(25 / 12.5)  # Every 12.5 years
        total_inverter_cost = inverter_replacements * self.maintenance_costs['inverter_replacement']
        
        # Panel replacement (every 25 years)
        total_panel_replacement_cost = self.maintenance_costs['panel_replacement']
        
        total_maintenance_cost = (annual_maintenance * 25 + 
                                total_inverter_cost + 
                                total_panel_replacement_cost)
        
        total_lifetime_cost = total_upfront_cost + total_maintenance_cost
        
        return {
            'system_capacity_kw': system_capacity_kw,
            'panel_cost': panel_cost,
            'installation_cost': installation_cost,
            'inverter_cost': inverter_cost,
            'mounting_cost': mounting_cost,
            'electrical_cost': electrical_cost,
            'total_upfront_cost': total_upfront_cost,
            'annual_maintenance': annual_maintenance,
            'total_maintenance_cost': total_maintenance_cost,
            'total_lifetime_cost': total_lifetime_cost,
            'cost_per_watt': total_upfront_cost / (system_capacity_kw * 1000)
        }
    
    def calculate_roi(self, system_capacity_kw: float, 
                     installation_type: str = 'residential_medium',
                     years: int = 25) -> Dict:
        """
        Calculate ROI, payback period, and cash flow analysis
        
        Args:
            system_capacity_kw: System capacity in kilowatts
            installation_type: Type of installation
            years: Analysis period in years
        """
        if not self.tariff_data:
            raise ValueError("Tariff data not set. Use set_tariff_data() first.")
        
        # Calculate energy production
        production = self.calculate_energy_production(system_capacity_kw, years=years)
        
        # Calculate costs
        costs = self.calculate_costs(system_capacity_kw, installation_type)
        
        # Calculate annual savings
        current_rate = self.tariff_data['current_rate']
        escalation_rate = self.tariff_data['escalation_rate']
        
        annual_savings = []
        cumulative_savings = 0
        net_cash_flow = []
        
        for year in range(1, years + 1):
            # Electricity rate with escalation
            year_rate = current_rate * (1 + escalation_rate) ** (year - 1)
            
            # Energy savings for this year
            year_production = production['yearly_production'][year - 1]
            year_savings = year_production * year_rate
            
            annual_savings.append(year_savings)
            cumulative_savings += year_savings
            
            # Net cash flow (savings - maintenance)
            if year == 1:
                year_maintenance = costs['annual_maintenance']
            elif year % 12 == 0:  # Inverter replacement
                year_maintenance = costs['annual_maintenance'] + self.maintenance_costs['inverter_replacement']
            elif year == 25:  # Panel replacement
                year_maintenance = costs['annual_maintenance'] + self.maintenance_costs['panel_replacement']
            else:
                year_maintenance = costs['annual_maintenance']
            
            net_cash_flow.append(year_savings - year_maintenance)
        
        # Calculate payback period
        upfront_cost = costs['total_upfront_cost']
        payback_year = None
        
        for year in range(years):
            if cumulative_savings >= upfront_cost:
                payback_year = year + 1
                break
        
        # Calculate ROI metrics
        total_savings = cumulative_savings
        total_cost = costs['total_lifetime_cost']
        net_benefit = total_savings - total_cost
        
        if total_cost > 0:
            roi_percentage = (net_benefit / total_cost) * 100
        else:
            roi_percentage = 0
        
        # Calculate NPV (Net Present Value) with 5% discount rate
        discount_rate = 0.05
        npv = -upfront_cost
        
        for year in range(years):
            npv += net_cash_flow[year] / ((1 + discount_rate) ** (year + 1))
        
        return {
            'system_capacity_kw': system_capacity_kw,
            'analysis_period_years': years,
            'upfront_cost': upfront_cost,
            'total_lifetime_cost': total_cost,
            'total_energy_production_kwh': production['cumulative_production_kwh'],
            'total_savings': total_savings,
            'net_benefit': net_benefit,
            'roi_percentage': roi_percentage,
            'payback_period_years': payback_year,
            'npv_5_percent': npv,
            'annual_savings': annual_savings,
            'net_cash_flow': net_cash_flow,
            'electricity_rate_escalation': escalation_rate,
            'discount_rate': discount_rate
        }
    
    def generate_report(self, roof_area: float, panel_type: str = 'monocrystalline',
                       installation_type: str = 'residential_medium') -> Dict:
        """
        Generate comprehensive solar feasibility report
        
        Args:
            roof_area: Available roof area in square meters
            panel_type: Type of solar panel
            installation_type: Type of installation
        """
        # Calculate system size
        system_size = self.calculate_system_size(roof_area, panel_type)
        
        # Calculate energy production
        production = self.calculate_energy_production(system_size['effective_capacity_kw'], panel_type)
        
        # Calculate costs
        costs = self.calculate_costs(system_size['effective_capacity_kw'], installation_type)
        
        # Calculate ROI
        roi = self.calculate_roi(system_size['effective_capacity_kw'], installation_type)
        
        # Compile comprehensive report
        report = {
            'location': self.location_data,
            'solar_data': self.solar_irradiance_data,
            'panel_specifications': self.panel_efficiency_data,
            'tariff_data': self.tariff_data,
            'system_design': system_size,
            'energy_production': production,
            'cost_analysis': costs,
            'roi_analysis': roi,
            'summary': {
                'recommendation': self._get_recommendation(roi['roi_percentage'], roi['payback_period_years']),
                'key_benefits': self._get_key_benefits(roi, production),
                'risks': self._get_risks(roi, production),
                'next_steps': self._get_next_steps()
            }
        }
        
        return report
    
    def _get_recommendation(self, roi_percentage: float, payback_years: int) -> str:
        """Generate recommendation based on ROI analysis"""
        if roi_percentage > 200 and payback_years <= 5:
            return "Highly Recommended - Excellent ROI and quick payback"
        elif roi_percentage > 100 and payback_years <= 8:
            return "Recommended - Good ROI with reasonable payback period"
        elif roi_percentage > 50 and payback_years <= 12:
            return "Moderately Recommended - Positive ROI but longer payback"
        elif roi_percentage > 0:
            return "Consider with Caution - Positive ROI but very long payback"
        else:
            return "Not Recommended - Negative ROI"
    
    def _get_key_benefits(self, roi: Dict, production: Dict) -> List[str]:
        """Generate list of key benefits"""
        benefits = [
            f"Lifetime energy production: {production['cumulative_production_kwh']:,.0f} kWh",
            f"Total savings: ${roi['total_savings']:,.0f} over {roi['analysis_period_years']} years",
            f"ROI: {roi['roi_percentage']:.1f}%",
            f"Payback period: {roi['payback_period_years']} years",
            f"Net Present Value: ${roi['npv_5_percent']:,.0f} (5% discount rate)"
        ]
        return benefits
    
    def _get_risks(self, roi: Dict, production: Dict) -> List[str]:
        """Generate list of potential risks"""
        risks = [
            "Panel efficiency degradation over time",
            "Weather variations affecting production",
            "Maintenance and replacement costs",
            "Electricity rate changes",
            "Technology improvements making current system obsolete"
        ]
        return risks
    
    def _get_next_steps(self) -> List[str]:
        """Generate list of next steps"""
        steps = [
            "Get multiple quotes from solar installers",
            "Verify roof condition and structural integrity",
            "Check local permits and regulations",
            "Review financing options and incentives",
            "Schedule professional site assessment"
        ]
        return steps
