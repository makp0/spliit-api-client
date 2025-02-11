#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create and activate a virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install the package and test dependencies
echo "Installing dependencies..."
pip install -e ".[test]"

# Start the containers in the background
echo "Starting Docker containers..."
cd "$PROJECT_ROOT/spliit"
docker compose down -v
docker compose up -d --wait

# Set environment variable to point to local instance
export SPLIIT_SERVER_URL="http://localhost:3000"

# Run the tests
echo "Running integration tests..."
cd "$PROJECT_ROOT"
pytest tests/test_integration.py -v

# Cleanup
echo "Cleaning up..."
cd "$PROJECT_ROOT/spliit"
docker compose down -v

# Deactivate virtual environment
deactivate 