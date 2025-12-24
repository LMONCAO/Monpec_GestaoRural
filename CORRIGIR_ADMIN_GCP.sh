#!/bin/bash
# Script para corrigir usuário admin no Google Cloud Run
# Execute: bash CORRIGIR_ADMIN_GCP.sh

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"
JOB_NAME="monpec-corrigir-admin"

echo "========================================"
echo "  CORRIGINDO USUÁRIO ADMIN"
echo "  Google Cloud Run"
echo "========================================"
echo ""

# Configurar projeto
echo "Configurando projeto: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Comando Python para corrigir admin
PYTHON_COMMAND='import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model, authenticate; User = get_user_model(); username = "admin"; password = "L6171r12@@"; user, created = User.objects.get_or_create(username=username, defaults={"email": "admin@monpec.com.br", "is_staff": True, "is_superuser": True, "is_active": True}); user.set_password(password); user.is_staff = True; user.is_superuser = True; user.is_active = True; user.email = "admin@monpec.com.br"; user.save(); print("✅ Admin corrigido!"); print(f"Username: {username}"); print(f"Password: {password}"); auth = authenticate(username=username, password=password); print(f"✅ Autenticação: {\"SUCESSO\" if auth else \"FALHOU\"}")'

echo "Criando/atualizando Cloud Run Job..."

# Verificar se o job existe
JOB_EXISTS=$(gcloud run jobs describe ${JOB_NAME} --region ${REGION} --format="value(metadata.name)" 2>&1 || echo "")

if [ -z "$JOB_EXISTS" ]; then
    echo "Criando novo job..."
    gcloud run jobs create ${JOB_NAME} \
        --image ${IMAGE_NAME} \
        --region ${REGION} \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
        --command python \
        --args -c,"${PYTHON_COMMAND}" \
        --max-retries 1 \
        --task-timeout 300 \
        --quiet
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao criar job"
        exit 1
    fi
    echo "✅ Job criado!"
else
    echo "Atualizando job existente..."
    gcloud run jobs update ${JOB_NAME} \
        --image ${IMAGE_NAME} \
        --region ${REGION} \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
        --command python \
        --args -c,"${PYTHON_COMMAND}" \
        --max-retries 1 \
        --task-timeout 300 \
        --quiet
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao atualizar job"
        exit 1
    fi
    echo "✅ Job atualizado!"
fi

echo ""
echo "Executando correção do admin..."
echo "(Isso pode levar alguns minutos...)"
echo ""

# Executar o job
gcloud run jobs execute ${JOB_NAME} --region ${REGION} --wait

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro ao executar job"
    echo ""
    echo "Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=${JOB_NAME}" --limit 30 --format="value(textPayload)" --project ${PROJECT_ID} | tail -30
    exit 1
fi

echo ""
echo "========================================"
echo "  ✅ ADMIN CORRIGIDO COM SUCESSO!"
echo "========================================"
echo ""
echo "Credenciais:"
echo "  Usuário: admin"
echo "  Senha: L6171r12@@"
echo "  Email: admin@monpec.com.br"
echo ""
echo "Acesse: https://monpec.com.br/login/"
echo ""

# Perguntar se deseja remover o job
read -p "Deseja remover o job temporário? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    gcloud run jobs delete ${JOB_NAME} --region ${REGION} --quiet
    echo "✅ Job removido"
else
    echo "Job mantido para uso futuro"
fi

echo ""












