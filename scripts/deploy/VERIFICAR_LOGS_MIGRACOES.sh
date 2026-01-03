#!/bin/bash
# Verificar logs do job de migrações que falhou

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs do job run-migrations-normal-mbwww..."
echo ""
echo "Execute este comando para ver os logs:"
echo ""
echo "gcloud logging read 'resource.type=cloud_run_job AND resource.labels.job_name=run-migrations-normal AND resource.labels.location=us-central1' --limit 100 --format='table(timestamp,textPayload)' --project=$PROJECT_ID"
echo ""
echo "Ou acesse diretamente:"
echo "https://console.cloud.google.com/run/jobs/executions/details/us-central1/run-migrations-normal-mbwww?project=$PROJECT_ID"








