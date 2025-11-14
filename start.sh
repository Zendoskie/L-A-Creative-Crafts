#!/bin/bash

# L&A Creative Crafts - Chatbot Startup Script

echo "======================================"
echo "L&A Creative Crafts - AI Chatbot"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "Dependencies installed!"
echo ""

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput
echo "Migrations completed!"
echo ""

# Start the server
echo "======================================"
echo "Starting Django development server..."
echo "======================================"
echo ""
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver

