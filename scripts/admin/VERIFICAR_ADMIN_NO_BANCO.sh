#!/bin/bash
# Script para verificar se o admin existe no banco

echo "🔍 Verificando admin no banco de dados"
echo "======================================="
echo ""

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)

# Criar script Python para verificar
cat > /tmp/verificar_admin.py << 'PYTHON_SCRIPT'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print("=" * 60)
print("VERIFICANDO USUÁRIOS NO BANCO")
print("=" * 60)
print()

total_users = User.objects.count()
print(f"Total de usuários: {total_users}")
print()

if total_users > 0:
    print("Usuários encontrados:")
    for u in User.objects.all():
        print(f"  - Username: {u.username}")
        print(f"    Email: {u.email}")
        print(f"    Ativo: {u.is_active}")
        print(f"    Superuser: {u.is_superuser}")
        print(f"    Staff: {u.is_staff}")
        print()
else:
    print("❌ Nenhum usuário encontrado no banco!")
    print()

# Verificar especificamente o admin
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print("✅ Usuário 'admin' encontrado:")
    print(f"   Email: {admin_user.email}")
    print(f"   Ativo: {admin_user.is_active}")
    print(f"   Superuser: {admin_user.is_superuser}")
    print(f"   Staff: {admin_user.is_staff}")
else:
    print("❌ Usuário 'admin' NÃO encontrado!")
PYTHON_SCRIPT

echo "▶ Criando job para verificar banco..."
gcloud run jobs create verificar-admin \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args /tmp/verificar_admin.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp-key" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo ""
echo "▶ Executando verificação..."
gcloud run jobs execute verificar-admin --region us-central1 --wait

echo ""
echo "🧹 Limpando..."
gcloud run jobs delete verificar-admin --region us-central1 --quiet 2>&1 || true








