# PulseOps AI - Complete Development Bible (Implementation Guide)

This document is the code documentation for developers and judges reviewing the **PulseOps AI** code modules.

---

## 🐍 1. Synthetic Data Generation Module

### Location: `datasets/generate_data.py`
This module generates configurable datasets dynamically scaling from Small to Large profiles.

```python
# Scale configuration profiles mapping
SCALES = {
    "SMALL": {
        "telemetry": 10000,
        "maintenance": 500,
        "occupancy": 1000,
        "incidents": 200
    },
    "MEDIUM": {
        "telemetry": 250000,
        "maintenance": 5000,
        "occupancy": 10000,
        "incidents": 2000
    },
    "LARGE": {
        "telemetry": 1000000,
        "maintenance": 20000,
        "occupancy": 50000,
        "incidents": 10000
    }
}
```

---

## 📊 2. NVIDIA RAPIDS cuDF Data Analytics Pipeline

### Location: `analytics/pipeline.py`
This module executes GPU-accelerated groupby aggregates and rolling averages. It implements a fallback Development Mode using Pandas.

```python
# CPU Fallback / GPU Switch logic
GPU_AVAILABLE = False
try:
    import cudf
    import cupy as cp
    GPU_AVAILABLE = True
    print("[NVIDIA RAPIDS] CUDA-enabled GPU detected. Running in Production (cuDF) mode.")
except ImportError:
    print("[NVIDIA RAPIDS] CUDA not available. Running in Development (Pandas) mode.")
```

---

## 🤖 3. AI Engines & Validation Services

### AI Decision Engine (`backend/app/services/decision_engine.py`)
Computes the Operational Priority Score (OPS) using weight metrics:
```python
def calculate_equipment_ops(telemetry_row: dict, maintenance_record: dict = None) -> float:
    # Heuristic Weights (ML targets in future scopes)
    w_utilization = 30
    w_temperature = 20
    w_alarm = 30
    w_service_delay = 20
    
    score_util = telemetry_row.get("utilization_rate", 0.0) * w_utilization
    # ...
    total_ops = score_util + score_temp + score_alarm + score_service
    return round(min(100.0, total_ops), 1)
```

### Recommendation Validation (`backend/app/services/validation.py`)
Verifies constraints before recommending allocations:
```python
def validate_resource_reallocation(equipment_id: str, source_dept: str, dest_dept: str, telemetry_data: list, maintenance_data: list) -> bool:
    # Check if target device is currently in active maintenance (downtime > 0)
    # Check if target device has critical alarms
    # Ensure source department retains at least one backup operational device
    ...
```

---

## 🐳 4. Monorepo Multi-Stage Dockerfile

### Location: `Dockerfile`
A single Dockerfile compiles static Vite React pages, copies assets to the FastAPI filesystem, and serves everything on port 8080.

```dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=frontend-builder /frontend/dist /frontend/dist
COPY backend/app ./backend/app
COPY analytics ./analytics
COPY datasets ./datasets
EXPOSE 8080
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```
