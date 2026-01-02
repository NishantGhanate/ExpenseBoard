FROM apache/superset:latest

USER root

# Install Postgres driver into Superset's venv
RUN uv pip install --python /app/.venv/bin/python psycopg2-binary pillow weasyprint

USER superset
