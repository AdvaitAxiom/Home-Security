#!/usr/bin/env python3
"""
Flask server for the Smart Home Anomaly Detection System

This server fetches sensor data from ThingSpeak, processes it using the AI model,
provides API endpoints to return system status and analyzed sensor data,
and serves a web dashboard for visualization and interaction.
"""

import os
import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import joblib
import sys
import threading
import logging

# Add the parent directory to sys.path to import from model directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration and utilities
from config import (
    THINGSPEAK_CHANNEL_ID, THINGSPEAK_READ_API_KEY,
    SERVER_HOST, SERVER_PORT, DEBUG_MODE,
    MODEL_PATH, CACHE_DURATION
)
from utils import format_timestamp, log_event, determine_risk_level

# Import model prediction functions
try:
    from model.predict import load_model, predict_with_confidence, predict_sound_type, get_risk_level
    model_available = True
except ImportError:
    print("Warning: Model module not found or could not be imported.")
    model_available = False

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'server.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)

# Global variables
latest_data = None
last_fetch_time = 0
model = None

# Load the model if available
if model_available:
    try:
        model = load_model(MODEL_PATH)
        if model is None:
            logger.warning(f"Failed to load model from {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = None
else:
    logger.warning("Model module not available, running in data-only mode")

def fetch_thingspeak_data():
    """
    Fetch the latest data from ThingSpeak
    
    Returns:
        dict: Latest sensor data or None if fetch fails
    """
    global latest_data, last_fetch_time
    
    # Check if we need to fetch new data (cache duration expired)
    current_time = time.time()
    if current_time - last_fetch_time < CACHE_DURATION and latest_data is not None:
        return latest_data
    
    try:
        # Construct ThingSpeak API URL
        url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
        params = {
            "api_key": THINGSPEAK_READ_API_KEY,
            "results": 1  # Get only the latest entry
        }
        
        # Make the request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the response
        data = response.json()
        
        if 'feeds' in data and len(data['feeds']) > 0:
            # Extract the latest feed
            feed = data['feeds'][0]
            
            # Update global variables
            latest_data = {
                'timestamp': feed.get('created_at'),
                'sound_amplitude': float(feed.get('field1', 0)),
                'pattern_id': int(float(feed.get('field4', 0))),
                'flame_detected': int(float(feed.get('field2', 0))) == 1,
                'motion_detected': int(float(feed.get('field3', 0))) == 1
            }
            last_fetch_time = current_time
            
            logger.info(f"Data fetched from ThingSpeak: {latest_data}")
            return latest_data
        else:
            logger.warning("No data found in ThingSpeak response")
            return None
    except Exception as e:
        logger.error(f"Error fetching data from ThingSpeak: {e}")
        return None

def analyze_data(data):
    """
    Analyze sensor data using the AI model
    
    Args:
        data (dict): Sensor data to analyze
        
    Returns:
        dict: Analysis results
    """
    if data is None:
        return {
            'sound_type': 'unknown',
            'risk_level': 'unknown',
            'confidence': 0.0
        }
    
    # Extract features
    sound_amplitude = data.get('sound_amplitude', 0)
    pattern_id = data.get('pattern_id', 0)
    flame_detected = data.get('flame_detected', False)
    motion_detected = data.get('motion_detected', False)
    
    # If model is available, use it to predict sound type
    if model is not None:
        import numpy as np
        features = np.array([[sound_amplitude, pattern_id]])
        sound_type, confidence_scores = predict_with_confidence(model, features)
        confidence = confidence_scores.get(sound_type, 0.0)
    else:
        # Fallback to rule-based classification if model is not available
        if sound_amplitude < 500:
            sound_type = 'normal'
            confidence = 0.8
        elif sound_amplitude >= 800:
            sound_type = 'human_scream' if pattern_id >= 7 else 'glass_break'
            confidence = 0.7
        elif sound_amplitude >= 600:
            sound_type = 'dog_bark' if pattern_id >= 9 else 'fire_crackle'
            confidence = 0.6
        else:
            sound_type = 'normal'
            confidence = 0.5
    
    # Determine risk level
    risk_level = determine_risk_level(sound_type, flame_detected, motion_detected)
    
    return {
        'sound_type': sound_type,
        'risk_level': risk_level,
        'confidence': float(confidence)
    }

@app.route('/')
def home():
    """
    Home endpoint that serves the dashboard
    """
    return render_template('dashboard.html')

@app.route('/api')
def api_info():
    """
    API info endpoint that returns basic information about the API
    """
    return jsonify({
        'name': 'Smart Home Anomaly Detection System API',
        'version': '1.0',
        'endpoints': [
            '/status',
            '/analyze',
            '/simulate'
        ]
    })

@app.route('/status')
def status():
    """
    Status endpoint that returns the current system status
    """
    # Fetch the latest data
    data = fetch_thingspeak_data()
    
    # Get the last analysis if data is available
    last_analysis = None
    if data is not None:
        last_analysis = analyze_data(data)
    
    return jsonify({
        'server_status': 'online',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'thingspeak_channel': THINGSPEAK_CHANNEL_ID,
        'last_data_fetch': format_timestamp(datetime.fromtimestamp(last_fetch_time).isoformat()) if last_fetch_time > 0 else None,
        'last_data': {
            'amplitude': data.get('sound_amplitude') if data else None,
            'pattern_id': data.get('pattern_id') if data else None,
            'flame_detected': data.get('flame_detected') if data else None,
            'motion_detected': data.get('motion_detected') if data else None
        } if data else None,
        'last_analysis': last_analysis
    })

def get_recommendations(sound_type, risk_level, flame_detected, motion_detected):
    """
    Generate recommendations based on the analysis results from ThingSpeak data
    
    Args:
        sound_type (str): The type of sound detected
        risk_level (str): The risk level determined
        flame_detected (bool): Whether flame was detected
        motion_detected (bool): Whether motion was detected
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    # Get the latest ThingSpeak data to ensure recommendations are based on current data
    thingspeak_data = fetch_thingspeak_data()
    if thingspeak_data is None:
        # Fallback if ThingSpeak data is not available
        recommendations.append("Unable to fetch ThingSpeak data. Recommendations may not be accurate.")
    else:
        # Extract data from ThingSpeak
        ts_pattern_id = thingspeak_data.get('pattern_id', 0)
        ts_sound_amplitude = thingspeak_data.get('sound_amplitude', 0)
        ts_flame_detected = thingspeak_data.get('flame_detected', False)
        ts_motion_detected = thingspeak_data.get('motion_detected', False)
        
        # Base recommendations on risk level
        if risk_level == 'high':
            recommendations.append("⚠️ HIGH RISK situation detected in ThingSpeak data! Immediate attention required.")
            
            # Specific recommendations based on sound type and pattern ID
            if sound_type == 'glass_break' or (ts_pattern_id >= 3 and ts_pattern_id <= 4):
                recommendations.append("🔍 Possible break-in detected. Check windows and doors immediately.")
                recommendations.append("📱 Consider contacting security or authorities.")
                if ts_motion_detected:
                    recommendations.append("👤 Motion detected with glass break sound - potential intruder in the house!")
            
            elif sound_type == 'fire_crackle' or (ts_pattern_id >= 5 and ts_pattern_id <= 6):
                recommendations.append("🔥 Possible fire detected. Check for signs of fire immediately.")
                recommendations.append("🚪 Prepare for evacuation if necessary.")
                if ts_flame_detected:
                    recommendations.append("🚨 CRITICAL: Both flame sensor and fire sounds detected - fire confirmed!")
            
            elif sound_type == 'human_scream' or (ts_pattern_id >= 7 and ts_pattern_id <= 8):
                recommendations.append("🆘 Distress call detected. Check for people in need of help.")
                recommendations.append("🚑 Consider contacting emergency services.")
                if ts_motion_detected:
                    recommendations.append("⚡ Motion detected with screams - someone may be in danger!")
        
        elif risk_level == 'medium':
            recommendations.append("⚠️ Medium risk situation detected in ThingSpeak data. Attention recommended.")
            
            if sound_type == 'dog_bark' or (ts_pattern_id >= 9 and ts_pattern_id <= 10):
                recommendations.append("🐕 Unusual dog barking detected. Check for disturbances.")
                if ts_motion_detected:
                    recommendations.append("👀 Motion detected with dog barking - someone may be near your property.")
        
        elif risk_level == 'low':
            recommendations.append("✅ Low risk situation. Normal conditions detected in ThingSpeak data.")
            if ts_sound_amplitude > 700:
                recommendations.append("🔊 Sound levels are higher than normal. May be worth checking.")
        
        # Additional recommendations based on ThingSpeak sensor data
        if ts_flame_detected and not (sound_type == 'fire_crackle' or (ts_pattern_id >= 5 and ts_pattern_id <= 6)):
            recommendations.append("🔥 ALERT: Flame detected in ThingSpeak data! Check for fire immediately.")
            recommendations.append("🧯 Verify if fire detection system is functioning properly.")
        
        if ts_motion_detected and not (risk_level == 'high' or risk_level == 'medium'):
            recommendations.append("🚶 Motion detected in ThingSpeak data. Normal activity detected.")
            if ts_sound_amplitude < 400:
                recommendations.append("🤫 Quiet movement detected - could be normal household activity.")
    
    return recommendations

@app.route('/analyze')
def analyze():
    """
    API endpoint to analyze the latest sensor data
    
    Returns:
        JSON: Analysis results
    """
    # Fetch the latest data from ThingSpeak
    data = fetch_thingspeak_data()
    
    # If no data is available, try to use sample data
    if data is None:
        try:
            # Look for sample data in the samples directory
            samples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'samples')
            sample_file = os.path.join(samples_dir, 'thingspeak_data.json')
            
            if os.path.exists(sample_file):
                with open(sample_file, 'r') as f:
                    sample_data = json.load(f)
                
                if 'feeds' in sample_data and len(sample_data['feeds']) > 0:
                    # Use the first sample as data
                    feed = sample_data['feeds'][0]
                    data = {
                        'timestamp': feed.get('created_at'),
                        'sound_amplitude': float(feed.get('field1', 0)),
                        'pattern_id': int(float(feed.get('field4', 0))),
                        'flame_detected': int(float(feed.get('field2', 0))) == 1,
                        'motion_detected': int(float(feed.get('field3', 0))) == 1
                    }
                    logger.info(f"Using sample data: {data}")
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
    
    # If still no data, return an error
    if data is None:
        return jsonify({
            'error': 'No data available',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    # Analyze the data
    analysis = analyze_data(data)
    
    # Prepare the response
    response = {
        'timestamp': data.get('timestamp'),
        'sensor_data': {
            'amplitude': data.get('sound_amplitude'),
            'pattern_id': data.get('pattern_id'),
            'flame_detected': data.get('flame_detected'),
            'motion_detected': data.get('motion_detected')
        },
        'analysis': analysis
    }
    
    # Add recommendations based on risk level
    recommendations = get_recommendations(analysis['sound_type'], analysis['risk_level'], 
                                         data.get('flame_detected'), 
                                         data.get('motion_detected'))
    response['analysis']['recommendations'] = recommendations
    
    # Log the event
    log_event(response)
    
    return jsonify(response)

@app.route('/simulate', methods=['POST'])
def simulate():
    """
    API endpoint to simulate sensor data for testing
    
    Returns:
        JSON: Analysis results for the simulated data
    """
    try:
        # Get data from request
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract sensor data from the request
        sensor_data_req = data.get('sensor_data', {})
        
        if not sensor_data_req:
            return jsonify({'error': 'No sensor data provided'}), 400
        
        # Prepare data for analysis
        sensor_data = {
            'timestamp': datetime.now().isoformat(),
            'sound_amplitude': float(sensor_data_req.get('amplitude', 0)),
            'pattern_id': int(sensor_data_req.get('pattern_id', 0)),
            'flame_detected': bool(sensor_data_req.get('flame_detected', False)),
            'motion_detected': bool(sensor_data_req.get('motion_detected', False))
        }
        
        # Analyze the data
        analysis = analyze_data(sensor_data)
        
        # Prepare the response
        response = {
            'timestamp': sensor_data.get('timestamp'),
            'sensor_data': {
                'amplitude': sensor_data.get('sound_amplitude'),
                'pattern_id': sensor_data.get('pattern_id'),
                'flame_detected': sensor_data.get('flame_detected'),
                'motion_detected': sensor_data.get('motion_detected')
            },
            'analysis': analysis
        }
        
        # Add recommendations based on risk level
        recommendations = get_recommendations(analysis['sound_type'], analysis['risk_level'], 
                                             sensor_data.get('flame_detected'), 
                                             sensor_data.get('motion_detected'))
        response['analysis']['recommendations'] = recommendations
        
        # Log the event
        log_event(response)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing simulation request: {e}")
        return jsonify({'error': str(e)}), 500

# Background thread to periodically fetch data
def background_fetch():
    """
    Background thread to periodically fetch data from ThingSpeak
    """
    while True:
        try:
            fetch_thingspeak_data()
        except Exception as e:
            logger.error(f"Error in background fetch: {e}")
        
        # Sleep for the cache duration
        time.sleep(CACHE_DURATION)

# Start the background fetch thread when the app starts
@app.before_first_request
def start_background_thread():
    """
    Start the background fetch thread before the first request
    """
    thread = threading.Thread(target=background_fetch)
    thread.daemon = True  # Thread will exit when the main thread exits
    thread.start()
    logger.info("Background fetch thread started")

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)
    
    # Start the server
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)