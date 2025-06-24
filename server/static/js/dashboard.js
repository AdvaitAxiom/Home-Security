/**
 * Smart Home Anomaly Detection System - Dashboard JavaScript
 * 
 * This file contains the JavaScript code for the dashboard UI,
 * including data fetching, chart rendering, and UI updates.
 */

// Global variables
let statusUpdateInterval;
let chartUpdateInterval;
let soundChart;
let riskChart;
let eventLog = [];
let currentStatus = {};

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventHandlers();
    updateStatus();
    updateCharts();
    
    // Set up intervals for automatic updates
    statusUpdateInterval = setInterval(updateStatus, 10000); // Update status every 10 seconds
    chartUpdateInterval = setInterval(updateCharts, 30000);  // Update charts every 30 seconds
});

/**
 * Initialize the charts using Chart.js
 */
function initializeCharts() {
    // Sound amplitude chart
    const soundCtx = document.getElementById('soundChart').getContext('2d');
    soundChart = new Chart(soundCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Sound Amplitude',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amplitude'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sound Amplitude Over Time'
                }
            }
        }
    });
    
    // Risk level chart (doughnut chart)
    const riskCtx = document.getElementById('riskChart').getContext('2d');
    riskChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Safe', 'Low', 'Medium', 'High'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',  // Safe - Green
                    'rgba(255, 206, 86, 0.8)',  // Low - Yellow
                    'rgba(255, 159, 64, 0.8)',  // Medium - Orange
                    'rgba(255, 99, 132, 0.8)'   // High - Red
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Risk Level Distribution'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Set up event handlers for buttons and forms
 */
function setupEventHandlers() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', function() {
        updateStatus();
        updateCharts();
    });
    
    // Simulate data form
    document.getElementById('simulateForm').addEventListener('submit', function(e) {
        e.preventDefault();
        simulateData();
    });
    
    // Clear events button
    document.getElementById('clearEventsBtn').addEventListener('click', function() {
        clearEvents();
    });
}

/**
 * Update the system status by fetching data from the API
 */
function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            currentStatus = data;
            updateStatusUI(data);
        })
        .catch(error => {
            console.error('Error fetching status:', error);
            showError('Failed to fetch system status. Check server connection.');
        });
}

/**
 * Update the UI with the current system status
 */
function updateStatusUI(data) {
    // Update status indicators
    document.getElementById('serverStatus').textContent = data.server_status;
    document.getElementById('modelStatus').textContent = data.model_loaded ? 'Loaded' : 'Not Loaded';
    document.getElementById('lastUpdate').textContent = formatDateTime(data.timestamp);
    
    // Update ThingSpeak panel
    document.getElementById('channelId').textContent = data.thingspeak_channel || 'N/A';
    document.getElementById('thingspeakLastUpdate').textContent = data.last_data_fetch || 'N/A';
    
    // Update current sensor values in both panels
    if (data.last_data) {
        // Update Status Panel
        document.getElementById('currentSound').textContent = data.last_data.amplitude;
        document.getElementById('currentPattern').textContent = data.last_data.pattern_id;
        document.getElementById('flameStatus').textContent = data.last_data.flame_detected ? 'Detected' : 'None';
        document.getElementById('motionStatus').textContent = data.last_data.motion_detected ? 'Detected' : 'None';
        
        // Update ThingSpeak Data Panel
        document.getElementById('tsSound').textContent = data.last_data.amplitude;
        document.getElementById('tsPattern').textContent = data.last_data.pattern_id;
        document.getElementById('tsFlame').textContent = data.last_data.flame_detected ? 'Yes' : 'No';
        document.getElementById('tsMotion').textContent = data.last_data.motion_detected ? 'Yes' : 'No';
        
        // Update AI Prediction section
        if (data.last_analysis) {
            document.getElementById('aiSoundType').textContent = data.last_analysis.sound_type;
            document.getElementById('aiConfidence').textContent = 
                (data.last_analysis.confidence * 100).toFixed(1) + '%';
            
            // Update risk level indicators
            const riskLevel = data.last_analysis.risk_level;
            
            // Update in Status Panel
            const riskIndicator = document.getElementById('riskIndicator');
            riskIndicator.textContent = riskLevel;
            
            // Update in AI Prediction Panel
            const aiRisk = document.getElementById('aiRisk');
            aiRisk.textContent = riskLevel;
            
            // Set color based on risk level for both indicators
            riskIndicator.className = 'risk-indicator';
            aiRisk.className = 'prediction-value risk-indicator';
            
            if (riskLevel === 'high') {
                riskIndicator.classList.add('high-risk');
                aiRisk.classList.add('high-risk');
            } else if (riskLevel === 'medium') {
                riskIndicator.classList.add('medium-risk');
                aiRisk.classList.add('medium-risk');
            } else if (riskLevel === 'low') {
                riskIndicator.classList.add('low-risk');
                aiRisk.classList.add('low-risk');
            } else if (riskLevel === 'safe') {
                riskIndicator.classList.add('safe');
                aiRisk.classList.add('safe');
            }
            
            // Update sound type in Status Panel
            document.getElementById('soundType').textContent = data.last_analysis.sound_type;
        }
    }
    
    // Show any recommendations
    if (data.last_analysis && data.last_analysis.recommendations) {
        const recsContainer = document.getElementById('recommendations');
        recsContainer.innerHTML = '';
        
        if (data.last_analysis.recommendations.length === 0) {
            const recItem = document.createElement('div');
            recItem.className = 'recommendation-item';
            recItem.textContent = 'No recommendations available based on current ThingSpeak data';
            recsContainer.appendChild(recItem);
        } else {
            data.last_analysis.recommendations.forEach(rec => {
                const recItem = document.createElement('div');
                recItem.className = 'recommendation-item';
                
                // Apply special classes based on content
                if (rec.includes('⚠️')) {
                    recItem.classList.add('warning-rec');
                } else if (rec.includes('🚨') || rec.includes('🆘')) {
                    recItem.classList.add('critical-rec');
                } else if (rec.includes('✅')) {
                    recItem.classList.add('safe-rec');
                }
                
                recItem.textContent = rec;
                recsContainer.appendChild(recItem);
            });
        }
    }
}

/**
 * Update the charts with the latest data
 */
function updateCharts() {
    fetch('/analyze')
        .then(response => response.json())
        .then(data => {
            updateSoundChart(data);
            updateEventLog(data);
            updateRiskDistribution();
        })
        .catch(error => {
            console.error('Error fetching analysis data:', error);
        });
}

/**
 * Update the sound amplitude chart with new data
 */
function updateSoundChart(data) {
    // Only update if we have sensor data
    if (!data.sensor_data) return;
    
    // Format timestamp for display
    const timestamp = formatTime(data.timestamp);
    
    // Add new data point
    soundChart.data.labels.push(timestamp);
    soundChart.data.datasets[0].data.push(data.sensor_data.amplitude);
    
    // Keep only the last 20 data points for better visualization
    if (soundChart.data.labels.length > 20) {
        soundChart.data.labels.shift();
        soundChart.data.datasets[0].data.shift();
    }
    
    // Update the chart
    soundChart.update();
}

/**
 * Update the event log with new events
 */
function updateEventLog(data) {
    // Only add to log if this is a new event with analysis
    if (!data.analysis || !data.timestamp) return;
    
    // Create a new event object
    const newEvent = {
        timestamp: data.timestamp,
        sound_type: data.analysis.sound_type,
        risk_level: data.analysis.risk_level,
        amplitude: data.sensor_data.amplitude,
        flame_detected: data.sensor_data.flame_detected,
        motion_detected: data.sensor_data.motion_detected
    };
    
    // Check if this is a duplicate event (same timestamp)
    const isDuplicate = eventLog.some(event => event.timestamp === newEvent.timestamp);
    if (!isDuplicate) {
        // Add to the beginning of the array
        eventLog.unshift(newEvent);
        
        // Keep only the last 50 events
        if (eventLog.length > 50) {
            eventLog.pop();
        }
        
        // Update the UI
        updateEventLogUI();
    }
}

/**
 * Update the event log UI
 */
function updateEventLogUI() {
    const logContainer = document.getElementById('eventLogItems');
    logContainer.innerHTML = '';
    
    eventLog.forEach(event => {
        const logItem = document.createElement('div');
        logItem.className = `event-item ${event.risk_level}-risk`;
        
        const time = document.createElement('span');
        time.className = 'event-time';
        time.textContent = formatTime(event.timestamp);
        
        const type = document.createElement('span');
        type.className = 'event-type';
        type.textContent = event.sound_type;
        
        const risk = document.createElement('span');
        risk.className = 'event-risk';
        risk.textContent = event.risk_level;
        
        logItem.appendChild(time);
        logItem.appendChild(type);
        logItem.appendChild(risk);
        
        logContainer.appendChild(logItem);
    });
}

/**
 * Update the risk distribution chart
 */
function updateRiskDistribution() {
    // Count occurrences of each risk level
    const riskCounts = {
        'safe': 0,
        'low': 0,
        'medium': 0,
        'high': 0
    };
    
    eventLog.forEach(event => {
        if (riskCounts.hasOwnProperty(event.risk_level)) {
            riskCounts[event.risk_level]++;
        }
    });
    
    // Update the chart data
    riskChart.data.datasets[0].data = [
        riskCounts.safe,
        riskCounts.low,
        riskCounts.medium,
        riskCounts.high
    ];
    
    // Update the chart
    riskChart.update();
}

/**
 * Simulate sensor data by sending a POST request to the /simulate endpoint
 */
function simulateData() {
    // Get form values
    const amplitude = document.getElementById('simAmplitude').value;
    const patternId = document.getElementById('simPattern').value;
    const flameDetected = document.getElementById('simFlame').checked;
    const motionDetected = document.getElementById('simMotion').checked;
    
    // Create request body
    const data = {
        sensor_data: {
            amplitude: parseInt(amplitude),
            pattern_id: parseInt(patternId),
            flame_detected: flameDetected,
            motion_detected: motionDetected
        }
    };
    
    // Send POST request
    fetch('/simulate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with the simulated data
        updateSoundChart(data);
        updateEventLog(data);
        updateRiskDistribution();
        updateStatusUI({
            server_status: currentStatus.server_status,
            model_loaded: currentStatus.model_loaded,
            timestamp: data.timestamp,
            last_data: data.sensor_data,
            last_analysis: data.analysis
        });
        
        // Show success message
        showMessage('Simulation data processed successfully');
    })
    .catch(error => {
        console.error('Error simulating data:', error);
        showError('Failed to simulate data. Check server connection.');
    });
}

/**
 * Clear the event log
 */
function clearEvents() {
    eventLog = [];
    updateEventLogUI();
    updateRiskDistribution();
    showMessage('Event log cleared');
}

/**
 * Format a timestamp into a readable date and time
 */
function formatDateTime(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Format a timestamp into a readable time only
 */
function formatTime(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

/**
 * Show a success message
 */
function showMessage(message) {
    const alertBox = document.getElementById('alertBox');
    alertBox.textContent = message;
    alertBox.className = 'alert alert-success';
    alertBox.style.display = 'block';
    
    // Hide after 3 seconds
    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 3000);
}

/**
 * Show an error message
 */
function showError(message) {
    const alertBox = document.getElementById('alertBox');
    alertBox.textContent = message;
    alertBox.className = 'alert alert-danger';
    alertBox.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 5000);
}