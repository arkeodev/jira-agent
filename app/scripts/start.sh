#!/bin/bash
set -e

echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload