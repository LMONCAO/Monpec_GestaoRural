#!/bin/bash
# Script para corrigir openpyxl e fazer deploy AGORA

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔧 CORRIGINDO OPENPYXL E DEPLOY"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Corrigindo views_relatorios_rastreabilidade.py..."
if [ -f "gestao_rural/views_relatorios_rastreabilidade.py" ]; then
    # Verificar se ainda tem imports no topo
    if head -25 gestao_rural/views_relatorios_rastreabilidade.py | grep -qE "^from openpyxl|^import openpyxl"; then
        echo "❌ Ainda tem imports no topo. Corrigindo..."
        cp gestao_rural/views_relatorios_rastreabilidade.py gestao_rural/views_relatorios_rastreabilidade.py.bak
        
        # Remover imports do topo (linhas 19-21 aproximadamente)
        sed -i '/^from openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
        sed -i '/^import openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
        
        # Adicionar comentário sobre lazy imports
        sed -i '19i# Importação lazy de openpyxl para evitar erro se não estiver instalado\n# Será importado dentro das funções quando necessário' gestao_rural/views_relatorios_rastreabilidade.py
        
        echo "✅ Corrigido"
    else
        echo "✅ Já está correto"
    fi
fi

echo ""
echo "2️⃣ Adicionando lazy imports nas funções..."
# Adicionar lazy imports nas 4 funções que usam openpyxl
python3 << 'PYTHON_SCRIPT'
import re

file_path = "gestao_rural/views_relatorios_rastreabilidade.py"
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Funções que precisam de lazy imports
    functions = [
        'exportar_anexo_i_excel',
        'exportar_anexo_ii_excel', 
        'exportar_anexo_iii_excel',
        'exportar_anexo_iv_excel'
    ]
    
    modified = False
    for func_name in functions:
        # Padrão para encontrar a função
        pattern = rf'(@login_required\s+def {func_name}\([^)]+\):.*?"""[^"]*""")'
        
        # Verificar se já tem try/except
        func_pattern = rf'def {func_name}\([^)]+\):'
        if re.search(func_pattern, content):
            func_match = re.search(func_pattern, content)
            func_start = func_match.start()
            # Verificar se já tem try logo após
            next_lines = content[func_start:func_start+500]
            if 'try:' in next_lines and 'from openpyxl' in next_lines:
                continue  # Já tem lazy import
            
            # Adicionar lazy import
            replacement = rf'\1\n    try:\n        from openpyxl import Workbook\n        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side\n    except ImportError:\n        from django.contrib import messages\n        messages.error(request, '\''Biblioteca openpyxl não está instalada. Execute: pip install openpyxl'\'')\n        from django.shortcuts import redirect\n        return redirect('\''rastreabilidade_dashboard'\'', propriedade_id=propriedade_id)\n    '
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Lazy imports adicionados nas funções")
    else:
        print("✅ Lazy imports já estão presentes")
except Exception as e:
    print(f"⚠️ Erro ao adicionar lazy imports: {e}")
    print("   Continuando mesmo assim...")
PYTHON_SCRIPT

echo ""
echo "3️⃣ Garantindo requirements_producao.txt..."
if [ ! -f "requirements_producao.txt" ] || ! grep -qE "^openpyxl" requirements_producao.txt; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ Adicionado openpyxl"
fi

echo ""
echo "4️⃣ Fazendo build..."
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
echo "Buildando: $IMAGE_TAG"
gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído"
    gcloud container images add-tag $IMAGE_TAG gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet
    echo "✅ Tag 'latest' atualizada"
else
    echo "❌ Erro no build"
    exit 1
fi

echo ""
echo "5️⃣ Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "6️⃣ Testando..."
sleep 30
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "301" ] && [ "$HTTP_CODE" != "302" ]; then
    echo ""
    echo "Verificando logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -100
fi

echo ""
echo "✅ Processo concluído!"





