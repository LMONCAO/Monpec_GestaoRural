@echo off
REM Script para executar migrações e criar admin no Google Cloud
REM Este script executa migrações e cria o usuário admin usando Cloud Run Jobs

setlocal enabledelayedexpansion

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set DB_INSTANCE=monpec-db
set DB_NAME=monpec_db
set DB_USER=monpec_user
set DB_PASSWORD=L6171r12@@jjms
set SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE
set DJANGO_SUPERUSER_PASSWORD=L6171r12@@
set IMAGE_NAME=gcr.io/%PROJECT_ID%/monpec:latest

echo ==========================================
echo EXECUTAR MIGRACOES E CRIAR ADMIN
echo ==========================================
echo.

echo [1/3] Verificando se o job existe...
gcloud run jobs describe migrate-and-create-admin --region=%REGION% >nul 2>&1
if errorlevel 1 (
    echo [INFO] Job nao existe. Criando job...
    goto CREATE_JOB
) else (
    echo [OK] Job existe. Atualizando...
    goto UPDATE_JOB
)

:CREATE_JOB
echo.
echo [2/3] Criando Cloud Run Job...
gcloud run jobs create migrate-and-create-admin ^
    --image=%IMAGE_NAME% ^
    --region=%REGION% ^
    --platform=managed ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=1800 ^
    --task-timeout=1800 ^
    --max-retries=1 ^
    --command=sh ^
    --args=-c,"python manage.py migrate --noinput && python manage.py garantir_admin --senha $DJANGO_SUPERUSER_PASSWORD && echo 'Migracoes e admin criado com sucesso!'" ^
    --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao criar job
    exit /b 1
)
goto EXECUTE_JOB

:UPDATE_JOB
echo.
echo [2/3] Atualizando Cloud Run Job...
gcloud run jobs update migrate-and-create-admin ^
    --image=%IMAGE_NAME% ^
    --region=%REGION% ^
    --platform=managed ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=1800 ^
    --task-timeout=1800 ^
    --max-retries=1 ^
    --command=sh ^
    --args=-c,"python manage.py migrate --noinput && python manage.py garantir_admin --senha $DJANGO_SUPERUSER_PASSWORD && echo 'Migracoes e admin criado com sucesso!'" ^
    --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar job
    exit /b 1
)

:EXECUTE_JOB
echo.
echo [3/3] Executando job (pode levar alguns minutos)...
gcloud run jobs execute migrate-and-create-admin ^
    --region=%REGION% ^
    --wait
if errorlevel 1 (
    echo [ERRO] Falha ao executar job
    echo.
    echo Verificando logs...
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-and-create-admin" --limit=20
    exit /b 1
)

echo.
echo ==========================================
echo SUCESSO!
echo ==========================================
echo.
echo Migracoes executadas e usuario admin criado!
echo.
echo Credenciais:
echo   Username: admin
echo   Senha: %DJANGO_SUPERUSER_PASSWORD%
echo.
echo Verificando logs do job...
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-and-create-admin" --limit=20 --format="table(timestamp,textPayload)"

echo.
pause

