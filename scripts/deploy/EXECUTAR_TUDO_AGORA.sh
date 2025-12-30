#!/bin/bash
# ========================================
# SCRIPT COMPLETO - EXECUTAR TUDO AGORA
# ========================================
# Este script faz TUDO automaticamente:
# 1. Verifica e corrige requirements.txt
# 2. Faz rebuild sem cache
# 3. Remove job antigo
# 4. Cria novo job
# 5. Executa migrações
# 6. Verifica resultado
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"

echo "========================================"
echo "  INICIANDO PROCESSO COMPLETO"
echo "========================================"
echo ""

# Configurar projeto
gcloud config set project $PROJECT_ID > /dev/null 2>&1
echo "✅ Projeto configurado: $PROJECT_ID"
echo ""

# ========================================
# PASSO 1: Verificar requirements.txt
# ========================================
echo "1. Verificando requirements.txt..."
if grep -q "^openpyxl" requirements.txt; then
    echo "   ✅ openpyxl encontrado no requirements.txt"
    grep "^openpyxl" requirements.txt
else
    echo "   ⚠️  openpyxl não encontrado! Adicionando..."
    if ! grep -q "openpyxl" requirements.txt; then
        echo "openpyxl>=3.1.5" >> requirements.txt
        echo "   ✅ openpyxl adicionado ao requirements.txt"
    fi
fi
echo ""

# ========================================
# PASSO 2: Criar build-config.yaml se não existir
# ========================================
echo "2. Verificando build-config.yaml..."
if [ ! -f "build-config.yaml" ]; then
    echo "   ⚠️  build-config.yaml não existe! Criando..."
    cat > build-config.yaml << 'EOF'
steps:
  # Build da imagem Docker SEM CACHE
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--no-cache'
      - '--tag'
      - 'gcr.io/$PROJECT_ID/monpec:latest'
      - '--file'
      - 'Dockerfile.prod'
      - '.'
  
  # Push da imagem para Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/monpec:latest'

images:
  - 'gcr.io/$PROJECT_ID/monpec:latest'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

timeout: '1800s'
EOF
    echo "   ✅ build-config.yaml criado"
else
    echo "   ✅ build-config.yaml já existe"
fi
echo ""

# ========================================
# PASSO 3: Verificar Dockerfile.prod
# ========================================
echo "3. Verificando Dockerfile.prod..."
if [ ! -f "Dockerfile.prod" ]; then
    echo "   ❌ Dockerfile.prod NÃO existe! Criando..."
    cat > Dockerfile.prod << 'EOF'
# Dockerfile para deploy no Google Cloud Run
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media /app/logs

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF
    echo "   ✅ Dockerfile.prod criado"
else
    echo "   ✅ Dockerfile.prod existe"
fi
echo ""

# ========================================
# PASSO 4: Rebuild sem cache
# ========================================
echo "4. Fazendo rebuild SEM CACHE (10-15 minutos)..."
echo "   Isso garante que TODAS as dependências sejam instaladas"
echo "   Por favor, aguarde..."
echo ""

gcloud builds submit \
    --config=build-config.yaml \
    --timeout=30m

if [ $? -eq 0 ]; then
    echo "   ✅ Build concluído com sucesso!"
else
    echo "   ❌ Erro no build! Verifique os logs acima."
    exit 1
fi
echo ""

# ========================================
# PASSO 5: Remover job antigo
# ========================================
echo "5. Removendo job antigo (se existir)..."
gcloud run jobs delete migrate-monpec --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
echo "   ✅ Job antigo removido"
echo ""

# ========================================
# PASSO 6: Criar novo job
# ========================================
echo "6. Criando novo job de migração..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create migrate-monpec \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 1 \
    --task-timeout 900 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

if [ $? -eq 0 ]; then
    echo "   ✅ Job criado com sucesso!"
else
    echo "   ❌ Erro ao criar job! Verifique os logs acima."
    exit 1
fi
echo ""

# ========================================
# PASSO 7: Executar migrações
# ========================================
echo "7. Executando migrações (aguarde 2-5 minutos)..."
echo ""

gcloud run jobs execute migrate-monpec --region $REGION --project $PROJECT_ID --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "   ✅ Migrações executadas!"
else
    echo ""
    echo "   ⚠️  Migrações podem ter falhado. Verificando..."
fi
echo ""

# ========================================
# PASSO 8: Verificar resultado
# ========================================
echo "8. Verificando resultado final..."
sleep 5

LATEST_EXECUTION=$(gcloud run jobs executions list --job migrate-monpec --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    MESSAGE=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].message)" 2>/dev/null || echo "")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "========================================"
        echo "  ✅✅✅ SUCESSO TOTAL! ✅✅✅"
        echo "========================================"
        echo ""
        echo "🎉 As migrações foram executadas com sucesso!"
        echo ""
        echo "Seu sistema está pronto e funcionando:"
        echo "  🌐 https://monpec-29862706245.us-central1.run.app"
        echo "  🌐 https://monpec-fzzfjppzva-uc.a.run.app"
        echo ""
        echo "Você pode acessar o sistema agora!"
        echo ""
    else
        echo ""
        echo "========================================"
        echo "  ⚠️  MIGRAÇÕES FALHARAM"
        echo "========================================"
        echo ""
        echo "Status: $STATUS"
        if [ -n "$MESSAGE" ]; then
            echo "Mensagem: $MESSAGE"
        fi
        echo ""
        echo "Verificando logs detalhados..."
        echo ""
        
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        echo "   Ver logs completos no console:"
        echo "   https://console.cloud.google.com/run/jobs/executions/details/us-central1/$LATEST_EXECUTION?project=$PROJECT_ID"
        echo ""
    fi
else
    echo ""
    echo "⚠️  Não foi possível verificar o status da execução"
    echo "   Verifique manualmente no console do Google Cloud"
fi

echo ""
echo "========================================"
echo "  PROCESSO CONCLUÍDO"
echo "========================================"
echo ""















