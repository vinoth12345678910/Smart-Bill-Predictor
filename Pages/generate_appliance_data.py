import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

def generate_appliance_dataset(num_appliances=5, days_of_data=30, readings_per_day=24):
    """
    Generate sample appliance dataset for testing the health prediction system
    
    Args:
        num_appliances: Number of appliances to generate
        days_of_data: Number of days of historical data
        readings_per_day: Number of readings per day (hourly = 24)
    """
    
    # Appliance categories and their characteristics
    appliance_types = {
        'refrigerator': {
            'power_rating': 150,  # watts
            'energy_pattern': 'cyclic',  # cycles on/off
            'temperature_sensitive': True,
            'vibration_low': True
        },
        'washing_machine': {
            'power_rating': 500,
            'energy_pattern': 'burst',  # high power during operation
            'temperature_sensitive': False,
            'vibration_low': False
        },
        'dishwasher': {
            'power_rating': 1800,
            'energy_pattern': 'burst',
            'temperature_sensitive': True,
            'vibration_low': True
        },
        'microwave': {
            'power_rating': 1200,
            'energy_pattern': 'burst',
            'temperature_sensitive': False,
            'vibration_low': True
        },
        'air_conditioner': {
            'power_rating': 2000,
            'energy_pattern': 'cyclic',
            'temperature_sensitive': True,
            'vibration_low': False
        }
    }
    
    # Generate appliance metadata
    appliances = []
    appliance_ids = []
    
    for i in range(num_appliances):
        appliance_type = random.choice(list(appliance_types.keys()))
        appliance_id = f"{appliance_type}_{i+1:02d}"
        appliance_ids.append(appliance_id)
        
        # Random installation date (1-10 years ago)
        years_ago = random.uniform(1, 10)
        installation_date = (datetime.now() - timedelta(days=years_ago*365)).strftime('%Y-%m-%d')
        
        appliance = {
            'appliance_id': appliance_id,
            'brand': random.choice(['Samsung', 'LG', 'Whirlpool', 'Bosch', 'GE', 'Maytag']),
            'model': f"{appliance_type.upper()}-{random.randint(1000, 9999)}",
            'power_rating': appliance_types[appliance_type]['power_rating'],
            'category': appliance_type,
            'installation_date': installation_date
        }
        appliances.append(appliance)
    
    # Generate historical readings
    all_readings = []
    start_date = datetime.now() - timedelta(days=days_of_data)
    
    for appliance in appliances:
        appliance_id = appliance['appliance_id']
        category = appliance['category']
        power_rating = appliance['power_rating']
        appliance_config = appliance_types[category]
        
        # Generate readings for each hour
        for day in range(days_of_data):
            current_date = start_date + timedelta(days=day)
            
            for hour in range(readings_per_day):
                timestamp = current_date + timedelta(hours=hour)
                
                # Base energy usage (varies by time of day and appliance type)
                base_energy = power_rating / 1000  # Convert to kWh
                
                # Time-based variations
                if category == 'refrigerator':
                    # Refrigerator runs more during day, less at night
                    time_factor = 0.8 + 0.4 * np.sin(2 * np.pi * hour / 24)
                    base_energy *= time_factor
                elif category == 'air_conditioner':
                    # AC runs more during hot hours (10 AM - 6 PM)
                    if 10 <= hour <= 18:
                        time_factor = 1.5
                    else:
                        time_factor = 0.3
                    base_energy *= time_factor
                else:
                    # Other appliances have random usage patterns
                    time_factor = random.uniform(0.1, 1.0)
                    base_energy *= time_factor
                
                # Add some randomness
                energy_usage = base_energy * random.uniform(0.8, 1.2)
                
                # Power factor (usually 0.85-1.0 for appliances)
                power_factor = random.uniform(0.85, 1.0)
                
                # Temperature (if applicable)
                temperature = None
                if appliance_config['temperature_sensitive']:
                    if category == 'refrigerator':
                        temperature = random.uniform(2, 8)  # Cold
                    elif category == 'dishwasher':
                        temperature = random.uniform(50, 70)  # Hot
                    elif category == 'air_conditioner':
                        temperature = random.uniform(18, 25)  # Cool
                
                # Vibration (if applicable)
                vibration = None
                if not appliance_config['vibration_low']:
                    vibration = random.uniform(0.05, 0.15)
                else:
                    vibration = random.uniform(0.01, 0.05)
                
                # Noise level
                noise_level = random.uniform(0.1, 0.3)
                
                # Introduce anomalies (5% chance)
                is_anomaly = random.random() < 0.05
                if is_anomaly:
                    # Energy spike
                    energy_usage *= random.uniform(1.5, 3.0)
                    # Poor power factor
                    power_factor = random.uniform(0.6, 0.8)
                    # High vibration
                    if vibration is not None:
                        vibration *= random.uniform(2.0, 4.0)
                    # High noise
                    noise_level *= random.uniform(1.5, 2.5)
                
                # Introduce gradual degradation over time (aging effect)
                age_factor = 1.0 + (day / days_of_data) * 0.3  # 30% increase over time
                energy_usage *= age_factor
                
                reading = {
                    'appliance_id': appliance_id,
                    'timestamp': timestamp.isoformat(),
                    'energy_usage': round(energy_usage, 4),
                    'power_factor': round(power_factor, 3),
                    'temperature': round(temperature, 1) if temperature else None,
                    'vibration': round(vibration, 3) if vibration else None,
                    'noise_level': round(noise_level, 3),
                    'is_anomaly': is_anomaly
                }
                
                all_readings.append(reading)
    
    return appliances, all_readings

def save_dataset(appliances, readings, appliances_file='sample_appliances.json', 
                readings_file='sample_readings.json'):
    """Save the generated dataset to JSON files"""
    
    # Save appliances metadata
    with open(appliances_file, 'w') as f:
        json.dump(appliances, f, indent=2)
    
    # Save readings (limit to avoid huge files)
    if len(readings) > 10000:
        readings = readings[-10000:]  # Keep last 10k readings
    
    with open(readings_file, 'w') as f:
        json.dump(readings, f, indent=2)
    
    print(f"Dataset saved:")
    print(f"  Appliances: {appliances_file} ({len(appliances)} appliances)")
    print(f"  Readings: {readings_file} ({len(readings)} readings)")

def create_training_data(readings, output_file='training_data.json'):
    """Create a subset of data suitable for training"""
    
    # Group readings by appliance
    appliance_readings = {}
    for reading in readings:
        appliance_id = reading['appliance_id']
        if appliance_id not in appliance_readings:
            appliance_readings[appliance_id] = []
        appliance_readings[appliance_id].append(reading)
    
    # Create balanced training dataset
    training_data = []
    min_readings = min(len(readings) for readings in appliance_readings.values())
    
    for appliance_id, readings_list in appliance_readings.items():
        # Take the most recent readings up to the minimum
        recent_readings = readings_list[-min_readings:]
        training_data.extend(recent_readings)
    
    # Shuffle the data
    random.shuffle(training_data)
    
    # Save training data
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Training data saved: {output_file} ({len(training_data)} samples)")

def main():
    """Generate and save the sample dataset"""
    print("Generating sample appliance health prediction dataset...")
    
    # Generate dataset
    appliances, readings = generate_appliance_dataset(
        num_appliances=8,      # 8 different appliances
        days_of_data=45,       # 45 days of historical data
        readings_per_day=24    # Hourly readings
    )
    
    # Save full dataset
    save_dataset(appliances, readings)
    
    # Create training dataset
    create_training_data(readings)
    
    # Print summary
    print("\nDataset Summary:")
    print(f"Total appliances: {len(appliances)}")
    print(f"Total readings: {len(readings)}")
    print(f"Date range: {(datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    
    # Count anomalies
    anomalies = sum(1 for r in readings if r['is_anomaly'])
    print(f"Total anomalies: {anomalies} ({anomalies/len(readings)*100:.1f}%)")
    
    # Appliance breakdown
    appliance_counts = {}
    for reading in readings:
        category = next(a['category'] for a in appliances if a['appliance_id'] == reading['appliance_id'])
        appliance_counts[category] = appliance_counts.get(category, 0) + 1
    
    print("\nReadings per appliance type:")
    for category, count in appliance_counts.items():
        print(f"  {category}: {count} readings")

if __name__ == "__main__":
    main()
