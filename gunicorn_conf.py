"""Gunicorn configuration for production deployment.

This module configures Gunicorn for production-ready deployment
with optimal worker settings and timeouts.
"""

import multiprocessing

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Binding
bind = "0.0.0.0:8000"

# Timeouts
timeout = 120  # DeepSeek API can be slow
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "madeena-core"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"


def on_starting(server):
    """Called just before the master process is initialized."""
    print("Gunicorn master process starting...")


def on_reload(server):
    """Called when the configuration is reloaded."""
    print("Gunicorn configuration reloaded")


def when_ready(server):
    """Called just after the server is started."""
    print(f"Gunicorn is ready. Listening on {bind}")
    print(f"Workers: {workers}")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Gunicorn master process shutting down...")
