#!/bin/bash
# Startup script for Railway deployment
# Railway sets $PORT environment variable automatically

PORT=${PORT:-8000}
exec uvicorn api.heavy:app --host 0.0.0.0 --port $PORT
