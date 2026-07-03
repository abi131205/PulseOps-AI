# ==========================================
# STAGE 1: Build React Static Assets
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend

# Install dependencies
COPY frontend/package.json ./
RUN npm install

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ==========================================
# STAGE 2: Create Python Production Server
# ==========================================
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (build essentials for pyarrow if wheel fails, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy compiled React static assets from Stage 1
COPY --from=frontend-builder /frontend/dist /frontend/dist

# Copy backend application files
COPY backend/app ./backend/app

# Copy analytics and data pipelines
COPY analytics ./analytics
COPY datasets ./datasets

# Set runtime configurations
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV DATASET_PROFILE=SMALL

# Run synthetic data generator on container boot to ensure files exist
RUN python datasets/generate_data.py

# Expose port and run server
EXPOSE 8080
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
