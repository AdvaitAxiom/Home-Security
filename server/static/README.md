# Smart Home Anomaly Detection System Dashboard

## Overview

This directory contains the static assets for the Smart Home Anomaly Detection System dashboard, a web-based interface for monitoring and interacting with the system.

## Directory Structure

- `css/`: Contains the CSS stylesheets for the dashboard
  - `styles.css`: Main stylesheet for the dashboard

- `js/`: Contains the JavaScript files for the dashboard
  - `dashboard.js`: Main JavaScript file for the dashboard functionality

## Features

The dashboard provides the following features:

1. **Real-time System Status**: View the current status of the system, including server status, AI model status, and last update time.

2. **Current Sensor Readings**: Display the current sensor readings, including sound amplitude, pattern ID, flame detection, and motion detection.

3. **Sound Classification**: View the current sound type classification and risk level.

4. **Recommendations**: Get real-time recommendations based on the detected sound type and risk level.

5. **Data Visualization**: View charts showing sound amplitude over time and risk level distribution.

6. **Event Log**: View a log of recent events, including timestamps, sound types, and risk levels.

7. **Simulation**: Simulate sensor data to test the system's response to different scenarios.

## Usage

The dashboard is automatically served by the Flask server when you access the root URL (`/`). No additional setup is required.

## Dependencies

- [Chart.js](https://www.chartjs.org/): Used for data visualization
- [Google Fonts (Roboto)](https://fonts.google.com/specimen/Roboto): Used for typography

## Browser Compatibility

The dashboard is compatible with modern browsers, including:

- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari

## Customization

To customize the dashboard:

1. Modify `styles.css` to change the appearance
2. Modify `dashboard.js` to change the functionality
3. Modify `dashboard.html` to change the structure