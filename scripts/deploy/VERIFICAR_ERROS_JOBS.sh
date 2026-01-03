#!/bin/bash
# Verificar logs dos jobs que falharam

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs do job run-migrations-step2..."
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-migrations-step2 AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID

echo ""
echo "================================================================================"
echo ""
echo "🔍 Verificando logs do job create-admin-step3..."
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=create-admin-step3 AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID

echo ""
echo "================================================================================"
echo ""
echo "Para ver mais detalhes, acesse:"
echo "https://console.cloud.google.com/run/jobs/executions?project=$PROJECT_ID"








