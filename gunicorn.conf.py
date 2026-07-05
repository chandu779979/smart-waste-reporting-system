# gunicorn.conf.py — Production Gunicorn configuration for Render
import os

# ---------------------------------------------------------------------------
# Server socket
# Render injects PORT env var. Fall back to 10000 for local gunicorn tests.
# ---------------------------------------------------------------------------
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# ---------------------------------------------------------------------------
# Worker processes
# Render free tier has 512 MB RAM. 2 workers is safe.
# Formula: (2 × CPU cores) + 1  — but keep low on free tier.
# ---------------------------------------------------------------------------
workers = 2
worker_class = "sync"
threads = 2

# ---------------------------------------------------------------------------
# Timeouts
# ---------------------------------------------------------------------------
timeout = 120          # Kill workers that exceed 2 minutes (Google Maps geocoding can be slow)
keepalive = 5

# ---------------------------------------------------------------------------
# Logging — output to stdout so Render captures it in its log viewer
# ---------------------------------------------------------------------------
accesslog = "-"        # stdout
errorlog  = "-"        # stdout
loglevel  = "info"

# ---------------------------------------------------------------------------
# Process naming
# ---------------------------------------------------------------------------
proc_name = "smart-waste-mgmt"
