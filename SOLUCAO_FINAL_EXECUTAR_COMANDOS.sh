#!/bin/bash
# SOLUÇÃO FINAL: Executar comandos diretamente no Cloud Run
# Execute: bash SOLUCAO_FINAL_EXECUTAR_COMANDOS.sh

echo "=== SOLUÇÃO FINAL: Executar comandos no Cloud Run ==="
echo ""
echo "Como o Dockerfile já executa migrate e collectstatic na inicialização,"
echo "a forma mais simples é fazer um redeploy ou executar os comandos diretamente."
echo ""

# Configurar projeto
gcloud config set project monpec-sistema-rural 2>/dev/null || true

echo "✅ Opção 1: O mais simples - Redeploy (recomendado)"
echo ""
echo "Como o Dockerfile.prod já executa migrate e collectstatic no CMD,"
echo "você só precisa fazer um redeploy do serviço:"
echo ""
echo "  1. Faça um pequeno rebuild da imagem (força nova execução do CMD):"
echo "     gcloud builds submit --tag gcr.io/monpec-sistema-rural/sistema-rural:latest ."
echo ""
echo "  2. Depois faça deploy novamente:"
echo "     gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/sistema-rural:latest --region us-central1"
echo ""
echo "✅ Opção 2: Executar comandos via Cloud Run Services (se disponível)"
echo ""
echo "Tente executar diretamente no serviço rodando:"
echo ""
echo "  gcloud run services update monpec --region us-central1 --update-env-vars FORCE_MIGRATE=true"
echo "  # Isso força uma reinicialização que executa migrate e collectstatic"
echo ""
echo "✅ Opção 3: Usar Cloud SQL Proxy localmente (mais complexo)"
echo ""
echo "Se as opções acima não funcionarem, você pode:"
echo "  1. Instalar Cloud SQL Proxy no Cloud Shell"
echo "  2. Conectar ao banco"
echo "  3. Executar comandos Django diretamente"
echo ""
echo "Mas a Opção 1 (redeploy) é a mais simples e recomendada!"

