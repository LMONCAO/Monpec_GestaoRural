#!/bin/bash
# Criar usuário admin manualmente via Cloud Run Job
# Execute: bash CRIAR_ADMIN_MANUALMENTE.sh

echo "=== CRIAR USUÁRIO ADMIN MANUALMENTE ==="
echo ""

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Verificar qual imagem usar
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

echo "Tentando criar usuário admin de forma mais simples..."
echo ""

# Tentar atualizar o job existente com comando mais simples
echo "Atualizando job create-admin com comando corrigido..."
gcloud run jobs update create-admin \
  --region=us-central1 \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,createsuperuser,--noinput,--username,admin,--email,admin@example.com" \
  --memory=2Gi \
  --cpu=2

echo ""
echo "⚠️ O comando acima não funciona porque precisa de senha interativa."
echo ""
echo "💡 SOLUÇÃO: Vamos usar um comando Python inline mais robusto..."
echo ""

# Deletar job antigo e criar novo
echo "Deletando job antigo..."
gcloud run jobs delete create-admin --region=us-central1 --quiet 2>/dev/null || true

echo "Criando novo job com comando Python inline..."
gcloud run jobs create create-admin-v2 \
  --region=us-central1 \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,shell" \
  --args="--command=import os; from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='admin'); u.set_password('L6171r12@@'); u.is_superuser = True; u.is_staff = True; u.email = 'admin@example.com'; u.save(); print('Admin criado!' if created else 'Admin atualizado!')" \
  --memory=2Gi \
  --cpu=2

echo ""
echo "✅ Job criado! Executando..."
echo ""
gcloud run jobs execute create-admin-v2 --region=us-central1 --wait

echo ""
echo "✅✅✅ TENTATIVA CONCLUÍDA! ✅✅✅"
echo ""
echo "Se ainda não funcionar, veja a próxima solução no arquivo COMANDOS_PARA_GOOGLE_CLOUD_SHELL.md"

