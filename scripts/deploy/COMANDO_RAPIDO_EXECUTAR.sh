#!/bin/bash
# Comando rápido para executar o job create-admin-final que já foi criado

echo "▶ Executando job create-admin-final..."
gcloud run jobs execute create-admin-final --region us-central1 --wait

echo ""
echo "✅ Admin criado!"
echo ""
echo "Teste o login:"
echo "https://monpec-29862706245.us-central1.run.app/login/"








