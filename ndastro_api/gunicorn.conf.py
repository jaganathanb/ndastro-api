"""Gunicorn configuration file for ndastro_api.

This module sets up server socket, worker processes, logging, process naming, server mechanics,
and memory management for running the ndastro_api application with Gunicorn and Uvicorn workers.
"""

import multiprocessing
import tempfile

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 jitter
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ndastro_api"

# Server mechanics
daemon = False

with tempfile.NamedTemporaryFile(prefix="gunicorn_", suffix=".pid", delete=False) as tmpfile:
    pidfile = tmpfile.name
user = None
group = None
tmp_upload_dir = None


# Worker timeout
timeout = 30
keepalive = 2

# Memory management
max_requests = 1000
max_requests_jitter = 50
preload_app = True
