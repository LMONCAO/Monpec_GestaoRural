#!/bin/bash
# Script para criar superusuário no Django via Cloud Run Job

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Criando superusuário no Django${NC}"
echo ""

# Obter projeto
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo "Projeto: $PROJECT_ID"
echo ""

# Solicitar informações
read -p "Username: " USERNAME
read -sp "Email: " EMAIL
echo ""
read -sp "Password: " PASSWORD
echo ""
read -sp "SECRET_KEY do Django: " SECRET_KEY
echo ""
read -p "DB_NAME [monpec_db]: " DB_NAME
DB_NAME=${DB_NAME:-monpec_db}
read -p "DB_USER [monpec_user]: " DB_USER
DB_USER=${DB_USER:-monpec_user}
read -sp "DB_PASSWORD: " DB_PASSWORD
echo ""
read -p "CLOUD_SQL_CONNECTION_NAME (formato: PROJECT_ID:REGION:INSTANCE_NAME): " CLOUD_SQL_CONNECTION_NAME

echo ""
echo -e "${YELLOW}Criando script Python temporário...${NC}"

# Criar script Python para criar superusuário
cat > /tmp/create_superuser.py << EOF
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='$USERNAME').exists():
    User.objects.create_superuser('$USERNAME', '$EMAIL', '$PASSWORD')
    print(f'Superusuário $USERNAME criado com sucesso!')
else:
    print(f'Superusuário $USERNAME já existe!')
EOF

echo -e "${YELLOW}Criando job...${NC}"

# Criar job temporário
gcloud run jobs create create-superuser-temp \
  --image=gcr.io/$PROJECT_ID/monpec:latest \
  --region=us-central1 \
  --command=python \
  --args=manage.py,shell \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --set-env-vars="SECRET_KEY=$SECRET_KEY" \
  --set-env-vars="DB_NAME=$DB_NAME" \
  --set-env-vars="DB_USER=$DB_USER" \
  --set-env-vars="DB_PASSWORD=$DB_PASSWORD" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-env-vars="PYTHONUNBUFFERED=1" \
  --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --max-retries=1 \
  --task-timeout=300

echo ""
echo -e "${YELLOW}Executando criação de superusuário...${NC}"
echo -e "${YELLOW}NOTA: Este método pode não funcionar perfeitamente.${NC}"
echo -e "${YELLOW}Recomenda-se criar o superusuário manualmente após o deploy.${NC}"
echo ""

# Alternativa: usar createsuperuser com --noinput
gcloud run jobs update create-superuser-temp \
  --args=manage.py,createsuperuser,--noinput \
  --set-env-vars="DJANGO_SUPERUSER_USERNAME=$USERNAME" \
  --set-env-vars="DJANGO_SUPERUSER_EMAIL=$EMAIL" \
  --set-env-vars="DJANGO_SUPERUSER_PASSWORD=$PASSWORD"

gcloud run jobs execute create-superuser-temp --region=us-central1 --wait

echo ""
echo -e "${GREEN}Processo concluído!${NC}"
echo ""
echo "Se não funcionou, você pode criar o superusuário manualmente:"
echo "1. Acesse o Cloud Shell"
echo "2. Execute: gcloud run jobs execute create-superuser-temp --region=us-central1"
echo "3. Ou conecte-se ao banco e crie via Django admin após o deploy"

