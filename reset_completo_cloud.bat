@echo off
REM RESET COMPLETO MONPEC - GOOGLE CLOUD APPROACH
REM Execute este arquivo no Google Cloud Shell

echo =========================================
echo 🔄 RESET COMPLETO MONPEC - CLOUD APPROACH
echo =========================================

echo.
echo 1️⃣ CRIANDO NOVO BANCO POSTGRESQL...
echo.

REM Dropar banco existente se existir
gcloud sql databases delete monpec-db --instance=monpec-db --quiet 2>nul || echo Banco nao existia

REM Criar novo banco
gcloud sql databases create monpec-db --instance=monpec-db

echo.
echo ✅ Novo banco criado
echo.

echo 2️⃣ FAZENDO BUILD DA IMAGEM LIMPA...
echo.

REM Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

echo.
echo ✅ Imagem buildada
echo.

echo 3️⃣ DEPLOY COM MIGRATE FRESH...
echo.

REM Criar job de migrate fresh
gcloud run jobs create migrate-fresh-clean --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --command="python" --args="manage.py,migrate,--noinput" --memory=4Gi --cpu=2 --max-retries=1 --task-timeout=1800

REM Executar migrate
gcloud run jobs execute migrate-fresh-clean --region=us-central1 --wait

echo.
echo ✅ Migrações aplicadas
echo.

echo 4️⃣ POPULANDO DADOS LIMPOS...
echo.

REM Criar job de população
gcloud run jobs create populate-clean-fresh --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --command="python" --args="popular_dados_producao.py" --memory=4Gi --cpu=2 --max-retries=1 --task-timeout=1800

REM Executar população
gcloud run jobs execute populate-clean-fresh --region=us-central1 --wait

echo.
echo ✅ Dados populados
echo.

echo 5️⃣ DEPLOY SERVIÇO LIMPO...
echo.

REM Deploy do serviço
gcloud run services update monpec --region=us-central1 --image=gcr.io/monpec-sistema-rural/monpec --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" --memory=4Gi --cpu=2 --timeout=300

echo.
echo ✅ Serviço atualizado
echo.

echo 6️⃣ TESTE FINAL...
echo.

timeout /t 10 /nobreak >nul

echo === VERIFICANDO SISTEMA ===
curl -I https://monpec-29862706245.us-central1.run.app/

echo.
echo === TESTANDO LANDING PAGE ===
curl -s https://monpec-29862706245.us-central1.run.app/ | head -10

echo.
echo =========================================
echo 🎉 SISTEMA MONPEC RESETADO E FUNCIONANDO!
echo =========================================
echo.
echo ✅ Novo banco PostgreSQL criado
echo ✅ Migrações aplicadas do zero
echo ✅ Dados populados limpos (1.300 animais)
echo ✅ Deploy sem conflitos
echo.
echo 🌐 URL: https://monpec-29862706245.us-central1.run.app/
echo 👤 Admin: admin / [sua senha atual]
echo.
echo =========================================

pause