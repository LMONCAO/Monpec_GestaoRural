#!/bin/bash
# ========================================
# EXECUTAR MIGRAÇÕES MANUALMENTE
# Alternativa se o job não funcionar
# ========================================

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "  EXECUTAR MIGRAÇÕES MANUALMENTE"
echo "========================================"
echo ""

# Opção 1: Executar via Cloud Run Jobs (recomendado)
echo "OPÇÃO 1: Via Cloud Run Jobs"
echo "----------------------------------------"
echo "Execute:"
echo "  gcloud run jobs execute migrate-monpec --region $REGION --wait"
echo ""

# Opção 2: Executar via Cloud Shell diretamente
echo "OPÇÃO 2: Via Cloud Shell (se tiver acesso ao banco)"
echo "----------------------------------------"
echo "1. Conecte ao Cloud SQL:"
echo "   gcloud sql connect monpec-db --user=monpec_user"
echo ""
echo "2. Ou execute via container temporário:"
echo "   gcloud run jobs create migrate-temp \\"
echo "     --image ${IMAGE_NAME}:latest \\"
echo "     --region $REGION \\"
echo "     --set-env-vars \"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\\\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db\" \\"
echo "     --command python \\"
echo "     --args manage.py,migrate,--noinput \\"
echo "     --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db"
echo ""
echo "   gcloud run jobs execute migrate-temp --region $REGION --wait"
echo ""

# Opção 3: Ver logs do job que falhou
echo "OPÇÃO 3: Ver logs do erro"
echo "----------------------------------------"
echo "Execute:"
echo "  gcloud run jobs executions list --job migrate-monpec --region $REGION"
echo "  gcloud run jobs executions logs read [EXECUTION_NAME] --region $REGION"
echo ""









