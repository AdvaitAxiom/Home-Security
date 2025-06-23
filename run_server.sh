#!/bin/bash
# Smart Home Anomaly Detection System - Server Runner Script
# This script activates the virtual environment and starts the Flask server

# Set text colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Function to check if virtual environment exists
check_virtualenv() {
    if [ ! -f "venv/bin/activate" ]; then
        echo -e "${RED}Virtual environment not found.${NC}"
        echo -e "${YELLOW}Please run setup.sh first to set up the environment.${NC}"
        return 1
    fi
    return 0
}

# Function to check if model exists
check_model() {
    if [ ! -f "model/sound_classifier.pkl" ]; then
        echo -e "${YELLOW}Pre-trained model not found.${NC}"
        read -p "Do you want to generate the model now? (y/n): " generate_model
        if [ "$generate_model" = "y" ]; then
            echo -e "${CYAN}Generating model...${NC}"
            python model/generate_model.py
            if [ $? -ne 0 ]; then
                echo -e "${RED}Failed to generate model.${NC}"
                return 1
            fi
            echo -e "${GREEN}Model generated successfully.${NC}"
        else
            echo -e "${YELLOW}Warning: Server will run without a model. Sound classification will use fallback method.${NC}"
        fi
    else
        echo -e "${GREEN}Pre-trained model found.${NC}"
    fi
    return 0
}

# Function to start the server
start_server() {
    local host="$1"
    local port="$2"
    local debug="$3"
    
    local debug_flag=""
    if [ "$debug" = "y" ]; then
        debug_flag="--debug"
    fi
    
    echo -e "${CYAN}Starting server on $host:$port...${NC}"
    
    # Set environment variables
    export SERVER_HOST="$host"
    export SERVER_PORT="$port"
    export DEBUG_MODE="$([ "$debug" = "y" ] && echo "True" || echo "False")"
    
    # Start the server
    python server/app.py $debug_flag
}

# Make script executable
chmod +x "$0"

# Main script
echo -e "${CYAN}Smart Home Anomaly Detection System - Server Runner${NC}"
echo -e "${CYAN}==============================================${NC}"

# Check if virtual environment exists
if ! check_virtualenv; then
    exit 1
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if model exists
if ! check_model; then
    exit 1
fi

# Get server configuration
echo -e "\n${CYAN}Server Configuration:${NC}"
read -p "Host (default: 127.0.0.1): " host_input
read -p "Port (default: 5000): " port_input
read -p "Debug mode (y/n) (default: n): " debug_input

host_value=${host_input:-"127.0.0.1"}
port_value=${port_input:-5000}
debug_value=${debug_input:-"n"}

# Start the server
start_server "$host_value" "$port_value" "$debug_value"