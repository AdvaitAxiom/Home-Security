# Smart Home Anomaly Detection System Templates

## Overview

This directory contains the HTML templates for the Smart Home Anomaly Detection System web interface. These templates are rendered by the Flask server to provide a user-friendly interface for monitoring and interacting with the system.

## Files

- `dashboard.html`: The main dashboard template for the Smart Home Anomaly Detection System.

## Dashboard Template

The `dashboard.html` template provides a comprehensive interface for monitoring the Smart Home Anomaly Detection System. It includes:

1. **Header**: Displays the system title and status information.

2. **Status Panel**: Shows the current system status, including server status, AI model status, and last update time.

3. **Sensor Data Panel**: Displays the current sensor readings and analysis results.

4. **Charts Panel**: Visualizes sensor data and risk levels over time using Chart.js.

5. **Event Log Panel**: Shows a log of recent events, including timestamps, sound types, and risk levels.

6. **Simulation Panel**: Allows users to simulate sensor data to test the system's response to different scenarios.

## Usage

The templates are automatically used by the Flask server when rendering the web interface. No additional setup is required.

## Customization

To customize the templates:

1. Modify the HTML structure to change the layout
2. Update the CSS classes to change the styling
3. Add or remove elements to change the functionality

## Dependencies

The templates depend on:

- CSS files in the `static/css` directory
- JavaScript files in the `static/js` directory
- [Chart.js](https://www.chartjs.org/) for data visualization
- [Google Fonts (Roboto)](https://fonts.google.com/specimen/Roboto) for typography