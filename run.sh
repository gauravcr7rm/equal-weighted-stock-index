#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

# Run data acquisition job
echo "Running data acquisition job..."
python3 -m app.jobs.data_acquisition

# Start the API server
echo "Starting API server..."
python3 -m uvicorn app.main:app --reload
