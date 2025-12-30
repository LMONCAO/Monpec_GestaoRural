#!/bin/bash
# Script para executar AGORA no Cloud Shell
# Copie e cole cada seção no terminal do Cloud Shell

echo "========================================"
echo "DEPLOY MONPEC - GOOGLE CLOUD"
echo "========================================"
echo ""

# 1. Configurar projeto
echo "1. Configurando projeto..."
gcloud config set project monpec-sistema-rural
echo "✓ Projeto configurado"
echo ""

# 2. Verificar se estamos no diretório correto
echo "2. Verificando diretório..."
if [ ! -f "manage.py" ]; then
    echo "⚠ ATENÇÃO: manage.py não encontrado!"
    echo "Você precisa fazer upload dos arquivos do projeto primeiro."
    echo ""
    echo "Opções:"
    echo "  A) Use o botão de upload no Cloud Shell Editor"
    echo "  B) Use git clone se o projeto estiver no Git"
    echo "  C) Use gsutil para fazer upload de um ZIP"
    echo ""
    read -p "Pressione Enter quando os arquivos estiverem no Cloud Shell..."
fi
echo ""

# 3. Verificar arquivos essenciais
echo "3. Verificando arquivos essenciais..."
files_ok=true
[ ! -f "Dockerfile.prod" ] && [ ! -f "Dockerfile" ] && { echo "✗ Dockerfile não encontrado"; files_ok=false; }
[ ! -f "requirements.txt" ] && { echo "✗ requirements.txt não encontrado"; files_ok=false; }
[ ! -f "manage.py" ] && { echo "✗ manage.py não encontrado"; files_ok=false; }
[ ! -f "sistema_rural/settings_gcp.py" ] && { echo "✗ settings_gcp.py não encontrado"; files_ok=false; }

if [ "$files_ok" = false ]; then
    echo ""
    echo "❌ Alguns arquivos estão faltando. Faça upload do projeto primeiro!"
    exit 1
fi
echo "✓ Todos os arquivos essenciais encontrados"
echo ""

# 4. Build da imagem
echo "4. Fazendo build da imagem Docker..."
echo "⏱️  Isso pode levar 5-10 minutos..."
echo ""
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro no build!"
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

echo ""
echo "✓ Build concluído com sucesso!"
echo ""

# 5. Deploy no Cloud Run
echo "5. Fazendo deploy no Cloud Run..."
echo "⏱️  Isso pode levar 2-3 minutos..."
echo ""

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

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro no deploy!"
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

echo ""
echo "✓ Deploy concluído com sucesso!"
echo ""

# 6. Obter URL
echo "6. Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format="value(status.url)")
echo ""
echo "========================================"
echo "✅ DEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "🌐 URL do serviço:"
echo "   $SERVICE_URL"
echo ""

# 7. Criar job de migração
echo "7. Criando job de migração..."
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    2>/dev/null || echo "Job já existe, continuando..."

# 8. Executar migrações
echo ""
echo "8. Aplicando migrações do banco de dados..."
echo "⏱️  Isso pode levar 1-2 minutos..."
echo ""
gcloud run jobs execute migrate-monpec --region us-central1 --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Migrações aplicadas com sucesso!"
else
    echo ""
    echo "⚠ Erro ao aplicar migrações. Verifique os logs."
fi

echo ""
echo "========================================"
echo "🎉 TUDO PRONTO!"
echo "========================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Teste o sistema:"
echo "   Abra no navegador: $SERVICE_URL"
echo ""
echo "2. Ver logs (se necessário):"
echo "   gcloud run services logs read monpec --region us-central1 --limit=50"
echo ""
echo "3. Configurar domínio (opcional):"
echo "   gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1"
echo ""
echo "========================================"
















