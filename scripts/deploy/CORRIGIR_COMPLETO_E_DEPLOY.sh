#!/bin/bash
# Script completo para corrigir openpyxl e fazer deploy

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔧 CORREÇÃO COMPLETA OPENPYXL + DEPLOY"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Corrigindo views_relatorios_rastreabilidade.py..."
if [ -f "gestao_rural/views_relatorios_rastreabilidade.py" ]; then
    # Backup
    cp gestao_rural/views_relatorios_rastreabilidade.py gestao_rural/views_relatorios_rastreabilidade.py.bak
    
    # Remover imports do topo
    sed -i '/^from openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    sed -i '/^import openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    
    # Adicionar comentário sobre lazy imports (se não existir)
    if ! grep -q "Importação lazy de openpyxl" gestao_rural/views_relatorios_rastreabilidade.py; then
        sed -i '19i# Importação lazy de openpyxl para evitar erro se não estiver instalado\n# Será importado dentro das funções quando necessário' gestao_rural/views_relatorios_rastreabilidade.py
    fi
    
    echo "✅ Imports do topo removidos"
    
    # Adicionar lazy imports nas funções usando Python
    python3 << 'PYTHON_SCRIPT'
import re

file_path = "gestao_rural/views_relatorios_rastreabilidade.py"
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions = [
        ('exportar_anexo_i_excel', 'rastreabilidade_dashboard'),
        ('exportar_anexo_ii_excel', 'rastreabilidade_dashboard'),
        ('exportar_anexo_iii_excel', 'rastreabilidade_dashboard'),
        ('exportar_anexo_iv_excel', 'rastreabilidade_dashboard')
    ]
    
    modified = False
    for func_name, redirect_name in functions:
        # Padrão para encontrar a função
        pattern = rf'(@login_required\s+def {func_name}\([^)]+\):\s+"""[^"]*"""\s+)(propriedade = get_object_or_404)'
        
        # Verificar se já tem try/except
        if f'def {func_name}(' in content:
            func_start = content.find(f'def {func_name}(')
            # Verificar próximas 200 caracteres
            next_section = content[func_start:func_start+200]
            if 'try:' in next_section and 'from openpyxl' in next_section:
                continue  # Já tem lazy import
            
            # Adicionar lazy import antes de propriedade = get_object_or_404
            lazy_import = f'''    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        from django.contrib import messages
        messages.error(request, 'Biblioteca openpyxl não está instalada. Execute: pip install openpyxl')
        from django.shortcuts import redirect
        return redirect('{redirect_name}', propriedade_id=propriedade_id)
    
    '''
            
            # Substituir
            replacement = rf'\1{lazy_import}\2'
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
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
else
    echo "❌ Arquivo não encontrado!"
fi

echo ""
echo "2️⃣ Garantindo requirements_producao.txt..."
if [ ! -f "requirements_producao.txt" ]; then
    cat > requirements_producao.txt << 'EOF'
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3
psycopg2-binary==2.9.7
gunicorn==21.2.0
whitenoise==6.6.0
Pillow==10.0.1
reportlab==4.0.4
weasyprint==60.2
pandas==2.1.1
numpy==1.24.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
python-decouple==3.8
celery==5.3.1
redis==5.0.0
django-ratelimit==4.1.0
django-csp==3.7
django-extensions==3.2.3
django-debug-toolbar==4.2.0
django-anymail==10.1
django-redis==5.4.0
django-dbbackup==3.3.0
django-compressor==4.4
django-cachalot==2.6.1
pytest==7.4.2
pytest-django==4.5.2
coverage==7.3.1
openpyxl>=3.1.5
EOF
    echo "✅ requirements_producao.txt criado"
elif ! grep -qE "^openpyxl" requirements_producao.txt; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ openpyxl adicionado"
else
    echo "✅ openpyxl já está no requirements_producao.txt"
fi

echo ""
echo "3️⃣ Fazendo build completo..."
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
echo "Buildando: $IMAGE_TAG"
echo "⚠️ Este processo pode levar alguns minutos. Aguarde..."

gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso"
    gcloud container images add-tag $IMAGE_TAG gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet
    echo "✅ Tag 'latest' atualizada"
else
    echo "❌ Erro no build"
    exit 1
fi

echo ""
echo "4️⃣ Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "5️⃣ Aguardando serviço ficar pronto e testando..."
sleep 45

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

echo ""
echo "=========================================="
echo "📊 RESULTADO DO DEPLOY"
echo "=========================================="
echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando corretamente!"
else
    echo "⚠️ Status: $HTTP_CODE"
    echo ""
    echo "Verificando logs de erro..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=5 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -150
fi

echo ""
echo "✅ Processo concluído!"





