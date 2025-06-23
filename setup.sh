#!/bin/bash
# Smart Home Anomaly Detection System - Setup Script
# This script sets up the Python virtual environment and installs dependencies

# Set text colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Function to check if Python is installed
check_python() {
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version)
        echo -e "${GREEN}Found $python_version${NC}"
        return 0
    else
        echo -e "${RED}Python 3 is not installed or not in PATH.${NC}"
        echo -e "${YELLOW}Please install Python 3.8 or higher from https://www.python.org/downloads/${NC}"
        return 1
    fi
}

# Function to create and activate virtual environment
setup_virtualenv() {
    venv_path="venv"
    
    # Check if virtual environment already exists
    if [ -d "$venv_path" ]; then
        echo -e "${YELLOW}Virtual environment already exists.${NC}"
        read -p "Do you want to recreate it? (y/n): " recreate
        if [ "$recreate" = "y" ]; then
            echo -e "${YELLOW}Removing existing virtual environment...${NC}"
            rm -rf "$venv_path"
        else
            echo -e "${GREEN}Using existing virtual environment.${NC}"
            return 0
        fi
    fi
    
    # Create virtual environment
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv "$venv_path"
    
    if [ ! -f "$venv_path/bin/activate" ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
    return 0
}

# Function to install dependencies
install_dependencies() {
    echo -e "${CYAN}Installing dependencies...${NC}"
    
    # Activate virtual environment
    source "venv/bin/activate"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install dependencies.${NC}"
            return 1
        fi
    else
        echo -e "${RED}requirements.txt not found.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
    return 0
}

# Function to generate the pre-trained model
generate_model() {
    echo -e "${CYAN}Generating pre-trained model...${NC}"
    
    # Activate virtual environment if not already activated
    if [[ "$(which python)" != *"venv"* ]]; then
        source "venv/bin/activate"
    fi
    
    # Run the model generation script
    if [ -f "model/generate_model.py" ]; then
        python model/generate_model.py
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to generate model.${NC}"
            return 1
        fi
    else
        echo -e "${RED}Model generation script not found.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Model generated successfully.${NC}"
    return 0
}

# Function to create necessary directories
create_directories() {
    directories=("logs" "model" "samples" "server/logs")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            echo -e "${CYAN}Creating directory: $dir${NC}"
            mkdir -p "$dir"
        fi
    done
    
    echo -e "${GREEN}Directories created successfully.${NC}"
    return 0
}

# Make script executable
chmod +x "$0"

# Main setup process
echo -e "${CYAN}Smart Home Anomaly Detection System - Setup${NC}"
echo -e "${CYAN}==========================================${NC}"

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. It's recommended to run this script as a regular user.${NC}"
    read -p "Continue as root? (y/n): " continue_as_root
    if [ "$continue_as_root" != "y" ]; then
        exit 1
    fi
fi

# Check Python installation
if ! check_python; then
    exit 1
fi

# Create necessary directories
if ! create_directories; then
    exit 1
fi

# Setup virtual environment
if ! setup_virtualenv; then
    exit 1
fi

# Install dependencies
if ! install_dependencies; then
    exit 1
fi

# Ask if user wants to generate the model
read -p "Do you want to generate the pre-trained model now? (y/n): " generate_model_now
if [ "$generate_model_now" = "y" ]; then
    if ! generate_model; then
        exit 1
    fi
fi

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "\n${CYAN}To start the server, run:${NC}"
echo -e "  1. Activate the virtual environment: ${NC}source venv/bin/activate"
echo -e "  2. Start the server: ${NC}python server/app.py"

echo -e "\n${CYAN}Press Enter to exit...${NC}"
read