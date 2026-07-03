#!/bin/bash

# Exit on first error
set -e

# Load environmental configurations
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | xargs)
fi

PROJECT_ID=${GCP_PROJECT_ID:-"your-gcp-project-id"}
REGION="us-central1"
SERVICE_NAME="pulseops-ai"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=========================================================="
echo " Starting PulseOps AI Google Cloud Run Deployment Pipeline"
echo " Target Project: ${PROJECT_ID}"
echo " Service Region: ${REGION}"
echo "=========================================================="

# Step 1: Ensure gcloud authenticated
echo "Checking Google Cloud Authentication status..."
gcloud config set project "${PROJECT_ID}"

# Step 2: Submit build to Google Cloud Build
echo "Submitting Docker image compilation to Google Cloud Build..."
gcloud builds submit --tag "${IMAGE_TAG}" .

# Step 3: Deploy compiled container to Cloud Run
echo "Deploying container image to serverless Google Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "DATASET_PROFILE=${DATASET_PROFILE:-SMALL},GEMINI_API_KEY=${GEMINI_API_KEY}"

# Retrieve service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')

echo "=========================================================="
echo " PulseOps AI deployment completed successfully!"
echo " Service Endpoint URL: ${SERVICE_URL}"
echo "=========================================================="
