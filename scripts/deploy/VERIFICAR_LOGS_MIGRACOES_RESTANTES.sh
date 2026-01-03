#!/bin/bash
# Verificar logs do job que falhou ao executar todas as migrações

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs do job run-all-migrations-lwdc7..."
echo ""

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-migrations AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -150








