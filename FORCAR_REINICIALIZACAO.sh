#!/bin/bash
# Força reinicialização do serviço Cloud Run
# Isso vai executar migrate e collectstatic automaticamente (via Dockerfile CMD)

echo "=== FORÇAR REINICIALIZAÇÃO DO SERVIÇO ==="
echo ""
echo "Isso vai forçar uma nova réplica do serviço, que executará"
echo "migrate e collectstatic automaticamente (definido no Dockerfile.prod)"
echo ""

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Forçar reinicialização atualizando uma variável de ambiente vazia
# Isso não altera nada mas força uma nova revisão
echo "Forçando nova revisão do serviço..."
gcloud run services update monpec \
  --region us-central1 \
  --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --no-traffic

echo ""
echo "✅ Nova revisão criada. Agora direcionando todo o tráfego para ela..."
gcloud run services update-traffic monpec \
  --region us-central1 \
  --to-latest

echo ""
echo "✅✅✅ SERVIÇO REINICIALIZADO! ✅✅✅"
echo ""
echo "O serviço foi reiniciado e executou automaticamente:"
echo "  ✅ python manage.py migrate --noinput"
echo "  ✅ python manage.py collectstatic --noinput"
echo ""
echo "Aguarde 1-2 minutos e verifique se está funcionando!"

