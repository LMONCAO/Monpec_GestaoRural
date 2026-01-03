#!/bin/bash
# Verificar erro 500 após deploy
# Execute no Google Cloud Shell

echo "============================================================"
echo "🔍 Verificando erro 500 após deploy"
echo "============================================================"
echo ""

echo "📋 Últimos 5 logs do serviço:"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=5 --format="value(textPayload)" 2>/dev/null

echo ""
echo "============================================================"
echo "💡 Problemas comuns e soluções:"
echo "============================================================"
echo ""
echo "1. DisallowedHost:"
echo "   - Verifique se monpec-fzzfjppzva-uc.a.run.app está em ALLOWED_HOSTS"
echo ""
echo "2. SECRET_KEY faltando:"
echo "   - Verifique se SECRET_KEY está definida nas variáveis de ambiente"
echo ""
echo "3. Migrations pendentes:"
echo "   - Execute o script de aplicar migrations novamente"
echo ""
echo "4. Erro de conexão com banco:"
echo "   - Verifique se Cloud SQL está rodando"
echo "   - Verifique CLOUD_SQL_CONNECTION_NAME"
echo ""

