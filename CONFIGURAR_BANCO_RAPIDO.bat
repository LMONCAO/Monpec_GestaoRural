@echo off
REM Script Rápido para Configurar Banco de Dados no Cloud Run
cd /d "%~dp0"

echo ========================================
echo   CONFIGURAR BANCO DE DADOS - CLOUD RUN
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set SERVICE_NAME=monpec
set CONNECTION_NAME=%PROJECT_ID%:us-central1:monpec-db

echo Connection Name: %CONNECTION_NAME%
echo.

REM Solicitar senha do banco
set /p DB_PASSWORD="Digite a senha do banco de dados (monpec_user): "

REM Gerar SECRET_KEY
echo.
echo Gerando SECRET_KEY...
for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(50))"') do set SECRET_KEY=%%i

echo.
echo 🚀 Configurando Cloud Run...
echo.

REM Conectar ao Cloud SQL e configurar variáveis
gcloud run services update %SERVICE_NAME% ^
    --region %REGION% ^
    --add-cloudsql-instances %CONNECTION_NAME% ^
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao configurar
    pause
    exit /b 1
)

echo.
echo ✅ Configuração concluída!
echo.
echo ⚠️  Próximos passos:
echo.
echo 1. Execute as migrações:
echo    gcloud run jobs execute monpec-migrate --region %REGION%
echo.
echo 2. Crie o usuário admin:
echo    Execute criar_admin_cloud_run.ps1
echo.

pause






































