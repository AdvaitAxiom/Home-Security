# Update dependencies script for Windows

Write-Host "Updating dependencies for Smart Home Anomaly Detection System..."

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first."
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Update dependencies
Write-Host "Updating dependencies..."
pip install -r requirements.txt

Write-Host "Dependencies updated successfully!"
Write-Host "You can now run the server using .\run_server.ps1"