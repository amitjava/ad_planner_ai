#!/bin/bash
# Smart Ad Planner - Google Cloud Run Deployment Script
# Deploys the multi-agent system to Cloud Run with ADC authentication

set -e  # Exit on error

# Configuration
PROJECT_ID="Gemini API"
REGION="us-central1"
SERVICE_NAME="smart-ad-planner"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Smart Ad Planner to Google Cloud Run"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Step 1: Set the project
echo "📋 Step 1: Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Step 2: Enable required APIs
echo "🔧 Step 2: Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    containerregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com

# Step 3: Build the container image
echo "🏗️  Step 3: Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Step 4: Deploy to Cloud Run
echo "☁️  Step 4: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars "GOOGLE_CLOUD_LOCATION=us-central1" \
    --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=true"

# Step 5: Get the service URL
echo "✅ Deployment complete!"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)')

echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "📝 Test your deployment:"
echo "curl ${SERVICE_URL}/health"
echo ""
echo "📊 View logs:"
echo "gcloud run logs tail ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "🎯 Generate a plan:"
echo "curl -X POST ${SERVICE_URL}/plan \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"business_name\": \"Test Coffee\", ...}'"
