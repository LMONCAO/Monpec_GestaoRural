#!/bin/bash

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "🔄 FORÇANDO ATUALIZAÇÃO COMPLETA - REMOVENDO CACHE"
echo "=================================================="
echo ""

gcloud config set project $PROJECT_ID

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: execute este script no diretório raiz do projeto (onde está manage.py)"
    exit 1
fi

echo "✅ Diretório correto detectado"
echo ""

# Limpar imagens antigas do registry para forçar novo build
echo "🧹 Limpando imagens antigas do registry..."
gcloud container images list-tags gcr.io/$PROJECT_ID/$SERVICE_NAME --limit=5 --format="value(digest)" | head -3 | while read digest; do
    if [ ! -z "$digest" ]; then
        echo "   Removendo imagem antiga: $digest"
        gcloud container images delete gcr.io/$PROJECT_ID/$SERVICE_NAME@$digest --quiet 2>/dev/null || true
    fi
done
echo "✅ Limpeza concluída"
echo ""

# 1. Atualizar middleware.py
echo "📝 1/6 Atualizando middleware.py..."
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
echo "✅ middleware.py atualizado"
echo ""

# 2. Corrigir settings_gcp.py
echo "📝 2/6 Corrigindo settings_gcp.py..."
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
    if "MIDDLEWARE.insert(common_index, middleware_path)" in content:
        print("✅ settings_gcp.py já está correto")
    else:
        # Tentar método alternativo
        pattern = r'(MIDDLEWARE\.insert\(0,\s*middleware_path\))'
        replacement = """try:
                    common_index = MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
                    MIDDLEWARE.insert(common_index, middleware_path)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"CloudRunHostMiddleware adicionado ANTES do CommonMiddleware")
                except ValueError:
                    MIDDLEWARE.insert(0, middleware_path)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"CloudRunHostMiddleware adicionado ao início do MIDDLEWARE")"""
        content = re.sub(pattern, replacement, content)
        with open('sistema_rural/settings_gcp.py', 'w') as f:
            f.write(content)
        print("✅ settings_gcp.py corrigido (método alternativo)")
PYEOF
echo ""

# 3. Garantir que requirements_producao.txt tem openpyxl
echo "📝 3/6 Verificando requirements_producao.txt..."
if ! grep -q "^openpyxl" requirements_producao.txt 2>/dev/null; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ openpyxl adicionado ao requirements_producao.txt"
else
    echo "✅ openpyxl já está no requirements_producao.txt"
fi
echo ""

# 4. Verificar Dockerfile.prod
echo "📝 4/6 Verificando Dockerfile.prod..."
if [ ! -f "Dockerfile.prod" ]; then
    echo "⚠️ Dockerfile.prod não encontrado, usando Dockerfile padrão"
else
    echo "✅ Dockerfile.prod encontrado"
fi
echo ""

# 5. Criar arquivo .dockerignore temporário para garantir que tudo seja copiado
echo "📝 5/6 Verificando .dockerignore..."
if [ -f ".dockerignore" ]; then
    echo "⚠️ .dockerignore existe, verificando se não está excluindo arquivos importantes..."
    if grep -q "^templates" .dockerignore 2>/dev/null; then
        echo "❌ AVISO: templates está sendo ignorado pelo .dockerignore!"
        echo "   Removendo templates do .dockerignore..."
        sed -i '/^templates/d' .dockerignore
        echo "✅ templates removido do .dockerignore"
    fi
else
    echo "✅ .dockerignore não existe ou não está excluindo arquivos importantes"
fi
echo ""

# 6. Build e deploy com timestamp único e sem cache
TIMESTAMP=$(date +%Y%m%d%H%M%S)
echo "📝 6/6 Buildando e fazendo deploy..."
echo "🔨 Buildando imagem Docker (timestamp: $TIMESTAMP)..."
echo "   Isso pode levar 5-10 minutos..."
echo "   Usando Dockerfile.prod..."

# Usar Dockerfile.prod explicitamente
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --config=cloudbuild.yaml 2>/dev/null || \
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP -f Dockerfile.prod .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build concluído com sucesso!"
    echo ""
    echo "🚀 Fazendo deploy da nova versão..."
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
        echo "🌐 URL do domínio: https://monpec.com.br"
        echo ""
        echo "⏳ IMPORTANTE:"
        echo "   1. Aguarde 30-60 segundos para o serviço inicializar completamente"
        echo "   2. Limpe o cache do navegador (Ctrl+Shift+Delete) ou use modo anônimo"
        echo "   3. Se ainda aparecer versão antiga, force refresh (Ctrl+F5)"
        echo ""
    else
        echo "❌ Erro no deploy"
        exit 1
    fi
else
    echo "❌ Erro no build"
    exit 1
fi



