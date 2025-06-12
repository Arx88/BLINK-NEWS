#!/bin/bash

# Print a startup message
echo "Starting BLINK NEWS installation..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "Error: pip is not installed. Please install pip and try again."
    exit 1
fi

# Create a virtual environment
echo "Creating virtual environment (blink_venv)..."
if ! python3 -m venv blink_venv
then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "Virtual environment created successfully."

# Activate virtual environment
echo "Activating virtual environment..."
source blink_venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements.txt..."
if ! pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies from requirements.txt."
    exit 1
fi
echo "Dependencies installed successfully."

# Install BLINK NEWS application
echo "Installing BLINK NEWS application..."
if ! python setup.py install; then
    echo "Error: Failed to install BLINK NEWS application."
    exit 1
fi
echo "BLINK NEWS application installed successfully."

# Print final success message
echo "Installation complete! To run BLINK NEWS, activate the virtual environment by running: source blink_venv/bin/activate"
