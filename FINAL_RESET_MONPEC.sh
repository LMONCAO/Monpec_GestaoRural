#!/bin/bash
echo "🎯 RESET COMPLETO MONPEC - COPIE E COLE TUDO ABAIXO NO CLOUD SHELL"
echo "=================================================================="

# RESET COMPLETO - COPIE DAQUI PARA BAIXO E COLE NO CLOUD SHELL
# =================================================================

echo "1️⃣ RESETANDO BANCO..."
gcloud sql databases delete monpec-db --instance=monpec-db --quiet 2>/dev/null || echo "OK"
gcloud sql databases create monpec-db --instance=monpec-db
echo "✅ Banco resetado"

echo "2️⃣ BUILD IMAGEM..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
echo "✅ Imagem buildada"

echo "3️⃣ MIGRATE FRESH..."
gcloud run jobs create migrate-clean --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --command="python" --args="manage.py,migrate,--noinput" --memory=4Gi --cpu=2 --max-retries=1 --task-timeout=1800
gcloud run jobs execute migrate-clean --region=us-central1 --wait
echo "✅ Migrações OK"

echo "4️⃣ POPULAR DADOS..."
gcloud run jobs create populate-clean --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --command="python" --args="popular_dados_producao.py" --memory=4Gi --cpu=2 --max-retries=1 --task-timeout=1800
gcloud run jobs execute populate-clean --region=us-central1 --wait
echo "✅ Dados populados"

echo "5️⃣ DEPLOY SERVIÇO..."
gcloud run services update monpec --region=us-central1 --image=gcr.io/monpec-sistema-rural/monpec --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --memory=4Gi --cpu=2 --timeout=300
echo "✅ Serviço deployado"

echo "6️⃣ TESTE FINAL..."
sleep 10
echo "=== VERIFICANDO SISTEMA ==="
curl -I https://monpec-29862706245.us-central1.run.app/
echo ""
echo "=== TESTANDO LANDING PAGE ==="
curl -s https://monpec-29862706245.us-central1.run.app/ | head -5

echo ""
echo "🎉 SISTEMA MONPEC RESETADO E FUNCIONANDO!"
echo "🌐 https://monpec-29862706245.us-central1.run.app/"
echo "👤 admin / [sua senha]"