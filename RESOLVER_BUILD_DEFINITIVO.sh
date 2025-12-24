#!/bin/bash
# Solução definitiva para o build

echo "========================================"
echo "🔧 RESOLVENDO BUILD DEFINITIVAMENTE"
echo "========================================"
echo ""

# 1. Verificar se há django-logging em algum lugar
echo "1️⃣  Verificando se há django-logging..."
if grep -r "django-logging" . --include="*.txt" --include="*.py" 2>/dev/null | grep -v ".git" | grep -v "__pycache__"; then
    echo "⚠️  Encontrado django-logging em algum arquivo"
    echo "Removendo..."
    find . -name "*.txt" -type f -exec sed -i '/django-logging/d' {} \; 2>/dev/null
    echo "✅ Removido"
else
    echo "✅ django-logging não encontrado nos arquivos"
fi
echo ""

# 2. Garantir que requirements_producao.txt está limpo
echo "2️⃣  Verificando requirements_producao.txt..."
if grep -q "django-logging" requirements_producao.txt 2>/dev/null; then
    echo "Removendo django-logging do requirements_producao.txt..."
    sed -i '/django-logging/d' requirements_producao.txt
    echo "✅ Removido"
else
    echo "✅ requirements_producao.txt está limpo"
fi
echo ""

# 3. Fazer build ignorando erros de dependências opcionais
echo "3️⃣  Fazendo build..."
echo "Aguarde, isso pode levar vários minutos..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD CONCLUÍDO COM SUCESSO!"
    echo ""
    echo "4️⃣  Agora faça o deploy:"
    echo ""
    echo "gcloud run deploy monpec \\"
    echo "    --image gcr.io/monpec-sistema-rural/monpec:latest \\"
    echo "    --region us-central1 \\"
    echo "    --platform managed \\"
    echo "    --allow-unauthenticated \\"
    echo "    --set-env-vars \"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br\" \\"
    echo "    --update-env-vars \"MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/\" \\"
    echo "    --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 1 --port 8080"
    echo ""
else
    echo ""
    echo "❌ BUILD FALHOU"
    echo ""
    echo "Verifique o erro acima. Se for django-logging, pode ser dependência de outro pacote."
    echo "Tente remover o pacote que está causando o problema."
    echo ""
fi



