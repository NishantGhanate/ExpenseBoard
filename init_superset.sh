#!/bin/bash
set -e

# First-time initialization
if [ ! -f /app/superset_home/initialized ]; then
  echo "Running first-time setup..."

  superset db upgrade

  superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@superset.com \
    --password admin

  superset init

  touch /app/superset_home/initialized
fi

echo "Starting Superset..."
/usr/bin/run-server.sh
