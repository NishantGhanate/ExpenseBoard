#!/bin/bash
set -e

# Always run db upgrade (safe to run multiple times)
echo "Running database migrations..."
superset db upgrade

# Create admin only if not exists (the || true handles "already exists" error)
echo "Ensuring admin user exists..."
superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com \
  --password admin 2>/dev/null || echo "Admin user already exists"

# Always run init (safe to run multiple times)
superset init

echo "Starting Superset..."
/usr/bin/run-server.sh
