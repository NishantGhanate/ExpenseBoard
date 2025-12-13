import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "changeme")

SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://superset:superset@postgres:5432/superset"
)

SQLLAB_ASYNC_TIME_LIMIT_SEC = 0


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

CELERY_CONFIG = CeleryConfig

# Results backend - using dict config
RESULTS_BACKEND_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_results_",
    "CACHE_REDIS_URL": "redis://redis:6379/2",
}

ENABLE_PROXY_FIX = True
ROW_LEVEL_SECURITY = True
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}
