#!/bin/bash

# Election Game Server Startup Script
# This script starts the Flask server on port 5001

echo "Starting Election Game Server..."
echo "Server will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

# Set the port and start the server
PORT=5001 python3 server.py 