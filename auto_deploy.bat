@echo off
REM DEPLOY AUTOMATICO COMPLETO MONPEC
echo ========================================
echo 🚀 DEPLOY AUTOMATICO COMPLETO MONPEC
echo ========================================
echo.
echo Este script faz tudo automaticamente!
echo.

REM Configurações
set IMAGE=gcr.io/monpec-sistema-rural/monpec:latest
set REGION=us-central1
set SERVICE=monpec
set ENV_VARS=DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE

echo ========================================
echo 1. RESETANDO BANCO DE DADOS
echo ========================================

echo Criando job de reset...
gcloud run jobs create reset-db-auto --image %IMAGE% --region %REGION% --set-env-vars="%ENV_VARS%" --command="python" --args="manage.py,reset_db" --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800

echo Executando reset...
gcloud run jobs execute reset-db-auto --region=%REGION% --wait

echo ========================================
echo 2. APLICANDO MIGRAÇÕES
echo ========================================

echo Criando job de migração...
gcloud run jobs create migrate-auto --image %IMAGE% --region %REGION% --set-env-vars="%ENV_VARS%" --command="python" --args="manage.py,migrate,--noinput" --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800

echo Executando migrações...
gcloud run jobs execute migrate-auto --region=%REGION% --wait

echo ========================================
echo 3. POPULANDO DADOS
echo ========================================

echo Criando job de população...
gcloud run jobs create populate-auto --image %IMAGE% --region %REGION% --set-env-vars="%ENV_VARS%" --command="python" --args="popular_dados_producao.py" --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800

echo Executando população...
gcloud run jobs execute populate-auto --region=%REGION% --wait

echo ========================================
echo 4. ATUALIZANDO SERVIÇO
echo ========================================

echo Atualizando serviço...
gcloud run services update %SERVICE% --region=%REGION% --set-env-vars="%ENV_VARS%" --memory=4Gi --cpu=2 --timeout=300

echo ========================================
echo 5. TESTANDO SISTEMA
echo ========================================

echo Testando sistema...
echo === VERIFICANDO SISTEMA ===
curl -I https://monpec-29862706245.us-central1.run.app/

echo.
echo === TESTANDO LANDING PAGE ===
curl -s https://monpec-29862706245.us-central1.run.app/ | head -10

echo.
echo ========================================
echo 🎉 DEPLOY CONCLUÍDO!
echo ========================================
echo.
echo 🌐 Landing Page: https://monpec-29862706245.us-central1.run.app/
echo 🔐 Admin: https://monpec-29862706245.us-central1.run.app/admin/
echo 📊 Dashboard: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/
echo 📅 Planejamento: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/planejamento/
echo.
echo 👤 LOGIN ADMIN:
echo Usuario: admin
echo Senha: [sua senha atual]
echo.
echo ========================================

pause