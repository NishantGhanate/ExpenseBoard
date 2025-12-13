# Expense Board


> docker build -t superset-custom .

> docker compose up -d

> docker logs superset_app -f

Visit me
> http://localhost:8088/login/

### Rebuilding
> docker compose down -v

> docker compose up -d --build

### Setup via terminal
```bash
# Enter the container
docker exec -it superset_app bash

# Initialize the database
superset db upgrade

# Create admin user
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin

# Initialize Superset
superset init

# Exit and restart
exit
docker restart superset_app
```


1. Database connection settings in Superset
When adding/editing your database connection in Superset, check the Advanced → Security settings:

Uncheck "Allow DDL" and "Allow DML" if you want read-only
But make sure "Allow this database to run non-SELECT statements" matches your needs

> docker restart superset_app superset_celery

For Async
```
docker build -t superset-custom .
docker compose down
docker compose up -d
```

### Debugging

# Remove the flag file and restart
docker exec -it superset_app rm -f /app/superset_home/initialized
docker restart superset_app

docker compose down -v   # -v removes volumes
docker compose up -d




# Debugging
> docker run --rm -it apache/superset:latest which uv
> docker run --rm -it apache/superset:latest ls -la /app/.venv/bin/


# Expense Dashboard

Includes:
- Superset dashboard export (`dashboard/expense_dashboard.json`)
- Dataset (schema + sample data)
- Dashboard screenshots (`assets/screenshots/`)

The dashboard provides:
- Monthly cashflow trends
- Category-wise spending breakdown
- Payment method analysis
- Goal progress tracking

Screenshots:
![Dashboard Overview](assets/screenshots/overview.png)
![Goals Tab](assets/screenshots/goals.png)
