# gunicorn.conf.py
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8001)}"
workers = int(os.getenv('GUNICORN_WORKERS', 4))
worker_class = "uvicorn.workers.UvicornWorker"

accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')

timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))
keepalive = 5
graceful_timeout = 30

max_requests = 1000
max_requests_jitter = 50
