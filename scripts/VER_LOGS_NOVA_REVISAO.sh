#!/bin/bash
# Ver logs da nova revisão para entender o problema
# Execute no Google Cloud Shell

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=monpec-00013-znt" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30


