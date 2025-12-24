#!/bin/bash
# Script para criar usuário admin no Cloud Run
# Uso: ./criar_admin_cloud_run.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-"SEU_PROJECT_ID"}
REGION=${2:-"us-central1"}
SERVICE_NAME="monpec"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🔐 Criando usuário administrador no Cloud Run..."

# Criar job temporário para executar o script
gcloud run jobs create monpec-create-admin \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
    --command python \
    --args criar_admin.py \
    --max-retries 1 \
    --task-timeout 300 \
    --quiet

# Executar o job
echo "Executando criação do usuário admin..."
gcloud run jobs execute monpec-create-admin --region ${REGION} --wait

# Ver logs
echo ""
echo "📋 Logs da execução:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=monpec-create-admin" \
    --limit 50 \
    --format json \
    --project ${PROJECT_ID} | grep -A 5 -B 5 "admin\|✅\|❌" || echo "Verifique os logs completos no Console do Google Cloud"

# Limpar job (opcional)
read -p "Deseja remover o job temporário? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    gcloud run jobs delete monpec-create-admin --region ${REGION} --quiet
    echo "✅ Job removido"
fi

echo ""
echo "✅ Processo concluído!"
echo "Acesse o sistema com:"
echo "  Username: admin"
echo "  Senha: L6171r12@@"



















