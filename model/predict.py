#!/usr/bin/env python3
"""
Prediction functions for the Smart Home Anomaly Detection System

This file contains functions for making predictions using the trained model
and determining risk levels based on the predictions and sensor data.
"""

import numpy as np
import joblib
import os
import sys

# Add the parent directory to sys.path to import from server directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Sound type mapping
SOUND_TYPES = {
    0: 'normal',
    1: 'glass_break',
    2: 'fire_crackle',
    3: 'human_scream',
    4: 'dog_bark'
}

def load_model(model_path=None):
    """
    Load the trained model from disk
    
    Args:
        model_path (str, optional): Path to the model file
        
    Returns:
        object: Loaded model object or None if loading fails
    """
    if model_path is None:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound_classifier.pkl')
    
    try:
        model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def predict_sound_type(model, features):
    """
    Predict the sound type using the trained model
    
    Args:
        model: Trained model object
        features (numpy.ndarray): Feature array for prediction
        
    Returns:
        str: Predicted sound type
    """
    try:
        # Make prediction
        prediction = model.predict(features)
        
        # Get the predicted class
        predicted_class = prediction[0]
        
        # Map class to sound type
        sound_type = SOUND_TYPES.get(predicted_class, 'unknown')
        
        return sound_type
    except Exception as e:
        print(f"Error making prediction: {e}")
        return 'unknown'

def get_risk_level(sound_type, flame_detected=False, motion_detected=False):
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
        return 'high'
    
    # Determine risk level based on sound type
    if sound_type in ['glass_break', 'human_scream']:
        return 'high'
    elif sound_type in ['fire_crackle', 'dog_bark']:
        return 'medium'
    elif sound_type == 'normal':
        # If motion is detected with normal sound, medium risk
        return 'medium' if motion_detected else 'low'
    else:
        # Unknown sound type with motion is medium risk, otherwise low
        return 'medium' if motion_detected else 'low'

def predict_with_confidence(model, features):
    """
    Predict the sound type with confidence scores
    
    Args:
        model: Trained model object
        features (numpy.ndarray): Feature array for prediction
        
    Returns:
        tuple: (predicted_sound_type, confidence_scores)
    """
    try:
        # Check if model has predict_proba method (for probability estimates)
        if hasattr(model, 'predict_proba'):
            # Get probability estimates for each class
            proba = model.predict_proba(features)[0]
            
            # Get the predicted class and its probability
            predicted_class = np.argmax(proba)
            confidence = proba[predicted_class]
            
            # Map class to sound type
            sound_type = SOUND_TYPES.get(predicted_class, 'unknown')
            
            # Create confidence scores for all classes
            confidence_scores = {SOUND_TYPES.get(i, f'class_{i}'): float(p) 
                               for i, p in enumerate(proba)}
            
            return sound_type, confidence_scores
        else:
            # If model doesn't support probabilities, just return the prediction
            prediction = model.predict(features)[0]
            sound_type = SOUND_TYPES.get(prediction, 'unknown')
            
            # Create a simple confidence score (1.0 for predicted class)
            confidence_scores = {sound_type: 1.0}
            
            return sound_type, confidence_scores
    except Exception as e:
        print(f"Error making prediction with confidence: {e}")
        return 'unknown', {'unknown': 1.0}

# If this file is run directly, test the functions
if __name__ == '__main__':
    # Test loading the model
    model = load_model()
    
    if model is not None:
        # Test making predictions
        test_features = np.array([[500, 2]])  # Example features
        
        # Test basic prediction
        sound_type = predict_sound_type(model, test_features)
        print(f"Predicted sound type: {sound_type}")
        
        # Test prediction with confidence
        sound_type, confidence = predict_with_confidence(model, test_features)
        print(f"Predicted sound type with confidence: {sound_type}")
        print(f"Confidence scores: {confidence}")
        
        # Test risk level determination
        risk_level = get_risk_level(sound_type)
        print(f"Risk level: {risk_level}")