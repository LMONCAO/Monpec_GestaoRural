#!/bin/bash
# Script completo para verificar e corrigir o problema do admin

echo "🔍 VERIFICAÇÃO COMPLETA - ADMIN"
echo "================================="
echo ""

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)

echo "Connection: $CONNECTION_NAME"
echo "Project: $PROJECT_ID"
echo ""

# 1. Verificar se o admin existe no banco
echo "▶ 1. Verificando se admin existe no banco..."
cat > /tmp/verificar_admin.py << 'EOF'
import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"✅ Admin encontrado: {admin.username} - Active: {admin.is_active} - Superuser: {admin.is_superuser}")
    print(f"   Email: {admin.email}")
else:
    print("❌ Admin NÃO encontrado no banco!")
    sys.exit(1)
EOF

gcloud run jobs create verificar-admin-temp \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args /tmp/verificar_admin.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute verificar-admin-temp --region us-central1 --wait
gcloud run jobs delete verificar-admin-temp --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ 2. Criando/atualizando admin com script garantido..."
cat > /tmp/criar_admin_garantido.py << 'EOF'
import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'
try:
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_superuser = True
        u.is_staff = True
        u.is_active = True
        u.email = email
        u.save()
        print(f"✅ Admin ATUALIZADO: {username}")
    else:
        User.objects.create_superuser(username, email, password)
        print(f"✅ Admin CRIADO: {username}")
    u = User.objects.get(username=username)
    print(f"Usuário: {u.username}")
    print(f"Email: {u.email}")
    print(f"Ativo: {u.is_active}")
    print(f"Superuser: {u.is_superuser}")
    print(f"Staff: {u.is_staff}")
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

gcloud run jobs create criar-admin-garantido \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args /tmp/criar_admin_garantido.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute criar-admin-garantido --region us-central1 --wait
gcloud run jobs delete criar-admin-garantido --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Processo concluído!"
echo ""
echo "🌐 Teste o login em: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"








