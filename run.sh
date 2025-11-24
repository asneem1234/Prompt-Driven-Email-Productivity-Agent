#!/bin/bash
# Quick start script for Linux/Mac

echo "================================"
echo "Email Productivity Agent"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "Checking dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo
echo "Starting application..."
echo
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo

streamlit run app.py
