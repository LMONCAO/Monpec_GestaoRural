@echo off
REM Script para Configurar Senha do Banco de Dados
cd /d "%~dp0"

echo ========================================
echo   CONFIGURAR SENHA DO BANCO DE DADOS
echo ========================================
echo.

set /p DB_PASSWORD="Digite a senha para o usuário monpec_user: "

if "%DB_PASSWORD%"=="" (
    echo ❌ Senha não pode estar vazia
    pause
    exit /b 1
)

echo.
echo 🔐 Configurando senha do banco...
gcloud sql users set-password monpec_user --instance=monpec-db --password=%DB_PASSWORD%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao configurar senha
    pause
    exit /b 1
)

echo.
echo ✅ Senha configurada!
echo.
echo 🚀 Atualizando Cloud Run com a senha...
echo.

gcloud run services update monpec --region us-central1 --update-env-vars "DB_PASSWORD=%DB_PASSWORD%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao atualizar Cloud Run
    pause
    exit /b 1
)

echo.
echo ✅ Tudo configurado!
echo.
echo ⚠️  Próximos passos:
echo.
echo 1. Execute as migrações:
echo    gcloud run jobs create monpec-migrate --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=E4-jbkGNP1rDcuZ8w-sKsb2jSPS1yWp7IbKvmrTXY0FIeR9GvKjugvgG6PBWLCoRIR0,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%" --command python --args manage.py,migrate
echo.
echo    gcloud run jobs execute monpec-migrate --region us-central1 --wait
echo.
echo 2. Crie o usuário admin:
echo    Execute criar_admin_cloud_run.ps1
echo.

pause






































