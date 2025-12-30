#!/bin/bash
# Criar admin usando um script Python temporário
# Execute: bash CRIAR_ADMIN_COM_SCRIPT_PYTHON.sh

echo "=== CRIAR ADMIN COM SCRIPT PYTHON ==="
echo ""

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Criar script Python temporário
cat > /tmp/create_admin.py <<'PYTHON'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth.models import User

# Criar ou atualizar admin
username = 'admin'
password = 'L6171r12@@'
email = 'admin@example.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.email = email
    user.save()
    print(f'✅ Usuário {username} atualizado com sucesso!')
except User.DoesNotExist:
    user = User.objects.create_superuser(username, email, password)
    print(f'✅ Usuário {username} criado com sucesso!')
except Exception as e:
    print(f'❌ Erro: {e}')
    exit(1)
PYTHON

# Criar job que executa o script
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

echo "Criando job que executa o script Python..."
gcloud run jobs delete create-admin-script --region=us-central1 --quiet 2>/dev/null || true

gcloud run jobs create create-admin-script \
  --region=us-central1 \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="/tmp/create_admin.py" \
  --memory=2Gi \
  --cpu=2

# Mas o script não vai estar no container... vamos usar outra abordagem
echo ""
echo "⚠️ O script não estará no container. Usando comando inline..."
echo ""

# Deletar e recriar com comando inline
gcloud run jobs delete create-admin-script --region=us-central1 --quiet 2>/dev/null || true

gcloud run jobs create create-admin-inline \
  --region=us-central1 \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.contrib.auth.models import User; u, c = User.objects.get_or_create(username='admin'); u.set_password('L6171r12@@'); u.is_superuser = True; u.is_staff = True; u.email = 'admin@example.com'; u.save(); print('OK' if c else 'Updated')" \
  --memory=2Gi \
  --cpu=2

echo ""
echo "Executando job..."
gcloud run jobs execute create-admin-inline --region=us-central1 --wait

echo ""
echo "✅ Tente fazer login agora com usuário: admin, senha: L6171r12@@"

