#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo ""
echo "Starting AI Receptionist Server..."
echo "Open a new terminal and run: ngrok http 5000"
echo ""
python server.py
