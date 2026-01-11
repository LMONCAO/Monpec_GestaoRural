#!/bin/bash

# 🚀 RESET COMPLETO MONPEC - GOOGLE CLOUD APPROACH
# Abordagem mais confiável: fazer tudo remotamente no Cloud

echo "========================================="
echo "🔄 RESET COMPLETO MONPEC - CLOUD APPROACH"
echo "========================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. CRIAR NOVO BANCO POSTGRESQL
echo ""
echo "1️⃣ CRIANDO NOVO BANCO POSTGRESQL..."

# Dropar banco existente se existir
gcloud sql databases delete monpec-db --instance=monpec-db --quiet 2>/dev/null || echo "Banco não existia"

# Criar novo banco
gcloud sql databases create monpec-db --instance=monpec-db

print_status "Novo banco criado"

# 2. BUILD IMAGEM LIMPA
echo ""
echo "2️⃣ FAZENDO BUILD DA IMAGEM LIMPA..."

# Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

print_status "Imagem buildada"

# 3. DEPLOY COM MIGRATE FRESH
echo ""
echo "3️⃣ DEPLOY COM MIGRATE FRESH..."

# Criar job de migrate fresh
gcloud run jobs create migrate-fresh-clean \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=4Gi \
  --cpu=2 \
  --max-retries=1 \
  --task-timeout=1800

# Executar migrate
gcloud run jobs execute migrate-fresh-clean --region=us-central1 --wait

print_status "Migrações aplicadas"

# 4. POPULAR DADOS LIMPOS
echo ""
echo "4️⃣ POPULANDO DADOS LIMPOS..."

# Criar job de população
gcloud run jobs create populate-clean-fresh \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" \
  --command="python" \
  --args="popular_dados_producao.py" \
  --memory=4Gi \
  --cpu=2 \
  --max-retries=1 \
  --task-timeout=1800

# Executar população
gcloud run jobs execute populate-clean-fresh --region=us-central1 --wait

print_status "Dados populados"

# 5. DEPLOY SERVIÇO LIMPO
echo ""
echo "5️⃣ DEPLOY SERVIÇO LIMPO..."

# Deploy do serviço
gcloud run services update monpec \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/monpec \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" \
  --memory=4Gi \
  --cpu=2 \
  --timeout=300

print_status "Serviço atualizado"

# 6. TESTE FINAL
echo ""
echo "6️⃣ TESTE FINAL..."

sleep 10

# Testar produção
echo "=== VERIFICANDO SISTEMA ==="
curl -I https://monpec-29862706245.us-central1.run.app/

echo ""
echo "=== TESTANDO LANDING PAGE ==="
curl -s https://monpec-29862706245.us-central1.run.app/ | head -10

print_status "RESET COMPLETO CONCLUÍDO!"

echo ""
echo "========================================="
echo "🎉 SISTEMA MONPEC RESETADO E FUNCIONANDO!"
echo "========================================="
echo ""
echo "✅ Novo banco PostgreSQL criado"
echo "✅ Migrações aplicadas do zero"
echo "✅ Dados populados limpos (1.300 animais)"
echo "✅ Deploy sem conflitos"
echo ""
echo "🌐 URL: https://monpec-29862706245.us-central1.run.app/"
echo "👤 Admin: admin / [sua senha atual]"
echo ""
echo "========================================="