#!/bin/bash
# Verificar se o deploy atualizou corretamente

echo "========================================"
echo "🔍 Verificando Deploy"
echo "========================================"
echo ""

# 1. Ver imagem atual do serviço
echo "1️⃣  Imagem atual do serviço:"
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].image)" 2>/dev/null
echo ""

# 2. Ver última revisão
echo "2️⃣  Últimas revisões:"
gcloud run revisions list --service monpec --region us-central1 --limit 3 2>/dev/null
echo ""

# 3. Ver logs recentes
echo "3️⃣  Logs recentes (últimas 10 linhas):"
gcloud run services logs read monpec --region us-central1 --limit 10 2>/dev/null | tail -15
echo ""

# 4. Verificar se há erros
echo "4️⃣  Verificando erros nos logs:"
gcloud run services logs read monpec --region us-central1 --limit 50 2>/dev/null | grep -i "error\|exception\|traceback" | head -10
echo ""
