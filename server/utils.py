#!/usr/bin/env python3
"""
Utility functions for the Smart Home Anomaly Detection System

This file contains helper functions used by the Flask server for data processing,
formatting, and other utility tasks.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
import os

# Import configuration
from config import RISK_LEVELS, SOUND_TYPES

def format_timestamp(timestamp_str):
    """
    Convert a timestamp string to a formatted datetime string
    
    Args:
        timestamp_str (str): Timestamp string in ISO format
        
    Returns:
        str: Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return timestamp_str

def prepare_features(sound_amplitude, additional_features=None):
    """
    Prepare features for model prediction
    
    Args:
        sound_amplitude (int): Sound amplitude value
        additional_features (dict, optional): Additional features to include
        
    Returns:
        numpy.ndarray: Feature array for model prediction
    """
    # Start with the sound amplitude as the base feature
    features = [sound_amplitude]
    
    # Add any additional features if provided
    if additional_features:
        for feature in additional_features.values():
            features.append(feature)
    
    # Return as numpy array with shape (1, n_features)
    return np.array([features])

def get_sound_description(sound_type):
    """
    Get a description for a sound type
    
    Args:
        sound_type (str): The type of sound
        
    Returns:
        str: Description of the sound type
    """
    return SOUND_TYPES.get(sound_type, "Unknown sound type")

def determine_risk_level(sound_type, flame_detected=False, motion_detected=False):
    """
    Determine the risk level based on sound type and other sensor data
    
    Args:
        sound_type (str): The type of sound
        flame_detected (bool): Whether flame was detected
        motion_detected (bool): Whether motion was detected
        
    Returns:
        str: Risk level ('high', 'medium', or 'low')
    """
    # If flame is detected, always high risk
    if flame_detected:
        return "high"
    
    # Determine base risk level from sound type
    base_risk = "low"  # Default risk level
    for level, sound_types in RISK_LEVELS.items():
        if sound_type in sound_types:
            base_risk = level
            break
    
    # Adjust risk based on motion detection
    if motion_detected and base_risk == "low":
        return "medium"  # Upgrade low to medium if motion is detected
    
    return base_risk

def log_event(event_data):
    """
    Log an event to a JSON file
    
    Args:
        event_data (dict): Event data to log
    """
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"events_{datetime.now().strftime('%Y%m%d')}.json")
    
    # Add timestamp to event data
    event_data['logged_at'] = datetime.now().isoformat()
    
    # Read existing logs if file exists
    existing_logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                existing_logs = json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, start with empty list
            existing_logs = []
    
    # Append new event
    existing_logs.append(event_data)
    
    # Write back to file
    with open(log_file, 'w') as f:
        json.dump(existing_logs, f, indent=2)