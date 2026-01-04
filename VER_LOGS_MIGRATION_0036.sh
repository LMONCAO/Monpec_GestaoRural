#!/bin/bash
# Ver logs do erro na migration 0036
# Execute no Google Cloud Shell

echo "📋 Logs do erro na migration 0036:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-mig-final AND resource.labels.execution_name=aplicar-mig-final-4dfdb" --limit=100 --format="value(textPayload)" 2>/dev/null | tail -50


