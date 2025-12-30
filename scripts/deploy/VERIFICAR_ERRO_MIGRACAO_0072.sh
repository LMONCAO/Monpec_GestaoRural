#!/bin/bash
# Verificar logs do erro na migração 0072

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs do job apply-72-5q24p..."
echo ""

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-72 AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -150

echo ""
echo "================================================================================"
echo ""
echo "🔍 Verificando logs do job run-all-final-tdrdh..."
echo ""

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-final AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -150








