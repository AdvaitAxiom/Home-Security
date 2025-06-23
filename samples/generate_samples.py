#!/usr/bin/env python3
"""
Sample data generator for the Smart Home Anomaly Detection System

This script generates sample data files that simulate real-time sensor data
for different sound types, flame detection, and motion detection scenarios.
"""

import numpy as np
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta

# Sound type definitions
SOUND_TYPES = {
    'normal': {'amplitude_range': (300, 500), 'pattern_id_range': (0, 3)},
    'glass_break': {'amplitude_range': (700, 900), 'pattern_id_range': (3, 5)},
    'fire_crackle': {'amplitude_range': (500, 700), 'pattern_id_range': (5, 7)},
    'human_scream': {'amplitude_range': (800, 900), 'pattern_id_range': (7, 9)},
    'dog_bark': {'amplitude_range': (600, 800), 'pattern_id_range': (9, 11)}
}

def generate_thingspeak_data(num_entries=100, output_file=None):
    """
    Generate sample ThingSpeak data for testing
    
    Args:
        num_entries (int): Number of data entries to generate
        output_file (str, optional): Path to save the JSON file
        
    Returns:
        dict: Generated ThingSpeak data
    """
    # Initialize data structure
    data = {
        "channel": {
            "id": 0000000,
            "name": "Smart Home Anomaly Detection",
            "description": "Sensor data for anomaly detection",
            "latitude": "0.0",
            "longitude": "0.0",
            "field1": "Sound Amplitude",
            "field2": "Pattern ID",
            "field3": "Flame Detected",
            "field4": "Motion Detected",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "last_entry_id": num_entries
        },
        "feeds": []
    }
    
    # Generate random entries
    base_time = datetime.now() - timedelta(hours=num_entries)
    
    for i in range(1, num_entries + 1):
        # Randomly select a sound type (weighted towards normal)
        sound_type = random.choices(
            list(SOUND_TYPES.keys()),
            weights=[0.7, 0.075, 0.075, 0.075, 0.075],
            k=1
        )[0]
        
        # Get amplitude and pattern ID ranges for the sound type
        amplitude_range = SOUND_TYPES[sound_type]['amplitude_range']
        pattern_id_range = SOUND_TYPES[sound_type]['pattern_id_range']
        
        # Generate random values
        amplitude = random.uniform(*amplitude_range)
        pattern_id = random.randint(*pattern_id_range)
        
        # Determine flame and motion detection
        # Higher chance of flame detection for fire_crackle
        flame_detected = 1 if (sound_type == 'fire_crackle' and random.random() < 0.7) or random.random() < 0.05 else 0
        
        # Higher chance of motion detection for human_scream, glass_break, and dog_bark
        motion_detected = 1 if sound_type in ['human_scream', 'glass_break', 'dog_bark'] and random.random() < 0.8 else (
            1 if random.random() < 0.2 else 0
        )
        
        # Create entry timestamp
        entry_time = base_time + timedelta(minutes=i*10)
        entry_time_str = entry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Create feed entry
        feed = {
            "created_at": entry_time_str,
            "entry_id": i,
            "field1": str(round(amplitude, 2)),
            "field2": str(pattern_id),
            "field3": str(flame_detected),
            "field4": str(motion_detected)
        }
        
        data["feeds"].append(feed)
    
    # Save to file if output_file is provided
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"ThingSpeak data saved to {output_file}")
    
    return data

def generate_csv_samples(output_dir=None):
    """
    Generate CSV sample files for each sound type
    
    Args:
        output_dir (str, optional): Directory to save the CSV files
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate samples for each sound type
    for sound_type, ranges in SOUND_TYPES.items():
        # Generate 20 samples for each sound type
        samples = []
        for _ in range(20):
            amplitude = round(random.uniform(*ranges['amplitude_range']), 2)
            pattern_id = random.randint(*ranges['pattern_id_range'])
            
            # Determine flame and motion detection based on sound type
            flame_detected = 1 if sound_type == 'fire_crackle' and random.random() < 0.7 else 0
            motion_detected = 1 if sound_type in ['human_scream', 'glass_break', 'dog_bark'] and random.random() < 0.8 else 0
            
            # Create timestamp
            timestamp = (datetime.now() - timedelta(minutes=random.randint(0, 1000))).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            samples.append({
                'timestamp': timestamp,
                'amplitude': amplitude,
                'pattern_id': pattern_id,
                'flame_detected': flame_detected,
                'motion_detected': motion_detected,
                'sound_type': sound_type
            })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(samples)
        output_file = os.path.join(output_dir, f"{sound_type}_samples.csv")
        df.to_csv(output_file, index=False)
        print(f"Generated {output_file}")

def generate_api_response_samples(output_dir=None):
    """
    Generate sample API response JSON files
    
    Args:
        output_dir (str, optional): Directory to save the JSON files
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_responses')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate sample responses for each sound type
    for sound_type in SOUND_TYPES.keys():
        # Determine risk level based on sound type
        if sound_type in ['glass_break', 'human_scream']:
            risk_level = 'high'
        elif sound_type in ['fire_crackle', 'dog_bark']:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Create sample response
        response = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sensor_data": {
                "sound_amplitude": round(random.uniform(*SOUND_TYPES[sound_type]['amplitude_range']), 2),
                "flame_detected": 1 if sound_type == 'fire_crackle' and random.random() < 0.7 else 0,
                "motion_detected": 1 if sound_type in ['human_scream', 'glass_break', 'dog_bark'] and random.random() < 0.8 else 0
            },
            "analysis": {
                "sound_type": sound_type,
                "risk_level": risk_level,
                "confidence": round(random.uniform(0.7, 0.99), 2)
            },
            "recommendations": get_recommendations(sound_type, risk_level)
        }
        
        # Save to file
        output_file = os.path.join(output_dir, f"{sound_type}_response.json")
        with open(output_file, 'w') as f:
            json.dump(response, f, indent=2)
        print(f"Generated {output_file}")

def get_recommendations(sound_type, risk_level):
    """
    Get recommendations based on sound type and risk level
    
    Args:
        sound_type (str): The type of sound
        risk_level (str): The risk level
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    if risk_level == 'high':
        recommendations.append("Alert authorities immediately")
        
        if sound_type == 'glass_break':
            recommendations.append("Possible break-in detected")
            recommendations.append("Activate security system")
        
        elif sound_type == 'human_scream':
            recommendations.append("Possible emergency situation")
            recommendations.append("Check on household members")
        
        elif sound_type == 'fire_crackle':
            recommendations.append("Possible fire detected")
            recommendations.append("Evacuate premises if confirmed")
    
    elif risk_level == 'medium':
        recommendations.append("Monitor situation closely")
        
        if sound_type == 'dog_bark':
            recommendations.append("Check for unusual activity")
        
        elif sound_type == 'fire_crackle':
            recommendations.append("Investigate potential fire hazards")
    
    else:  # low risk
        recommendations.append("No immediate action required")
        recommendations.append("Continue normal monitoring")
    
    return recommendations

# If this file is run directly, generate all sample files
if __name__ == '__main__':
    # Create samples directory if it doesn't exist
    samples_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(samples_dir, exist_ok=True)
    
    # Generate ThingSpeak data
    generate_thingspeak_data(num_entries=100, output_file=os.path.join(samples_dir, 'thingspeak_data.json'))
    
    # Generate CSV samples
    generate_csv_samples(samples_dir)
    
    # Generate API response samples
    generate_api_response_samples(os.path.join(samples_dir, 'api_responses'))
    
    print("Sample data generation complete!")