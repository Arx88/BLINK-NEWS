#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Print each command to stderr before executing it.
set -x

echo "--- Starting BLINK NEWS installation script (install_blink_news.sh) ---"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "--- ERROR: Python 3 is not installed. Please install Python 3 and try again. ---"
    exit 1
fi
echo "--- Python 3 found. ---"

# Check if pip for Python 3 is installed (often pip3)
if ! command -v pip3 &> /dev/null
then
    echo "--- ERROR: pip3 is not installed. Please install pip3 for Python 3 and try again. ---"
    exit 1
fi
echo "--- pip3 found. ---"

# Create a virtual environment
echo "--- Creating virtual environment (blink_venv)... ---"
if ! python3 -m venv blink_venv
then
    echo "--- ERROR: Failed to create virtual environment. ---"
    exit 1
fi
echo "--- Virtual environment 'blink_venv' created successfully. ---"

echo "--- Upgrading pip, setuptools, and wheel in virtual environment... ---"
if ! blink_venv/bin/python -m pip install --upgrade pip setuptools wheel; then
    echo "--- ERROR: Failed to upgrade pip, setuptools, or wheel. ---"
    exit 1
fi
echo "--- Build tools upgraded successfully. ---"

# Install dependencies using pip from the virtual environment
echo "--- Installing dependencies from requirements.txt into blink_venv... ---"
if ! blink_venv/bin/pip install -r requirements.txt; then
    echo "--- ERROR: Failed to install dependencies from requirements.txt. ---"
    exit 1
fi
echo "--- Dependencies installed successfully. ---"

# Install BLINK NEWS application using python from the virtual environment
echo "--- Installing BLINK NEWS application into blink_venv... ---"
if ! blink_venv/bin/python setup.py install; then
    echo "--- ERROR: Failed to install BLINK NEWS application. ---"
    exit 1
fi
echo "--- BLINK NEWS application installed successfully. ---"

echo "--- Installation complete! ---"
echo "--- To run BLINK NEWS, activate the virtual environment by running: ---"
echo "--- source blink_venv/bin/activate ---"

# Turn off command printing
set +x
