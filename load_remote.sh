#!/bin/bash

# Find the PID of the Flask app process
PID=$(pgrep -f "python[3]? app.py")

if [ -n "$PID" ]; then
    echo "Flask app process found with PID: $PID"

  # Kill the Flask app process
  echo "Killing Flask app process..."
  kill -9 $PID
  sleep 2

  # Pull changes from GitHub
  echo "Pulling changes from GitHub..."
  git pull

  # Run the Flask app again
  echo "Running the Flask app..."
  python3 app.py &
else
    echo "Flask app process not found."
fi
