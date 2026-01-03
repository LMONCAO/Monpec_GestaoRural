#!/bin/bash
# Solução corrigida: usar arquivo Python ao invés de comando inline

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando estado completo (usando arquivo Python)..."

# Verificar usando arquivo Python
gcloud run jobs create check-full-status-fixed \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args verificar_estado_migracao.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

STATUS_OUTPUT=$(gcloud run jobs execute check-full-status-fixed --region us-central1 --wait 2>&1)
echo "$STATUS_OUTPUT" | tail -30
gcloud run jobs delete check-full-status-fixed --region us-central1 --quiet 2>&1 || true

# Se a migração está registrada mas a tabela não existe, remover o registro e reaplicar
if echo "$STATUS_OUTPUT" | grep -q "PROBLEMA"; then
    echo ""
    echo "▶ Removendo registro da migração 0071 para reaplicar..."
    
    # Criar script para remover registro
    cat > /tmp/remove_migration_71.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';")
print('✅ Registro da migração 0071 removido')
EOF
    
    gcloud run jobs create remove-migration-71 \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args -c,"import os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');import django;django.setup();from django.db import connection;c=connection.cursor();c.execute(\"DELETE FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal'\");print('OK')" \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 300 \
      --memory 512Mi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    gcloud run jobs execute remove-migration-71 --region us-central1 --wait 2>&1 | tail -10
    gcloud run jobs delete remove-migration-71 --region us-central1 --quiet 2>&1 || true
    
    echo ""
    echo "▶ Reaplicando migração 0071..."
    
    gcloud run jobs create reapply-0071 \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args manage.py,migrate,gestao_rural,0071_adicionar_produtos_cadastro_fiscal,--verbosity=2 \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 600 \
      --memory 1Gi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    REAPPLY_OUTPUT=$(gcloud run jobs execute reapply-0071 --region us-central1 --wait 2>&1)
    echo "$REAPPLY_OUTPUT" | tail -100
    gcloud run jobs delete reapply-0071 --region us-central1 --quiet 2>&1 || true
fi

echo ""
echo "▶ Executando todas as migrações restantes..."

gcloud run jobs create run-all-remaining-migrations \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,--noinput \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 900 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

MIG_ALL_OUTPUT=$(gcloud run jobs execute run-all-remaining-migrations --region us-central1 --wait 2>&1)
echo "$MIG_ALL_OUTPUT" | tail -100
gcloud run jobs delete run-all-remaining-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Criando admin..."

gcloud run jobs create create-admin-final \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

ADMIN_OUTPUT=$(gcloud run jobs execute create-admin-final --region us-central1 --wait 2>&1)
echo "$ADMIN_OUTPUT" | tail -30
gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TUDO CONCLUÍDO! ✅✅✅"
echo ""
echo "🔐 CREDENCIAIS:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








