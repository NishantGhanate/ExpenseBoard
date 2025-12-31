import os
from urllib.parse import quote_plus

# ============================================
# SECRET KEY
# ============================================
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "changeme")

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_USER = os.environ.get("DATABASE_USER", "superset")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "superset")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "postgres")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")
DATABASE_DB = os.environ.get("DATABASE_DB", "superset")

# URL encode password to handle special characters (@, #, %, etc.)
DATABASE_PASSWORD_ENCODED = quote_plus(DATABASE_PASSWORD)

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD_ENCODED}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

# ============================================
# REDIS CONFIGURATION
# ============================================
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

# Build Redis URL (with optional password)
if REDIS_PASSWORD:
    REDIS_PASSWORD_ENCODED = quote_plus(REDIS_PASSWORD)
    REDIS_BASE_URL = f"redis://:{REDIS_PASSWORD_ENCODED}@{REDIS_HOST}:{REDIS_PORT}"
else:
    REDIS_BASE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# ============================================
# CACHE CONFIGURATION
# ============================================
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300)),
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/1",
}
DATA_CACHE_CONFIG = CACHE_CONFIG

# ============================================
# CELERY CONFIGURATION (async queries)
# ============================================
class CeleryConfig:
    broker_url = f"{REDIS_BASE_URL}/0"
    result_backend = f"{REDIS_BASE_URL}/0"

CELERY_CONFIG = CeleryConfig

# ============================================
# RESULTS BACKEND
# ============================================
RESULTS_BACKEND_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(os.environ.get("RESULTS_CACHE_TIMEOUT", 86400)),
    "CACHE_KEY_PREFIX": "superset_results_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/2",
}

# ============================================
# SQL LAB CONFIGURATION
# ============================================
SQLLAB_ASYNC_TIME_LIMIT_SEC = int(os.environ.get("SQLLAB_ASYNC_TIME_LIMIT_SEC", 0))

# ============================================
# SECURITY & FEATURES
# ============================================
ENABLE_PROXY_FIX = True
ROW_LEVEL_SECURITY = True

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

## Characters That Need Encoding
# ```
# @ → %40
# # → %23
# % → %25
# : → %3A
# / → %2F
# ? → %3F
# & → %26
# = → %3D
# + → %2B
#   → %20 (space)
