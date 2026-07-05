#!/bin/bash
set -e

echo "=========================================================="
echo " PulseOps AI container starting"
echo " DATASET_PROFILE=${DATASET_PROFILE:-SMALL}"
echo "=========================================================="

# Generate synthetic dataset matching the profile requested at deploy time
# (SMALL / MEDIUM / LARGE). Running this here instead of at Docker build time
# means Meenakshi's MEDIUM/LARGE scale tests actually get the right data volume.
python datasets/generate_data.py

echo "Data generation complete. Starting Uvicorn server..."
exec uvicorn backend.app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8080}"
