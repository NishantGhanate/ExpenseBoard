import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "changeme")

SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://superset:superset@postgres:5432/superset"
)

# Redis Cache
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": "redis://redis:6379/1",
}
DATA_CACHE_CONFIG = CACHE_CONFIG

# Celery (async queries)
class CeleryConfig:
    broker_url = "redis://redis:6379/0"
    result_backend = "redis://redis:6379/0"
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
    }

CELERY_CONFIG = CeleryConfig

# Disable async if you don't want to run a Celery worker
# SQLLAB_ASYNC_TIME_LIMIT_SEC = 0

ENABLE_PROXY_FIX = True
ROW_LEVEL_SECURITY = True
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}
