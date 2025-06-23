# Smart Home Anomaly Detection System - Setup Script
# This script sets up the Python virtual environment and installs dependencies

# Function to check if Python is installed
function Check-Python {
    try {
        $pythonVersion = python --version
        Write-Host "Found $pythonVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Python 3.8 or higher from https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
}

# Function to create and activate virtual environment
function Setup-VirtualEnv {
    $venvPath = "venv"
    
    # Check if virtual environment already exists
    if (Test-Path $venvPath) {
        Write-Host "Virtual environment already exists." -ForegroundColor Yellow
        $recreate = Read-Host "Do you want to recreate it? (y/n)"
        if ($recreate -eq "y") {
            Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $venvPath
        } else {
            Write-Host "Using existing virtual environment." -ForegroundColor Green
            return $true
        }
    }
    
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $venvPath
    
    if (-not (Test-Path "$venvPath\Scripts\activate.ps1")) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        return $false
    }
    
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
    return $true
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    
    # Activate virtual environment
    & .\venv\Scripts\activate.ps1
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies from requirements.txt
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install dependencies." -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "requirements.txt not found." -ForegroundColor Red
        return $false
    }
    
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
    return $true
}

# Function to generate the pre-trained model
function Generate-Model {
    Write-Host "Generating pre-trained model..." -ForegroundColor Cyan
    
    # Activate virtual environment if not already activated
    if (-not (Get-Command python).Path.Contains("venv")) {
        & .\venv\Scripts\activate.ps1
    }
    
    # Run the model generation script
    if (Test-Path "model\generate_model.py") {
        python model\generate_model.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to generate model." -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "Model generation script not found." -ForegroundColor Red
        return $false
    }
    
    Write-Host "Model generated successfully." -ForegroundColor Green
    return $true
}

# Function to create necessary directories
function Create-Directories {
    $directories = @("logs", "model", "samples", "server\logs")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            Write-Host "Creating directory: $dir" -ForegroundColor Cyan
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Host "Directories created successfully." -ForegroundColor Green
    return $true
}

# Main setup process
Write-Host "Smart Home Anomaly Detection System - Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Note: Some operations may require administrator privileges." -ForegroundColor Yellow
}

# Check Python installation
if (-not (Check-Python)) {
    exit 1
}

# Create necessary directories
if (-not (Create-Directories)) {
    exit 1
}

# Setup virtual environment
if (-not (Setup-VirtualEnv)) {
    exit 1
}

# Install dependencies
if (-not (Install-Dependencies)) {
    exit 1
}

# Ask if user wants to generate the model
$generateModel = Read-Host "Do you want to generate the pre-trained model now? (y/n)"
if ($generateModel -eq "y") {
    if (-not (Generate-Model)) {
        exit 1
    }
}

Write-Host "\nSetup completed successfully!" -ForegroundColor Green
Write-Host "\nTo start the server, run:" -ForegroundColor Cyan
Write-Host "  1. Activate the virtual environment: .\venv\Scripts\activate.ps1" -ForegroundColor White
Write-Host "  2. Start the server: python server\app.py" -ForegroundColor White

Write-Host "\nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")