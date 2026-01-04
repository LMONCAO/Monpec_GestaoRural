@echo off
chcp 65001 >nul
echo ========================================
echo   VERIFICAR E APLICAR MIGRATIONS
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set CLOUD_SQL_CONN=%PROJECT_ID%:%REGION%:%DB_INSTANCE%

echo ???? Executando migrations via Cloud Run Job...
echo.

REM Criar job tempor??rio para aplicar migrations
gcloud run jobs create aplicar-migrations-temp ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region=%REGION% ^
    --add-cloudsql-instances=%CLOUD_SQL_CONN% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" ^
    --command python ^
    --args manage.py,migrate,--noinput ^
    --memory=2Gi ^
    --cpu=2 ^
    --max-retries=1 ^
    --task-timeout=600 ^
    --wait 2>nul

if errorlevel 1 (
    echo ??????  Job j?? existe ou erro ao criar. Tentando executar...
)

echo.
echo ???? Executando migrations...
echo.

gcloud run jobs execute aplicar-migrations-temp --region=%REGION% --wait

if errorlevel 1 (
    echo.
    echo ??? ERRO ao executar migrations!
    echo    Verifique os logs acima.
    pause
    exit /b 1
)

echo.
echo ??? Migrations aplicadas!
echo.

REM Limpar job tempor??rio
gcloud run jobs delete aplicar-migrations-temp --region=%REGION% --quiet 2>nul

echo.
echo ??? Processo conclu??do!
pause