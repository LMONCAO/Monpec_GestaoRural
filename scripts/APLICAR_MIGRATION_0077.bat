@echo off
chcp 65001 >nul
echo ========================================
echo   APLICAR MIGRATION 0077
echo   (mercadopago_customer_id)
echo ========================================
echo.
echo Esta migration adiciona os campos do Mercado Pago na tabela AssinaturaCliente
echo.

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set IMAGE_NAME=gcr.io/monpec-sistema-rural/sistema-rural:latest

echo [1/3] Configurando projeto...
gcloud config set project %PROJECT_ID%
if errorlevel 1 (
    echo [ERRO] Falha ao configurar projeto
    pause
    exit /b 1
)

echo.
echo [2/3] Criando job para aplicar migration...
set CLOUD_SQL_CONN=%PROJECT_ID%:%REGION%:monpec-db

gcloud run jobs delete aplicar-migration-0077 --region=%REGION% --quiet 2>nul

gcloud run jobs create aplicar-migration-0077 ^
    --region=%REGION% ^
    --image=%IMAGE_NAME% ^
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=%CLOUD_SQL_CONN%" ^
    --set-cloudsql-instances=%CLOUD_SQL_CONN% ^
    --command="python" ^
    --args="manage.py,migrate,gestao_rural,0077,--fake-if-exists" ^
    --max-retries=1 ^
    --memory=2Gi ^
    --cpu=2 ^
    --task-timeout=300

if errorlevel 1 (
    echo [ERRO] Falha ao criar job!
    pause
    exit /b 1
)

echo.
echo [3/3] Executando migration...
gcloud run jobs execute aplicar-migration-0077 --region=%REGION% --wait

if errorlevel 1 (
    echo [ERRO] Falha ao executar migration!
    echo.
    echo Verificando logs...
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migration-0077" --limit=20 --format="value(textPayload)" --freshness=5m
    pause
    exit /b 1
)

echo.
echo Verificando logs...
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migration-0077" --limit=20 --format="value(textPayload)" --freshness=5m

echo.
echo Limpando job...
gcloud run jobs delete aplicar-migration-0077 --region=%REGION% --quiet 2>nul

echo.
echo ========================================
echo   MIGRATION APLICADA!
echo ========================================
echo.
echo Teste acessando: https://monpec-29862706245.us-central1.run.app/dashboard/
echo.
pause


