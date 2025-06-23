# Smart Home Anomaly Detection System with AI-Powered Sound Source Classification

## Overview

This project implements a smart home security system that uses AI to detect and classify anomalous sounds in a home environment. The system integrates hardware sensors (simulated in Wokwi), cloud data storage (ThingSpeak), and a machine learning model to identify potential security threats based on sound patterns. It provides real-time alerts and recommendations based on the detected anomalies through a web dashboard.

## System Architecture

### Components

1. **Hardware Simulation (Wokwi)**
   - ESP32 microcontroller
   - Sound sensor (analog) - detects sound amplitude
   - Flame sensor (digital) - detects presence of fire
   - PIR motion sensor (digital) - detects movement

2. **Cloud Data Platform (ThingSpeak)**
   - Stores sensor data sent from ESP32
   - Provides API for data retrieval

3. **Server Application (Flask)**
   - Fetches data from ThingSpeak
   - Processes sensor data
   - Hosts the AI model
   - Provides API endpoints for system status

4. **AI Model**
   - Classifies sound sources based on amplitude patterns
   - Categories: fire crackle, glass break, human scream, dog bark, normal
   - Assigns risk levels to detected sounds

### Data Flow

```
┌─────────┐     HTTP     ┌────────────┐    API     ┌─────────────┐    ┌─────────┐
│  Wokwi  │───GET────────▶ ThingSpeak │◀───GET─────┤ Flask Server│────▶ AI Model│
│ (ESP32) │              │            │            │             │    └─────┬───┘
└─────────┘              └────────────┘            └─────────────┘          │
                                                          │                 │
                                                          ▼                 │
                                                  ┌───────────────┐         │
                                                  │ JSON Response │◀────────┘
                                                  │ - sound_type  │
                                                  │ - risk_level  │
                                                  └───────────────┘
```

## Setup Instructions

### 1. Automated Setup

#### Windows

```powershell
# Run the setup script
.\setup.ps1
```

#### Linux/macOS

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The setup script will:
- Check for Python installation
- Create a virtual environment
- Install dependencies from requirements.txt
- Generate the pre-trained model
- Create necessary directories

### 1.1. Updating Dependencies

If you encounter dependency-related issues or need to update dependencies after changes to requirements.txt:

#### Windows

```powershell
# Run the update dependencies script
.\update_dependencies.ps1
```

#### Linux/macOS

```bash
# Make the script executable
chmod +x update_dependencies.sh

# Run the update dependencies script
./update_dependencies.sh
```

### 2. ThingSpeak Configuration

1. Create a free account on [ThingSpeak](https://thingspeak.com/)
2. Create a new channel with the following fields:
   - Field 1: Sound Amplitude
   - Field 2: Pattern ID
   - Field 3: Flame Sensor (0/1)
   - Field 4: Motion Sensor (0/1)
3. Note your Channel ID and Read API Key
4. Update the configuration in `server/config.py`:
   ```python
   THINGSPEAK_CHANNEL_ID = "your_channel_id"
   THINGSPEAK_READ_API_KEY = "your_read_api_key"
   ```

### 3. Running the Server

#### Windows

```powershell
# Run the server script
.\run_server.ps1
```

#### Linux/macOS

```bash
# Make the script executable
chmod +x run_server.sh

# Run the server script
./run_server.sh
```

The run script will:
- Check for the virtual environment
- Check for the pre-trained model
- Prompt for server host, port, and debug mode
- Start the Flask server

### 4. Accessing the Dashboard

Once the server is running, open a web browser and navigate to:
```
http://localhost:5000
```
Or use the host and port you specified when running the server.

#### Generating the Model

The model is automatically generated during setup. If you need to regenerate the model manually:

```bash
# Activate the virtual environment first
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Navigate to model directory
cd model

# Run the model generation script
python generate_model.py
```

This will generate a new model using synthetic data and save it as `sound_classifier.pkl` in the model directory.

#### Customizing the Model

To customize the model generation process, you can modify the `generate_model.py` script to:

1. Adjust the feature generation parameters
2. Change the classifier parameters
3. Add new sound types
4. Modify the synthetic data generation logic

## Web Dashboard

The system includes a web-based dashboard for monitoring and interacting with the Smart Home Anomaly Detection System. The dashboard is accessible by navigating to the root URL of the server (e.g., `http://localhost:5000`).

### Dashboard Features

1. **System Status Panel**
   - Server status (online/offline)
   - AI model status (loaded/not loaded)
   - Last data fetch time
   - Last analysis time

2. **Current Sensor Data Panel**
   - Sound amplitude
   - Pattern ID
   - Flame detection status
   - Motion detection status
   - Current sound type classification
   - Risk level assessment
   - Confidence score

3. **Recommendations Panel**
   - Actionable recommendations based on detected anomalies
   - Context-specific advice for different risk levels

4. **Data Visualization**
   - Sound amplitude chart (historical data)
   - Risk level distribution chart

5. **Event Log**
   - Chronological list of detected events
   - Timestamps, sound types, and risk levels
   - Filtering options

6. **Simulation Panel**
   - Test the system with simulated sensor data
   - Adjust amplitude, pattern ID, flame, and motion parameters
   - View analysis results for simulated data

### Dashboard Interaction

- **Refresh Button**: Manually refresh data from the server
- **Simulate Button**: Submit simulated sensor data for analysis
- **Auto-Refresh**: Dashboard automatically updates every 30 seconds

## API Endpoints

### GET /

Serves the web dashboard interface.

### GET /api

Returns information about the available API endpoints.

### GET /status

Returns the current system status, including server status, model loading status, last data fetch time, and current sensor readings.

### GET /analyze

Fetches the latest data from ThingSpeak and returns the analysis.

Response format:
```json
{
  "timestamp": "2023-07-15T14:30:45Z",
  "sound": {
    "amplitude": 750,
    "pattern_id": 2,
    "type": "glass_break",
    "risk_level": "high",
    "confidence": 0.92
  },
  "flame_detected": false,
  "motion_detected": true,
  "recommendations": [
    "Possible security breach detected. Check windows and doors.",
    "Consider contacting security services if you're not home."
  ]
}
```

### POST /simulate

Allows simulation of sensor data for testing the system's response.

Request format:
```json
{
  "sensor_data": {
    "amplitude": 750,
    "pattern_id": 2,
    "flame_detected": false,
    "motion_detected": true
  }
}
```

Response format is the same as the /analyze endpoint.

## Sample Data

The `samples/` directory contains example sound amplitude patterns for different sound types:

- `normal_samples.csv`: Background noise, typical home sounds
- `glass_break_samples.csv`: Glass breaking sound patterns
- `fire_crackle_samples.csv`: Fire crackling sound patterns
- `human_scream_samples.csv`: Human screaming sound patterns
- `dog_bark_samples.csv`: Dog barking sound patterns

These samples are used as fallback data when ThingSpeak data is unavailable and can be used as reference for how different sound patterns are classified. Each sample file contains amplitude and pattern_id values that represent the characteristics of each sound type.

### Sample Data Format

Each sample file follows this format:

```
timestamp,amplitude,pattern_id
2023-07-15T14:30:00Z,120,1
2023-07-15T14:30:01Z,125,1
...
```

The system will use these samples if it cannot connect to ThingSpeak, allowing for testing and demonstration without an active internet connection.

## Project Structure

```
/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Python project metadata (PEP 621)
├── setup.ps1               # Windows setup script
├── setup.sh                # Linux/macOS setup script
├── update_dependencies.ps1 # Windows dependency update script
├── update_dependencies.sh  # Linux/macOS dependency update script
├── run_server.ps1          # Windows server start script
├── run_server.sh           # Linux/macOS server start script
├── test_imports.py         # Script to test dependencies
├── check_system.py         # System diagnostic tool
├── maintenance.py          # System maintenance utility
├── generate_test_data.py   # Test data generator
├── visualize_data.py       # Data visualization tool
├── benchmark.py            # API performance benchmark tool
├── run_tests.py            # Test runner for automated testing
├── .github/                # GitHub configuration
│   └── workflows/          # GitHub Actions workflows
│       └── ci.yml          # Continuous Integration workflow
├── logs/                   # System event logs
│   ├── README.md           # Log documentation
│   └── events.json         # Sample event log
├── model/                  # AI model
│   ├── generate_model.py   # Script to generate the pre-trained model
│   └── sound_classifier.pkl # Pre-trained model (generated)
├── samples/                # Sample data for training
│   ├── fire_crackle_samples.csv
│   ├── glass_break_samples.csv
│   ├── human_scream_samples.csv
│   ├── dog_bark_samples.csv
│   └── normal_samples.csv
└── server/                 # Flask server
    ├── app.py              # Main server application
    ├── config.py           # Configuration settings
    ├── utils.py            # Utility functions
    ├── logs/               # Server-specific logs
    │   └── README.md       # Server log documentation
    ├── static/             # Static assets for web interface
    │   ├── README.md       # Static assets documentation
    │   ├── css/            # CSS stylesheets
    │   │   └── styles.css  # Main stylesheet
    │   └── js/             # JavaScript files
    │       └── dashboard.js # Dashboard functionality
    └── templates/          # HTML templates
        ├── README.md       # Templates documentation
        └── dashboard.html  # Main dashboard template
```

## Troubleshooting

### Common Issues

1. **Model Not Loading**
   - **Symptom**: Server logs show "Failed to load model" or the dashboard shows "Model: Not Loaded"
   - **Solution**: Run the setup script to generate the model, or manually generate it using the instructions in the "Generating the Model" section

2. **ThingSpeak Data Not Available**
   - **Symptom**: Server logs show "Failed to fetch ThingSpeak data" or "Using sample data"
   - **Solution**: 
     - Check your internet connection
     - Verify your ThingSpeak API credentials in `server/config.py`
     - Ensure your ThingSpeak channel is active and has data
     - The system will automatically fall back to sample data

3. **Server Not Starting**
   - **Symptom**: Error messages when running the server script
   - **Solution**:
     - Check if another process is using the same port
     - Verify that the virtual environment is activated
     - Check server logs in `server/logs/server.log` for specific error messages

4. **Dashboard Not Loading**
   - **Symptom**: Browser shows "Cannot connect to server" or blank page
   - **Solution**:
     - Verify the server is running
     - Check that you're using the correct URL (host and port)
     - Clear browser cache or try a different browser

5. **Werkzeug Import Error**
   - **Symptom**: Error message: `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'`
   - **Solution**:
     - Run the update_dependencies script to install the correct version of Werkzeug:
       ```
       # Windows
       .\update_dependencies.ps1
       
       # Linux/macOS
       ./update_dependencies.sh
       ```
     - This error occurs when Flask and Werkzeug versions are incompatible
     - You can verify that the imports are working correctly by running the test script:
       ```
       # Activate virtual environment first
       # Windows
       .\venv\Scripts\activate
       # Linux/macOS
       source venv/bin/activate
       
       # Run the test script
       python test_imports.py
       ```

### System Diagnostics

The project includes a diagnostic tool to check for common issues:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Run the diagnostic tool
python check_system.py
```

This tool checks:
- Python version compatibility
- Virtual environment activation
- Required dependencies
- Flask-Werkzeug compatibility
- Model file existence
- Directory structure
- Sample data files
- Configuration settings

### System Maintenance

The project includes a maintenance utility to help with routine system upkeep:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# View available maintenance options
python maintenance.py

# Examples:
# Clean logs older than 7 days
python maintenance.py --clean-logs --days 7

# Clean Python cache files
python maintenance.py --clean-cache

# Backup important data
python maintenance.py --backup

# Perform all maintenance tasks with dry run (no changes)
python maintenance.py --all --dry-run
```

The maintenance utility can:
- Clean and archive old log files
- Remove Python cache files
- Backup important system data
- Perform dry runs to preview changes

### Test Data Generator

The project includes a utility to generate test data for development and testing:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Generate default test data (100 samples, 70% normal, 30% anomalies)
python generate_test_data.py

# Generate 500 samples with custom distribution
python generate_test_data.py --samples 500 --normal-ratio 0.8 --anomaly1-ratio 0.1 --anomaly2-ratio 0.05 --anomaly3-ratio 0.05

# Generate test data and event logs
python generate_test_data.py --generate-events

# Generate only CSV format
python generate_test_data.py --format csv
```

The test data generator can:
- Create sample data with configurable distributions of normal and anomaly patterns
- Generate both CSV and JSON formatted data
- Create simulated event logs
- Customize output directory and file formats

### Data Visualization

The project includes a data visualization tool to help analyze sensor data and model performance:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# View available visualization options
python visualize_data.py

# Visualize the latest sample data
python visualize_data.py --all

# Visualize a specific data file
python visualize_data.py --input samples/my_data_samples.csv

# Include event log visualization
python visualize_data.py --events

# Generate a summary report
python visualize_data.py --report

# Visualize model information (if available)
python visualize_data.py --model
```

The visualization tool generates the following outputs in the `visualizations` directory:
- Time series plots of sensor data
- Amplitude distribution by pattern type
- Pattern type distribution
- Event timeline (if events are available)
- Feature importance (if model is available)
- Summary reports in JSON and text formats

### API Performance Benchmarking

The project includes a benchmark tool to measure API performance:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# View available benchmark options
python benchmark.py

# Run benchmark with default settings
python benchmark.py --url http://localhost:5000 --requests 100

# Benchmark specific endpoints
python benchmark.py --endpoints /status /analyze

# Include simulation endpoint in benchmark
python benchmark.py --simulate

# Specify output directory
python benchmark.py --output-dir my_benchmark_results
```

The benchmark tool generates the following outputs in the `benchmark_results` directory:
- Response time distribution plots
- Endpoint comparison charts
- Detailed performance reports in JSON and text formats
- Success rates and error counts
- Response time statistics (min, max, average, 95th percentile)

### Automated Testing

The project includes a test runner for automated testing:

```bash
# Activate virtual environment first
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# View available test options
python run_tests.py

# Create sample test files if none exist
python run_tests.py --create-tests

# Run all tests with verbose output
python run_tests.py --verbose

# Run a specific test file
python run_tests.py --test-file tests/test_server.py

# Specify output directory for test results
python run_tests.py --output-dir my_test_results
```

The test runner can:
- Create sample test files for server, model, and utilities
- Run all tests or specific test files
- Generate detailed test reports in JSON and text formats
- Provide success rates and failure details
- Track test execution time

### Continuous Integration

The project includes a GitHub Actions workflow for continuous integration:

- **File**: `.github/workflows/ci.yml`
- **Triggers**: Push to main/master/develop branches, pull requests, manual dispatch

The CI workflow includes the following jobs:

1. **Test**:
   - Runs on multiple Python versions (3.8, 3.9, 3.10)
   - Installs dependencies
   - Creates necessary directories
   - Generates test data
   - Runs tests and uploads results

2. **Lint**:
   - Checks code quality with flake8 and pylint
   - Identifies syntax errors and potential issues

3. **Build**:
   - Runs after successful test and lint jobs
   - Executes setup script
   - Verifies system configuration
   - Creates distribution package

To use this workflow, push your code to a GitHub repository. The CI process will automatically run on each push or pull request to the specified branches.

### Python Packaging

The project uses modern Python packaging with `pyproject.toml` (PEP 621):

```bash
# Install the project in development mode
pip install -e .

# Build distribution packages
pip install build
python -m build

# Run scripts defined in pyproject.toml
python -m smart_home_anomaly_detection.run_server
python -m smart_home_anomaly_detection.generate_model
```

Key features of the packaging configuration:

- **Project Metadata**: Name, version, description, authors, classifiers
- **Dependencies**: All required packages with version constraints
- **Entry Points**: Command-line scripts for running the server and generating models
- **Development Tools**: Configuration for pytest, black, isort, and pylint
- **Python Compatibility**: Supports Python 3.8, 3.9, and 3.10

### Logs

The system generates several log files that can help with troubleshooting:

- **Server Logs**: `server/logs/server.log`
  - Contains detailed information about server operations, errors, and warnings
  - Useful for debugging server-side issues

- **Event Logs**: `logs/events_YYYY-MM-DD.json`
  - Contains records of detected events
  - Useful for reviewing system activity and verifying functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.