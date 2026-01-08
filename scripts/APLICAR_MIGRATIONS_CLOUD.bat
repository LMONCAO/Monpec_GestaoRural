@echo off
chcp 65001 >nul
echo ========================================
echo   APLICAR MIGRATIONS NO CLOUD RUN
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set CLOUD_SQL_CONN=%PROJECT_ID%:%REGION%:%DB_INSTANCE%

echo ???? Configura????es:
echo    Projeto: %PROJECT_ID%
echo    Servi??o: %SERVICE_NAME%
echo    Cloud SQL: %CLOUD_SQL_CONN%
echo.

echo ??????  IMPORTANTE: Este script executa migrations via Cloud Run Job
echo    Certifique-se de que as vari??veis de ambiente est??o configuradas.
echo.

pause

echo.
echo ???? Criando Cloud Run Job para aplicar migrations...
echo.

gcloud run jobs create aplicar-migrations ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region=%REGION% ^
    --add-cloudsql-instances=%CLOUD_SQL_CONN% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" ^
    --memory=2Gi ^
    --cpu=2 ^
    --max-retries=1 ^
    --task-timeout=600

if errorlevel 1 (
    echo ??????  Job j?? existe, atualizando...
    gcloud run jobs update aplicar-migrations ^
        --image gcr.io/%PROJECT_ID%/monpec:latest ^
        --region=%REGION% ^
        --add-cloudsql-instances=%CLOUD_SQL_CONN% ^
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" ^
        --memory=2Gi ^
        --cpu=2 ^
        --max-retries=1 ^
        --task-timeout=600
)

echo.
echo ???? Executando migrations...
echo.

gcloud run jobs execute aplicar-migrations --region=%REGION% --wait

if errorlevel 1 (
    echo.
    echo ??? ERRO ao executar migrations!
    echo    Verifique os logs acima.
    pause
    exit /b 1
)

echo.
echo ??? Migrations aplicadas com sucesso!
echo.

pause