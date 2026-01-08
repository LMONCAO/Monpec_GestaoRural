#!/bin/bash
echo '=== DIAGNÓSTICO MERCADO PAGO ==='

# 1. Verificar variáveis de ambiente
echo '1. Verificando variáveis MERCADOPAGO:'
gcloud run services describe monpec --region=us-central1 --format='value(spec.template.spec.containers[0].env[].name)' | grep -i mercado || echo '❌ Nenhuma variável MERCADOPAGO encontrada'

# 2. Verificar logs de erro
echo -e '\n2. Últimos logs de erro (últimas 10 linhas):'
gcloud run services logs read monpec --region=us-central1 --limit=10 | grep -E 'ERROR|500|mercadopago|checkout' || echo 'Nenhum erro específico encontrado nos últimos logs'

# 3. Testar URLs de checkout
echo -e '\n3. Testando URLs de checkout:'
echo 'Página assinaturas (landing page):'
curl -s -o /dev/null -w 'HTTP: %{http_code}\n' https://monpec.com.br/assinaturas/

echo 'Checkout básico (simulado):'
curl -s -o /dev/null -w 'HTTP: %{http_code}\n' https://monpec.com.br/assinaturas/plano/basico/checkout/ || echo '❌ Checkout não acessível (esperado se não logado)'

echo 'Página sucesso:'
curl -s -o /dev/null -w 'HTTP: %{http_code}\n' https://monpec.com.br/assinaturas/sucesso/

echo 'Página cancelado:'
curl -s -o /dev/null -w 'HTTP: %{http_code}\n' https://monpec.com.br/assinaturas/cancelado/

echo -e '\n=== CONCLUSÃO ==='
echo 'PROVÁVEL CAUSA: MERCADOPAGO_ACCESS_TOKEN não configurado no Cloud Run'
echo 'SOLUÇÃO: Configurar variável de ambiente MERCADOPAGO_ACCESS_TOKEN'


