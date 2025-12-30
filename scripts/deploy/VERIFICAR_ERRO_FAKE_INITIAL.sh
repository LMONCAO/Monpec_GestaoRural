#!/bin/bash
# Verificar logs do job que falhou

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs do job que falhou..."
echo ""
echo "Execute este comando para ver os logs detalhados:"
echo ""
echo "gcloud run jobs executions describe run-migrations-fake-initial-pd194 --region us-central1 --format='value(status.logUri)'"
echo ""
echo "Ou acesse diretamente:"
echo "https://console.cloud.google.com/run/jobs/executions/details/us-central1/run-migrations-fake-initial-pd194?project=$PROJECT_ID"
echo ""
echo "Para ver os logs do container:"
echo "gcloud logging read 'resource.type=cloud_run_job AND resource.labels.job_name=run-migrations-fake-initial AND resource.labels.location=us-central1' --limit 50 --format json"








