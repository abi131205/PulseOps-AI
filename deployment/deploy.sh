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

# FIX: fail fast with a clear message instead of silently deploying with
# an empty GEMINI_API_KEY (which would make Abijith's Gemini briefings fail
# silently in production).
if [ -z "${GEMINI_API_KEY}" ]; then
  echo "ERROR: GEMINI_API_KEY is not set. Add it to .env or export it before running this script."
  exit 1
fi

if [ "${PROJECT_ID}" == "your-gcp-project-id" ]; then
  echo "ERROR: GCP_PROJECT_ID is not set. Add it to .env or export it before running this script."
  exit 1
fi

# FIX: scale Cloud Run memory to the dataset profile. Pandas (no GPU on
# Cloud Run) holds the full merged dataset in memory - 2Gi is fine for
# SMALL/MEDIUM but risks an OOM kill on LARGE (1M+ rows) during
# process_cpu_metrics()'s merge/groupby steps in pipeline.py.
case "${DATASET_PROFILE:-SMALL}" in
  LARGE)
    RUN_MEMORY="8Gi"
    RUN_CPU="4"
    ;;
  MEDIUM)
    RUN_MEMORY="4Gi"
    RUN_CPU="2"
    ;;
  *)
    RUN_MEMORY="2Gi"
    RUN_CPU="1"
    ;;
esac

echo "=========================================================="
echo " Starting PulseOps AI Google Cloud Run Deployment Pipeline"
echo " Target Project: ${PROJECT_ID}"
echo " Service Region: ${REGION}"
echo " Dataset Profile: ${DATASET_PROFILE:-SMALL}"
echo " Allocated Memory/CPU: ${RUN_MEMORY} / ${RUN_CPU} vCPU"
echo "=========================================================="

# Step 1: Ensure gcloud authenticated
echo "Checking Google Cloud Authentication status..."
gcloud config set project "${PROJECT_ID}"

# Step 2: Submit build to Google Cloud Build
echo "Submitting Docker image compilation to Google Cloud Build..."
gcloud builds submit --tag "${IMAGE_TAG}" .

# Step 3: Deploy compiled container to Cloud Run
echo "Deploying container image to serverless Google Cloud Run..."
# FIX: GCP_PROJECT_ID and BIGQUERY_DATASET were never being passed to the
# running container, so pipeline.py's load_data_source() could never take
# the BigQuery path in production - it always silently fell back to CSV.
# Passing them explicitly now (still optional - unset GCP_PROJECT_ID here
# means "stay on CSV mode", which is a valid choice, just no longer silent).
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory "${RUN_MEMORY}" \
  --cpu "${RUN_CPU}" \
  --set-env-vars "DATASET_PROFILE=${DATASET_PROFILE:-SMALL},GEMINI_API_KEY=${GEMINI_API_KEY},CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS:-*},GCP_PROJECT_ID=${GCP_PROJECT_ID},BIGQUERY_DATASET=${BIGQUERY_DATASET:-pulseops_ai}"

# Retrieve service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')

echo "=========================================================="
echo " PulseOps AI deployment completed successfully!"
echo " Service Endpoint URL: ${SERVICE_URL}"
echo "=========================================================="
