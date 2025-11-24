#!/bin/bash
# ✅ Script para verificar se o deploy foi bem-sucedido
# Execute no Cloud Shell ou localmente

SERVICE_URL="https://monpec-fzzfjppzva-uc.a.run.app"

echo "🔍 VERIFICANDO DEPLOY - MONPEC"
echo "========================================"
echo ""
echo "🌐 URL do serviço: $SERVICE_URL"
echo ""

# Verificar se o serviço está respondendo
echo "1️⃣ Verificando se o serviço está online..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Serviço está online (HTTP $HTTP_CODE)"
else
    echo "   ❌ Serviço retornou HTTP $HTTP_CODE"
    exit 1
fi

echo ""

# Verificar meta tag
echo "2️⃣ Verificando meta tag do Google Search Console..."
META_TAG=$(curl -s $SERVICE_URL | grep -i "google-site-verification" | head -1)
if [ -n "$META_TAG" ]; then
    echo "   ✅ Meta tag encontrada:"
    echo "   $META_TAG"
else
    echo "   ❌ Meta tag NÃO encontrada no código-fonte"
    echo "   ⚠️  Verifique se fez push para o GitHub e se o build incluiu as alterações"
fi

echo ""

# Verificar arquivo HTML
echo "3️⃣ Verificando arquivo HTML do Google Search Console..."
HTML_FILE=$(curl -s "$SERVICE_URL/google40933139f3b0d469.html")
if [ -n "$HTML_FILE" ]; then
    if echo "$HTML_FILE" | grep -q "google-site-verification"; then
        echo "   ✅ Arquivo HTML encontrado:"
        echo "   $HTML_FILE"
    else
        echo "   ❌ Arquivo HTML não contém o conteúdo esperado"
        echo "   Conteúdo recebido: $HTML_FILE"
    fi
else
    echo "   ❌ Arquivo HTML não encontrado (404 ou erro)"
    echo "   ⚠️  Verifique se a rota está configurada no urls.py"
fi

echo ""
echo "========================================"
echo "📋 Próximos Passos:"
echo "========================================"
echo ""
echo "1. Acesse: $SERVICE_URL"
echo "2. Pressione Ctrl+U para ver o código-fonte"
echo "3. Procure por: google-site-verification"
echo "4. Acesse: $SERVICE_URL/google40933139f3b0d469.html"
echo "5. Verifique no Google Search Console:"
echo "   https://search.google.com/search-console"
echo "   → Adicionar propriedade"
echo "   → Prefixo de URL: $SERVICE_URL"
echo "   → Método: Tag HTML ou Arquivo HTML"
echo ""














