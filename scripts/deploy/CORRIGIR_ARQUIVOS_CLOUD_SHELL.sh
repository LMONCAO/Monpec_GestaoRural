#!/bin/bash
# Script para corrigir arquivos diretamente no Cloud Shell ANTES do build

set -e

echo "=========================================="
echo "🔧 CORRIGINDO ARQUIVOS NO CLOUD SHELL"
echo "=========================================="
echo ""

echo "1️⃣ Verificando views_exportacao.py..."
echo "----------------------------------------"
if [ -f "gestao_rural/views_exportacao.py" ]; then
    # Verificar se tem import no topo (linhas 1-20)
    if head -20 gestao_rural/views_exportacao.py | grep -q "^from openpyxl\|^import openpyxl"; then
        echo "❌ Encontrado import de openpyxl no topo!"
        echo "Removendo..."
        # Criar backup
        cp gestao_rural/views_exportacao.py gestao_rural/views_exportacao.py.bak
        
        # Remover linhas que começam com from openpyxl ou import openpyxl nas primeiras 20 linhas
        sed -i '1,20{/^from openpyxl/d; /^import openpyxl/d}' gestao_rural/views_exportacao.py
        
        echo "✅ Removido. Verificando..."
        if head -20 gestao_rural/views_exportacao.py | grep -q "^from openpyxl\|^import openpyxl"; then
            echo "⚠️ Ainda há imports. Verificando manualmente..."
            head -20 gestao_rural/views_exportacao.py | grep -n "openpyxl" || echo "✅ Nenhum import encontrado"
        else
            echo "✅ Confirmado: sem imports no topo"
        fi
    else
        echo "✅ Nenhum import de openpyxl no topo encontrado"
    fi
else
    echo "❌ Arquivo gestao_rural/views_exportacao.py não encontrado!"
fi

echo ""
echo "2️⃣ Verificando middleware.py..."
echo "----------------------------------------"
if [ -f "sistema_rural/middleware.py" ]; then
    if grep -q "request.get_host()" sistema_rural/middleware.py; then
        echo "❌ Middleware ainda usa request.get_host()!"
        echo "Corrigindo..."
        # Criar backup
        cp sistema_rural/middleware.py sistema_rural/middleware.py.bak
        
        # Substituir request.get_host() por request.META.get('HTTP_HOST', '').split(':')[0]
        sed -i "s/request\.get_host()\.split(':')\[0\]/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        sed -i "s/request\.get_host()/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        
        echo "✅ Corrigido"
    else
        echo "✅ Middleware já está correto"
    fi
else
    echo "❌ Arquivo sistema_rural/middleware.py não encontrado!"
fi

echo ""
echo "3️⃣ Verificando requirements.txt..."
echo "----------------------------------------"
if [ ! -f "requirements.txt" ]; then
    echo "Criando requirements.txt..."
    cat > requirements.txt << 'EOF'
Django>=4.2.7,<5.0
psycopg2-binary>=2.9.9
gunicorn>=21.2.0
python-decouple>=3.8
whitenoise>=6.6.0
openpyxl>=3.1.5
reportlab>=4.0.0
Pillow>=10.0.0
django-extensions>=3.2.0
EOF
    echo "✅ requirements.txt criado"
elif ! grep -q "^openpyxl" requirements.txt; then
    echo "Adicionando openpyxl..."
    echo "openpyxl>=3.1.5" >> requirements.txt
    echo "✅ openpyxl adicionado"
else
    echo "✅ openpyxl já está no requirements.txt"
fi

echo ""
echo "4️⃣ Verificando se há requirements_producao.txt..."
echo "----------------------------------------"
if [ -f "requirements_producao.txt" ]; then
    if ! grep -q "^openpyxl" requirements_producao.txt; then
        echo "Adicionando openpyxl ao requirements_producao.txt..."
        echo "openpyxl>=3.1.5" >> requirements_producao.txt
        echo "✅ openpyxl adicionado ao requirements_producao.txt"
    else
        echo "✅ openpyxl já está no requirements_producao.txt"
    fi
fi

echo ""
echo "=========================================="
echo "✅ CORREÇÕES APLICADAS"
echo "=========================================="
echo ""
echo "📝 Próximo passo: Execute o build e deploy"
echo ""





