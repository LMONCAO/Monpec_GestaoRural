#!/bin/bash
# Script para executar migrate e collectstatic usando Cloud Run Jobs
# Execute: bash executar_com_cloud_run_jobs.sh

# Não usar set -e porque queremos tratar erros manualmente

echo "=== EXECUTAR MIGRATE E COLECTSTATIC COM CLOUD RUN JOBS ==="
echo ""
echo "Este método é mais confiável que gcloud builds submit!"
echo ""

# Configurar projeto
echo "1️⃣ Configurando projeto..."
gcloud config set project monpec-sistema-rural
echo "✅ Projeto configurado"
echo ""

# Verificar qual imagem usar
echo "2️⃣ Verificando imagens disponíveis..."
IMAGES=$(gcloud container images list --repository=gcr.io/monpec-sistema-rural --format="value(name)" 2>/dev/null | head -1)

if echo "$IMAGES" | grep -q "monpec"; then
    IMAGE_NAME="gcr.io/monpec-sistema-rural/monpec:latest"
    echo "✅ Usando imagem: $IMAGE_NAME"
elif echo "$IMAGES" | grep -q "sistema-rural"; then
    IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"
    echo "✅ Usando imagem: $IMAGE_NAME"
else
    echo "⚠️ Não foi possível detectar a imagem automaticamente."
    echo "Usando: gcr.io/monpec-sistema-rural/sistema-rural:latest"
    IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"
fi
echo ""

# Criar ou atualizar job para migrate + collectstatic
echo "3️⃣ Criando/atualizando Cloud Run Job para migrate + collectstatic..."

# Tentar criar primeiro, se já existir, atualizar
gcloud run jobs describe migrate-collectstatic --region=us-central1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Job já existe, atualizando..."
    gcloud run jobs update migrate-collectstatic \
      --region=us-central1 \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="sh" \
      --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
      --memory=2Gi \
      --cpu=2
else
    echo "Criando novo job..."
    gcloud run jobs create migrate-collectstatic \
      --image="$IMAGE_NAME" \
      --region=us-central1 \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="sh" \
      --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2
fi

echo "✅ Job criado/atualizado"
echo ""

# Executar o job
echo "4️⃣ Executando migrate e collectstatic..."
echo "⏱️ Isso pode levar 3-5 minutos..."
echo ""
echo "⚠️ Se aparecer erro de autenticação, o comando geralmente funciona mesmo assim no Cloud Shell..."
echo ""
gcloud run jobs execute migrate-collectstatic --region=us-central1 --wait || {
    echo ""
    echo "⚠️ Erro ao executar job. Tentando verificar se o job existe..."
    gcloud run jobs describe migrate-collectstatic --region=us-central1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Job existe. O erro pode ser temporário."
        echo "Tente executar manualmente:"
        echo "  gcloud run jobs execute migrate-collectstatic --region=us-central1 --wait"
        exit 1
    else
        echo "❌ Job não foi criado corretamente."
        exit 1
    fi
}

echo ""
echo "✅✅✅ MIGRATE E COLECTSTATIC CONCLUÍDOS! ✅✅✅"
echo ""

# Criar job para criar admin
echo "5️⃣ Criando/atualizando Cloud Run Job para criar usuário admin..."

# Tentar criar primeiro, se já existir, atualizar
gcloud run jobs describe create-admin --region=us-central1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Job já existe, atualizando..."
    gcloud run jobs update create-admin \
      --region=us-central1 \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
      --memory=2Gi \
      --cpu=2
else
    echo "Criando novo job..."
    gcloud run jobs create create-admin \
      --image="$IMAGE_NAME" \
      --region=us-central1 \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2
fi

echo "✅ Job criado/atualizado"
echo ""

# Executar job para criar admin
echo "6️⃣ Criando usuário admin..."
echo "⏱️ Isso pode levar 1-2 minutos..."
echo ""
echo "⚠️ Se aparecer erro de autenticação, o comando geralmente funciona mesmo assim no Cloud Shell..."
echo ""
gcloud run jobs execute create-admin --region=us-central1 --wait || {
    echo ""
    echo "⚠️ Erro ao executar job. Tentando verificar se o job existe..."
    gcloud run jobs describe create-admin --region=us-central1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Job existe. O erro pode ser temporário."
        echo "Tente executar manualmente:"
        echo "  gcloud run jobs execute create-admin --region=us-central1 --wait"
        exit 1
    else
        echo "❌ Job não foi criado corretamente."
        exit 1
    fi
}

echo ""
echo "✅✅✅ TUDO CONCLUÍDO COM SUCESSO! ✅✅✅"
echo ""
echo "Agora você pode:"
echo "- Acessar o sistema na URL do Cloud Run"
echo "- Fazer login com:"
echo "  Usuário: admin"
echo "  Senha: L6171r12@@"
echo ""
echo "💡 Os jobs foram criados e podem ser reutilizados no futuro."
echo "   Para executar novamente:"
echo "   - Migrate/Collectstatic: gcloud run jobs execute migrate-collectstatic --region=us-central1 --wait"
echo "   - Criar Admin: gcloud run jobs execute create-admin --region=us-central1 --wait"

