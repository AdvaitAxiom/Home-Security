# Smart Home Anomaly Detection System - Server Runner Script
# This script activates the virtual environment and starts the Flask server

# Function to check if virtual environment exists
function Check-VirtualEnv {
    if (-not (Test-Path "venv\Scripts\activate.ps1")) {
        Write-Host "Virtual environment not found." -ForegroundColor Red
        Write-Host "Please run setup.ps1 first to set up the environment." -ForegroundColor Yellow
        return $false
    }
    return $true
}

# Function to check if model exists
function Check-Model {
    if (-not (Test-Path "model\sound_classifier.pkl")) {
        Write-Host "Pre-trained model not found." -ForegroundColor Yellow
        $generateModel = Read-Host "Do you want to generate the model now? (y/n)"
        if ($generateModel -eq "y") {
            Write-Host "Generating model..." -ForegroundColor Cyan
            python model\generate_model.py
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Failed to generate model." -ForegroundColor Red
                return $false
            }
            Write-Host "Model generated successfully." -ForegroundColor Green
        } else {
            Write-Host "Warning: Server will run without a model. Sound classification will use fallback method." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Pre-trained model found." -ForegroundColor Green
    }
    return $true
}

# Function to start the server
function Start-Server {
    param (
        [string]$Host = "127.0.0.1",
        [int]$Port = 5000,
        [switch]$Debug
    )
    
    $debugFlag = if ($Debug) { "--debug" } else { "" }
    
    Write-Host "Starting server on ${Host}:${Port}..." -ForegroundColor Cyan
    
    # Set environment variables
    $env:SERVER_HOST = $Host
    $env:SERVER_PORT = $Port
    $env:DEBUG_MODE = if ($Debug) { "True" } else { "False" }
    
    # Start the server
    python server\app.py $debugFlag
}

# Main script
Write-Host "Smart Home Anomaly Detection System - Server Runner" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Check-VirtualEnv)) {
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\activate.ps1

# Check if model exists
if (-not (Check-Model)) {
    exit 1
}

# Get server configuration
Write-Host "\nServer Configuration:" -ForegroundColor Cyan
$host_input = Read-Host "Host (default: 127.0.0.1)"
$port_input = Read-Host "Port (default: 5000)"
$debug_input = Read-Host "Debug mode (y/n) (default: n)"

$host_value = if ([string]::IsNullOrWhiteSpace($host_input)) { "127.0.0.1" } else { $host_input }
$port_value = if ([string]::IsNullOrWhiteSpace($port_input)) { 5000 } else { [int]$port_input }
$debug_value = if ($debug_input -eq "y") { $true } else { $false }

# Start the server
Start-Server -Host $host_value -Port $port_value -Debug:$debug_value