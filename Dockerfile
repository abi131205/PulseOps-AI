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

# FIX (Bug #1): Copy compiled React static assets into /app/frontend/dist
# main.py resolves the path as "<main.py location>/../../frontend/dist" which,
# once backend/app is copied into /app below, resolves to /app/frontend/dist.
# The old path "COPY --from=frontend-builder /frontend/dist /frontend/dist"
# copied to the container ROOT instead of /app, so the React build was never found.
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Copy backend application files
COPY backend/app ./backend/app

# Copy analytics and data pipelines
COPY analytics ./analytics
COPY datasets ./datasets

# FIX (Bug #2): Copy in the runtime entrypoint script instead of generating
# data at build time. Data generation now happens on container START, so it
# respects whatever DATASET_PROFILE is passed in via `--set-env-vars` at deploy
# time (SMALL / MEDIUM / LARGE), instead of being permanently baked in as SMALL.
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Set runtime configurations
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV DATASET_PROFILE=SMALL

# Expose port and run server via entrypoint (generates data, then starts uvicorn)
EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
