#!/bin/bash
# Script com todos os comandos para copiar e colar no Cloud Shell
# Use este arquivo como referência rápida

echo "========================================"
echo "COMANDOS PARA DEPLOY - GOOGLE CLOUD"
echo "========================================"
echo ""

# 1. Configurar projeto
echo "# 1. Configurar projeto"
echo "gcloud config set project monpec-sistema-rural"
echo ""

# 2. Build
echo "# 2. Build da imagem"
echo "gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest"
echo ""

# 3. Deploy
echo "# 3. Deploy no Cloud Run"
cat << 'EOF'
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
EOF
echo ""

# 4. Migrações
echo "# 4. Criar job de migração"
cat << 'EOF'
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600
EOF
echo ""

echo "# 5. Executar migrações"
echo "gcloud run jobs execute migrate-monpec --region us-central1 --wait"
echo ""

echo "# 6. Obter URL"
echo "gcloud run services describe monpec --region us-central1 --format=\"value(status.url)\""
echo ""

echo "# 7. Ver logs"
echo "gcloud run services logs read monpec --region us-central1 --limit=50"
echo ""

echo "========================================"
echo "Copie e cole cada comando no Cloud Shell"
echo "========================================"
















