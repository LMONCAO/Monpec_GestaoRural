#!/bin/bash
# Executar o job run-migrations-normal que já foi criado

echo "▶ Executando job run-migrations-normal..."
gcloud run jobs execute run-migrations-normal --region us-central1 --wait

echo ""
echo "✅ Migrações executadas!"
echo ""
echo "▶ Verificando se funcionou..."
echo "Acesse os logs para verificar se houve erros:"
echo "https://console.cloud.google.com/run/jobs/executions?project=$(gcloud config get-value project)"








