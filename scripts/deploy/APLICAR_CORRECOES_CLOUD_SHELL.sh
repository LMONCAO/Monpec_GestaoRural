#!/bin/bash

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "🔧 Aplicando correções no Cloud Shell..."

gcloud config set project $PROJECT_ID

# 1. Atualizar middleware.py com process_request
echo "📝 Atualizando middleware.py..."
cat > sistema_rural/middleware.py << 'EOF'
"""
Middleware customizado para permitir hosts do Cloud Run dinamicamente.
"""
from django.conf import settings
from django.core.exceptions import DisallowedHost
import logging

logger = logging.getLogger(__name__)


class CloudRunHostMiddleware:
    """
    Middleware para permitir hosts do Cloud Run dinamicamente.
    Cloud Run URLs têm formato: SERVICE-PROJECT_HASH-REGION.a.run.app
    
    Este middleware deve ser o PRIMEIRO na lista de middlewares para interceptar
    antes da validação padrão do Django.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Processa a requisição ANTES de qualquer outro middleware.
        Isso garante que o host seja adicionado ao ALLOWED_HOSTS antes
        do CommonMiddleware validar.
        """
        # CRÍTICO: Não usar request.get_host() aqui pois ele já valida ALLOWED_HOSTS
        # Obter host diretamente do header HTTP ANTES de qualquer validação
        host = request.META.get('HTTP_HOST', '').split(':')[0]  # Remove porta se houver
        
        # Se não tiver HTTP_HOST, tentar SERVER_NAME
        if not host:
            host = request.META.get('SERVER_NAME', '')
        
        # Se for um host do Cloud Run (qualquer formato), adicionar ao ALLOWED_HOSTS
        if host:
            # Verificar se é um host do Cloud Run
            is_cloud_run = host.endswith('.run.app') or host.endswith('.a.run.app')
            
            # Se for Cloud Run ou localhost, adicionar ao ALLOWED_HOSTS
            if is_cloud_run or host in ['localhost', '127.0.0.1', '0.0.0.0']:
                # Adicionar ao ALLOWED_HOSTS se não estiver lá
                if host not in settings.ALLOWED_HOSTS:
                    # Modificar a lista diretamente
                    if isinstance(settings.ALLOWED_HOSTS, list):
                        settings.ALLOWED_HOSTS.append(host)
                        logger.info(f"✅ Adicionado host ao ALLOWED_HOSTS: {host}")
                    # Se for uma tupla ou outro tipo, converter para lista
                    elif hasattr(settings.ALLOWED_HOSTS, '__iter__'):
                        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
                        logger.info(f"✅ Adicionado host ao ALLOWED_HOSTS: {host}")
        
        # Retornar None para continuar o processamento normal
        return None

    def __call__(self, request):
        # Chamar process_request primeiro
        response = self.process_request(request)
        if response is not None:
            return response
        
        # Processar a requisição normalmente
        try:
            response = self.get_response(request)
            return response
        except DisallowedHost as e:
            # Se ainda assim der erro, tentar adicionar o host novamente
            host = request.META.get('HTTP_HOST', '').split(':')[0]
            if host and host not in settings.ALLOWED_HOSTS:
                if isinstance(settings.ALLOWED_HOSTS, list):
                    settings.ALLOWED_HOSTS.append(host)
                    logger.warning(f"⚠️ Host bloqueado, adicionando ao ALLOWED_HOSTS: {host}")
                    # Tentar novamente
                    try:
                        response = self.get_response(request)
                        return response
                    except DisallowedHost:
                        logger.error(f"❌ Falha ao processar host: {host}")
                        raise
            raise
EOF

# 2. Corrigir settings_gcp.py para inserir middleware ANTES do CommonMiddleware
echo "📝 Corrigindo settings_gcp.py..."
python3 << 'PYEOF'
import re

with open('sistema_rural/settings_gcp.py', 'r') as f:
    content = f.read()

# Substituir a lógica de inserção do middleware
old_code = """                # Inserir no início, antes de TODOS os outros middlewares
                MIDDLEWARE.insert(0, middleware_path)"""

new_code = """                # Tentar inserir ANTES do CommonMiddleware
                try:
                    common_index = MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
                    MIDDLEWARE.insert(common_index, middleware_path)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"CloudRunHostMiddleware adicionado ANTES do CommonMiddleware")
                except ValueError:
                    # Se não encontrar CommonMiddleware, inserir no início
                    MIDDLEWARE.insert(0, middleware_path)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"CloudRunHostMiddleware adicionado ao início do MIDDLEWARE")"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('sistema_rural/settings_gcp.py', 'w') as f:
        f.write(content)
    print("✅ settings_gcp.py corrigido")
else:
    # Verificar se já está correto
    if "MIDDLEWARE.insert(common_index, middleware_path)" in content:
        print("✅ settings_gcp.py já está correto")
    else:
        print("⚠️ Não foi possível encontrar o padrão para substituir")
        print("Verificando estrutura do arquivo...")
PYEOF

# 3. Verificar se há outros arquivos que precisam ser atualizados
echo "🔍 Verificando outros arquivos..."

# Garantir que requirements_producao.txt tem openpyxl
if ! grep -q "^openpyxl" requirements_producao.txt 2>/dev/null; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ openpyxl adicionado ao requirements_producao.txt"
fi

# 4. Build e deploy
TIMESTAMP=$(date +%Y%m%d%H%M%S)
echo "🔨 Buildando imagem Docker (aguarde, pode levar alguns minutos)..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP

if [ $? -eq 0 ]; then
    echo "✅ Build concluído!"
    echo "🚀 Fazendo deploy..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP \
        --region=$REGION \
        --platform managed \
        --allow-unauthenticated \
        --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅"
        echo ""
        echo "🌐 URL do serviço: https://monpec-29862706245.us-central1.run.app"
        echo ""
        echo "Aguarde alguns segundos e teste o acesso."
    else
        echo "❌ Erro no deploy"
        exit 1
    fi
else
    echo "❌ Erro no build"
    exit 1
fi




