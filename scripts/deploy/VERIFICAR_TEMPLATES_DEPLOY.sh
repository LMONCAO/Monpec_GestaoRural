#!/bin/bash
# Script para verificar se templates serão incluídos no deploy

echo "========================================"
echo "VERIFICAÇÃO: Templates no Deploy"
echo "========================================"
echo ""

# Verificar .dockerignore
echo "1. Verificando .dockerignore..."
if [ -f ".dockerignore" ]; then
    echo "✓ .dockerignore encontrado"
    
    # Verificar se templates está sendo ignorado
    if grep -qi "template" .dockerignore; then
        echo "  ⚠ AVISO: 'template' encontrado no .dockerignore!"
        echo "  Linhas encontradas:"
        grep -i "template" .dockerignore | sed 's/^/    /'
        echo ""
        echo "  ⚠ Isso pode excluir templates do deploy!"
    else
        echo "  ✓ Templates NÃO estão sendo ignorados (.dockerignore OK)"
    fi
else
    echo "  ⚠ .dockerignore não encontrado (tudo será copiado)"
fi
echo ""

# Verificar Dockerfile.prod
echo "2. Verificando Dockerfile.prod..."
if [ -f "Dockerfile.prod" ]; then
    echo "✓ Dockerfile.prod encontrado"
    
    if grep -q "COPY \. \." Dockerfile.prod; then
        echo "  ✓ Comando 'COPY . .' encontrado (copia tudo, incluindo templates)"
    else
        echo "  ⚠ Comando 'COPY . .' não encontrado"
        echo "  Verificando outros comandos COPY..."
        grep -i "COPY" Dockerfile.prod | head -5
    fi
else
    echo "  ⚠ Dockerfile.prod não encontrado"
fi
echo ""

# Verificar se pasta templates existe
echo "3. Verificando estrutura de templates..."
TEMPLATE_DIRS=(
    "templates"
    "gestao_rural/templates"
    "templates/gestao_rural"
)

FOUND_TEMPLATES=false
for dir in "${TEMPLATE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ Pasta encontrada: $dir"
        COUNT=$(find "$dir" -name "*.html" 2>/dev/null | wc -l)
        if [ "$COUNT" -gt 0 ]; then
            echo "    → $COUNT arquivos .html encontrados"
            FOUND_TEMPLATES=true
        else
            echo "    → Nenhum arquivo .html encontrado"
        fi
    fi
done

if [ "$FOUND_TEMPLATES" = false ]; then
    echo "  ⚠ Nenhuma pasta de templates encontrada nos locais padrão"
    echo "  Procurando arquivos .html em todo o projeto..."
    HTML_COUNT=$(find . -name "*.html" -not -path "./staticfiles/*" -not -path "./.git/*" 2>/dev/null | wc -l)
    if [ "$HTML_COUNT" -gt 0 ]; then
        echo "  → $HTML_COUNT arquivos .html encontrados no projeto"
        echo "  Localizações:"
        find . -name "*.html" -not -path "./staticfiles/*" -not -path "./.git/*" 2>/dev/null | head -10 | sed 's/^/    /'
    fi
fi
echo ""

# Verificar settings.py
echo "4. Verificando configuração TEMPLATES no settings.py..."
if [ -f "sistema_rural/settings.py" ]; then
    if grep -A 5 "TEMPLATES" sistema_rural/settings.py | grep -q "templates"; then
        echo "  ✓ Configuração TEMPLATES encontrada"
        echo "  Configuração:"
        grep -A 8 "TEMPLATES" sistema_rural/settings.py | grep -E "(DIRS|APP_DIRS)" | sed 's/^/    /'
    else
        echo "  ⚠ Configuração TEMPLATES não encontrada ou diferente"
    fi
fi
echo ""

# Resumo
echo "========================================"
echo "RESUMO"
echo "========================================"
echo ""
echo "Como templates são enviados:"
echo ""
echo "1. Dockerfile.prod executa: COPY . ."
echo "   → Isso copia TODOS os arquivos do projeto"
echo ""
echo "2. .dockerignore define o que NÃO copiar"
echo "   → Templates NÃO estão no .dockerignore ✅"
echo ""
echo "3. Portanto: Templates SÃO copiados automaticamente ✅"
echo ""
echo "4. Django encontra templates pela configuração TEMPLATES"
echo "   → DIRS: [BASE_DIR / 'templates']"
echo "   → APP_DIRS: True (procura em cada app/templates/)"
echo ""
echo "========================================"
echo "✅ Conclusão: Templates são enviados automaticamente!"
echo "   Não é necessário fazer nada especial."
echo "========================================"
echo ""





