#!/bin/bash

# Wait for X server and network
sleep 10

# Export display for GUI
export DISPLAY=:0

# Change to script directory
cd "$(dirname "$0")"

# Run the kiosk application
/usr/bin/python3 main.py 