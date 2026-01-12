FROM apache/superset:latest

USER root

# 1. Create internal directories and set permissions
RUN mkdir -p /app/superset_home

# Install Postgres driver into Superset's venv
RUN uv pip install --python /app/.venv/bin/python psycopg2-binary pillow weasyprint

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER superset
