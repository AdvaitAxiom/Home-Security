#!/usr/bin/env python3
"""
Training script for the Smart Home Anomaly Detection System

This script trains a machine learning model to classify sound types based on
features extracted from sound data. It saves the trained model to disk for
later use in the prediction module.
"""

import numpy as np
import pandas as pd
import joblib
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

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

def train_model(X, y, model_path=None):
    """
    Train a machine learning model and save it to disk
    
    Args:
        X (numpy.ndarray): Feature matrix
        y (numpy.ndarray): Target vector
        model_path (str, optional): Path to save the model
        
    Returns:
        object: Trained model object
    """
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Create and train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save the model and scaler
    if model_path is None:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound_classifier.pkl')
    
    # Create a dictionary with the model and scaler
    model_dict = {
        'model': model,
        'scaler': scaler,
        'feature_names': ['amplitude', 'pattern_id'],
        'class_mapping': {v: k for k, v in SOUND_TYPES.items()}
    }
    
    # Save the model dictionary
    joblib.dump(model_dict, model_path)
    print(f"Model saved to {model_path}")
    
    return model_dict

def save_sample_data(X, y, output_dir=None):
    """
    Save sample data to CSV files for reference
    
    Args:
        X (numpy.ndarray): Feature matrix
        y (numpy.ndarray): Target vector
        output_dir (str, optional): Directory to save the files
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'samples')
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a DataFrame with the data
    df = pd.DataFrame(X, columns=['amplitude', 'pattern_id'])
    df['sound_type'] = [list(SOUND_TYPES.keys())[list(SOUND_TYPES.values()).index(label)] for label in y]
    
    # Save the full dataset
    df.to_csv(os.path.join(output_dir, 'sound_data.csv'), index=False)
    
    # Save samples for each sound type
    for sound_type in SOUND_TYPES.keys():
        df_type = df[df['sound_type'] == sound_type].sample(min(10, len(df[df['sound_type'] == sound_type])))
        df_type.to_csv(os.path.join(output_dir, f'{sound_type}_samples.csv'), index=False)
    
    print(f"Sample data saved to {output_dir}")

# If this file is run directly, train the model
if __name__ == '__main__':
    # Generate synthetic data
    X, y = generate_synthetic_data(n_samples=1000)
    
    # Train and save the model
    model_dict = train_model(X, y)
    
    # Save sample data
    save_sample_data(X, y)
    
    print("Model training complete!")