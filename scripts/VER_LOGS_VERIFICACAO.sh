#!/bin/bash
# Ver logs da verificação de migrations
# Execute no Google Cloud Shell

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-migrations-estado" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[X\]|\[ \]|gestao_rural|sessions" | head -60
