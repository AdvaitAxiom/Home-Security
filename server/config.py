#!/usr/bin/env python3
"""
Configuration settings for the Smart Home Anomaly Detection System

This file contains all the configuration variables used by the Flask server,
including API keys, channel IDs, and other settings.
"""

# ThingSpeak configuration
THINGSPEAK_CHANNEL_ID = "0000000"  # Replace with your ThingSpeak Channel ID
THINGSPEAK_READ_API_KEY = "YOUR_THINGSPEAK_READ_API_KEY"  # Replace with your ThingSpeak Read API Key

# Server configuration
SERVER_HOST = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 5000  # Default port for the Flask server
DEBUG_MODE = True  # Set to False in production

# Model configuration
MODEL_PATH = "../model/sound_classifier.pkl"  # Path to the trained model file

# Cache configuration
CACHE_DURATION = 10  # Duration in seconds to cache ThingSpeak data

# Risk level thresholds
RISK_LEVELS = {
    "high": ["glass_break", "human_scream", "fire_crackle"],
    "medium": ["dog_bark"],
    "low": ["normal"]
}

# Sound type descriptions
SOUND_TYPES = {
    "normal": "Normal background noise",
    "glass_break": "Sound of glass breaking",
    "fire_crackle": "Sound of fire crackling",
    "human_scream": "Human scream or shout",
    "dog_bark": "Dog barking"
}

# Feature names for the model
FEATURE_NAMES = ["amplitude", "pattern_id"]