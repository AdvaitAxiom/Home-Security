#!/bin/bash
# Update dependencies script for Linux/macOS

echo "Updating dependencies for Smart Home Anomaly Detection System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Update dependencies
echo "Updating dependencies..."
pip install -r requirements.txt

echo "Dependencies updated successfully!"
echo "You can now run the server using ./run_server.sh"