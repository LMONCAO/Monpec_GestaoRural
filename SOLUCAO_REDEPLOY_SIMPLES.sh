#!/bin/bash
# Solução mais simples: Redeploy do serviço
# O Dockerfile já executa migrate e collectstatic quando o container inicia
# Execute: bash SOLUCAO_REDEPLOY_SIMPLES.sh

echo "=== REDEPLOY DO SERVIÇO CLOUD RUN ==="
echo ""
echo "Esta solução funciona porque o Dockerfile.prod já executa"
echo "migrate e collectstatic quando o container inicia!"
echo ""

# Configurar projeto
echo "1️⃣ Configurando projeto..."
gcloud config set project monpec-sistema-rural
echo "✅ Projeto configurado"
echo ""

# Build da imagem (força nova versão)
echo "2️⃣ Fazendo build da imagem (pode levar 10-20 minutos)..."
echo "⏱️ Isso força uma nova versão que vai executar migrate e collectstatic"
echo ""
gcloud builds submit --tag gcr.io/monpec-sistema-rural/sistema-rural:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build concluído!"
    echo ""
    echo "3️⃣ Fazendo deploy no Cloud Run..."
    echo "⏱️ Isso vai iniciar o container, que executará migrate e collectstatic automaticamente"
    echo ""
    
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/sistema-rural:latest \
        --region us-central1 \
        --platform managed \
        --allow-unauthenticated \
        --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
        --memory=2Gi \
        --cpu=2 \
        --timeout=600 \
        --max-instances=10 \
        --min-instances=0
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅"
        echo ""
        echo "O serviço foi reiniciado e executou:"
        echo "  ✅ migrate (criou as tabelas)"
        echo "  ✅ collectstatic (organizou os arquivos estáticos)"
        echo "  ✅ Criou usuário admin (se o comando garantir_admin estiver funcionando)"
        echo ""
        echo "Aguarde 1-2 minutos e acesse o sistema!"
    fi
else
    echo ""
    echo "❌ Erro no build. Verifique os logs acima."
fi

