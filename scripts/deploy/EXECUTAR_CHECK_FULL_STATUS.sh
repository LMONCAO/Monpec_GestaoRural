#!/bin/bash
# Executar o job check-full-status que foi criado

echo "▶ Executando verificação de estado completo..."
gcloud run jobs execute check-full-status --region us-central1 --wait

echo ""
echo "✅ Verificação concluída!"
echo ""
echo "Se a tabela não existe, o script continuará automaticamente removendo o registro da migração e reaplicando."








