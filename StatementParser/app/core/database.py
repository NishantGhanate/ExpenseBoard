"""
Reusable PostgreSQL database module using psycopg3
> pip install psycopg[binary,pool]
> python ./app/core/database.py
"""
import atexit
import logging
from contextlib import contextmanager
from typing import Any

import psycopg
from app.config.settings import settings
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

logger = logging.getLogger(name="app")

# _pool: ConnectionPool | None = None


# def get_pool() -> ConnectionPool:
#     global _pool
#     if _pool is None:
#         _pool = ConnectionPool(
#             conninfo=settings.SQL_DATABASE_URL,
#             min_size=5,
#             max_size=20,
#             timeout=20,
#             max_idle=300,
#             max_lifetime=3600,
#             open=True,
#         )
#         logger.info("Postgres pool created: %s", _pool.get_stats())
#     return _pool

# def close_pool() -> None:
#     """Close all connections in the pool gracefully."""
#     global _pool
#     if _pool:
#         logger.info("Closing database connection pool...")
#         _pool.close(timeout=5.0)

# @atexit.register
# def close_pool_exit():
#     pool = get_pool()
#     pool.close()


@contextmanager
def get_cursor():
    """
    Create a new DB connection per usage and close it safely.
    """
    conn = None
    try:
        conn = psycopg.connect(
            settings.SQL_DATABASE_URL,
            autocommit=True,          # avoid idle-in-transaction
            row_factory=dict_row,
            connect_timeout=10,
        )

        with conn.cursor() as cur:
            yield cur

    except Exception as e:
        logger.exception("Database error in get_cursor")
        raise

    finally:
        if conn is not None:
            conn.close()





# --- Testing ---
if __name__ == "__main__":

    pass
