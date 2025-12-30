#!/bin/bash
# Criar admin diretamente no serviço Cloud Run
# Este método executa o script dentro do container do serviço ativo

echo "🔐 Criando admin diretamente no serviço Cloud Run"
echo "=================================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

echo "Connection: $CONNECTION_NAME"
echo ""

# Criar script Python inline
SCRIPT_PYTHON='import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_rural.settings_gcp")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = "admin"
email = "admin@monpec.com.br"
password = "L6171r12@@"
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
    print(f"Usuário: {username}")
    print(f"Senha: {password}")
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)'

# Salvar script temporariamente
echo "$SCRIPT_PYTHON" > /tmp/criar_admin_temp.py

# Criar job temporário usando a mesma imagem do serviço
echo "▶ Criando job temporário..."
gcloud run jobs create create-admin-direto \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --command python \
  --args -c,"$SCRIPT_PYTHON" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp-key" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo ""
echo "▶ Executando job..."
gcloud run jobs execute create-admin-direto --region $REGION --wait

echo ""
echo "✅ Verifique o resultado acima!"
echo ""
echo "🧹 Limpando job temporário..."
gcloud run jobs delete create-admin-direto --region $REGION --quiet 2>&1 || true








