# Create
docker network create shared_network

# List
docker network ls

# Inspect
docker network inspect shared_network

# Remove (when no longer needed)
docker network rm shared_network

# Use custom env file
docker compose --env-file .env.production up -d

# Use multiple env files (later overrides earlier)
docker compose --env-file .env --env-file .env.local up -d

# Show resolved config with all variables substituted
docker compose config

# Show specific variable
docker compose config | grep DATABASE_PASSWORD
