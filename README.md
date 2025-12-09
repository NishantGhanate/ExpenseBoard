# Expense Board


> docker build -t superset-custom .

> docker compose up -d

> docker logs superset_app -f


### Rebuilding
> docker compose down -v

> docker compose up -d --build


docker compose run superset superset db upgrade
docker compose run superset superset fab create-admin \
    --username admin --firstname Superset --lastname Admin \
    --email admin@superset.com --password admin
docker compose run superset superset init
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
