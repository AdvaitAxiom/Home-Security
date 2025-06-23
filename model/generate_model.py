#!/usr/bin/env python3
"""
Model generator for the Smart Home Anomaly Detection System

This script generates a pre-trained model for sound classification
and saves it to disk for use by the Flask server.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Add the parent directory to sys.path to import from model directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Sound type mapping
SOUND_TYPES = {
    'normal': 0,
    'glass_break': 1,
    'fire_crackle': 2,
    'human_scream': 3,
    'dog_bark': 4
}

def generate_synthetic_data(n_samples=1000, random_state=42):
    """
    Generate synthetic data for training the model
    
    Args:
        n_samples (int): Number of samples to generate
        random_state (int): Random seed for reproducibility
        
    Returns:
        tuple: (X, y) where X is the feature matrix and y is the target vector
    """
    np.random.seed(random_state)
    
    # Initialize empty arrays
    X = np.zeros((n_samples, 2))  # Features: amplitude, pattern_id
    y = np.zeros(n_samples, dtype=int)  # Target: sound type
    
    # Generate data for each sound type
    samples_per_class = n_samples // len(SOUND_TYPES)
    
    for i, (sound_type, class_id) in enumerate(SOUND_TYPES.items()):
        start_idx = i * samples_per_class
        end_idx = (i + 1) * samples_per_class if i < len(SOUND_TYPES) - 1 else n_samples
        
        # Generate features based on sound type
        if sound_type == 'normal':
            # Normal sounds have lower amplitude and consistent patterns
            X[start_idx:end_idx, 0] = np.random.uniform(300, 500, end_idx - start_idx)  # Amplitude
            X[start_idx:end_idx, 1] = np.random.randint(0, 3, end_idx - start_idx)  # Pattern ID
        
        elif sound_type == 'glass_break':
            # Glass breaks have high amplitude spikes
            X[start_idx:end_idx, 0] = np.random.uniform(700, 900, end_idx - start_idx)  # Amplitude
            X[start_idx:end_idx, 1] = np.random.randint(3, 5, end_idx - start_idx)  # Pattern ID
        
        elif sound_type == 'fire_crackle':
            # Fire crackles have medium amplitude with variations
            X[start_idx:end_idx, 0] = np.random.uniform(500, 700, end_idx - start_idx)  # Amplitude
            X[start_idx:end_idx, 1] = np.random.randint(5, 7, end_idx - start_idx)  # Pattern ID
        
        elif sound_type == 'human_scream':
            # Human screams have very high amplitude
            X[start_idx:end_idx, 0] = np.random.uniform(800, 900, end_idx - start_idx)  # Amplitude
            X[start_idx:end_idx, 1] = np.random.randint(7, 9, end_idx - start_idx)  # Pattern ID
        
        elif sound_type == 'dog_bark':
            # Dog barks have medium-high amplitude
            X[start_idx:end_idx, 0] = np.random.uniform(600, 800, end_idx - start_idx)  # Amplitude
            X[start_idx:end_idx, 1] = np.random.randint(9, 11, end_idx - start_idx)  # Pattern ID
        
        # Set the target class
        y[start_idx:end_idx] = class_id
    
    return X, y

def create_and_save_model():
    """
    Create and save a pre-trained model for sound classification
    """
    # Generate synthetic data
    X, y = generate_synthetic_data(n_samples=1000)
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Create and train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # Create a dictionary with the model and scaler
    model_dict = {
        'model': model,
        'scaler': scaler,
        'feature_names': ['amplitude', 'pattern_id'],
        'class_mapping': {v: k for k, v in SOUND_TYPES.items()}
    }
    
    # Save the model dictionary
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound_classifier.pkl')
    joblib.dump(model_dict, model_path)
    print(f"Model saved to {model_path}")
    
    return model_dict

if __name__ == '__main__':
    # Create and save the model
    model_dict = create_and_save_model()
    print("Pre-trained model generated successfully!")