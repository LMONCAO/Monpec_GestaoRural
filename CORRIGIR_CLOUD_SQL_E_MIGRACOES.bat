@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para criar Cloud SQL e executar migracoes

echo ========================================
echo   CORRIGIR CLOUD SQL E MIGRACOES
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set DB_NAME=monpec_db
set DB_USER=monpec_user
set DB_PASSWORD=L6171r12@@jjms

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Instancia SQL: %DB_INSTANCE%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM VERIFICAR SE INSTANCIA EXISTE
REM ========================================
echo [1/5] Verificando se instancia Cloud SQL existe...
echo.

gcloud sql instances describe %DB_INSTANCE% --project=%PROJECT_ID% >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Instancia Cloud SQL nao encontrada. Criando...
    echo.
    echo Isso pode levar 5-10 minutos. Aguarde...
    echo.
    
    REM Criar instancia
    gcloud sql instances create %DB_INSTANCE% ^
        --database-version=POSTGRES_14 ^
        --tier=db-f1-micro ^
        --region=%REGION% ^
        --backup-start-time=03:00 ^
        --storage-type=SSD ^
        --storage-size=10GB ^
        --project=%PROJECT_ID%
    
    if errorlevel 1 (
        echo [ERRO] Falha ao criar instancia Cloud SQL!
        pause
        exit /b 1
    )
    
    echo [OK] Instancia Cloud SQL criada!
    echo.
    echo Aguardando instancia estar pronta (pode levar 3-5 minutos)...
    gcloud sql instances wait %DB_INSTANCE% --timeout=600 --project=%PROJECT_ID%
    echo [OK] Instancia pronta!
    echo.
) else (
    echo [OK] Instancia Cloud SQL ja existe!
    echo.
)

REM ========================================
REM CRIAR BANCO DE DADOS
REM ========================================
echo [2/5] Verificando/Criando banco de dados...
echo.

gcloud sql databases create %DB_NAME% --instance=%DB_INSTANCE% --project=%PROJECT_ID% 2>&1 | findstr /V "already exists" || echo.
echo [OK] Banco de dados verificado!
echo.

REM ========================================
REM CRIAR/ATUALIZAR USUARIO
REM ========================================
echo [3/5] Verificando/Criando usuario do banco...
echo.

REM Tentar criar usuario (pode ja existir)
gcloud sql users create %DB_USER% --instance=%DB_INSTANCE% --password=%DB_PASSWORD% --project=%PROJECT_ID% 2>&1 | findstr /V "already exists" || echo.

REM Atualizar senha do usuario (caso ja exista)
gcloud sql users set-password %DB_USER% --instance=%DB_INSTANCE% --password=%DB_PASSWORD% --project=%PROJECT_ID% >nul 2>&1

echo [OK] Usuario verificado!
echo.

REM ========================================
REM VERIFICAR CONEXAO DO CLOUD RUN
REM ========================================
echo [4/5] Verificando se Cloud Run esta conectado ao Cloud SQL...
echo.

REM Verificar se o Cloud Run tem a conexao configurada
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(spec.template.spec.containers[0].env)" --project=%PROJECT_ID% | findstr "CLOUD_SQL_CONNECTION_NAME" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Cloud Run pode nao estar conectado ao Cloud SQL corretamente.
    echo Voce pode precisar fazer um novo deploy com: DEPLOY_TUDO_AUTOMATICO.bat
    echo.
) else (
    echo [OK] Cloud Run esta configurado para usar Cloud SQL!
    echo.
)

REM ========================================
REM EXECUTAR MIGRACOES
REM ========================================
echo [5/5] Executando migracoes no Cloud Run...
echo.

echo IMPORTANTE: Para executar migracoes, vamos usar um job temporario do Cloud Run.
echo.

REM Criar um job temporario para executar migracoes
set JOB_NAME=monpec-migrate-temp

echo Criando job temporario para migracoes...
gcloud run jobs create %JOB_NAME% ^
    --image gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^
    --region=%REGION% ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --command "python" ^
    --args "manage.py,migrate,--noinput" ^
    --memory=1Gi ^
    --cpu=1 ^
    --max-retries=1 ^
    --project=%PROJECT_ID% 2>&1 | findstr /V "already exists" || echo.

echo Executando job de migracao...
gcloud run jobs execute %JOB_NAME% --region=%REGION% --project=%PROJECT_ID% --wait

if errorlevel 1 (
    echo [AVISO] Job de migracao falhou ou nao foi necessario.
    echo As migracoes podem ser executadas automaticamente no proximo deploy.
    echo.
) else (
    echo [OK] Migracoes executadas!
    echo.
)

REM Limpar job temporario
echo Removendo job temporario...
gcloud run jobs delete %JOB_NAME% --region=%REGION% --project=%PROJECT_ID% --quiet 2>&1 | findstr /V "does not exist" || echo.

REM ========================================
REM RESUMO
REM ========================================
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo Cloud SQL:
echo   Instancia: %DB_INSTANCE%
echo   Banco: %DB_NAME%
echo   Usuario: %DB_USER%
echo.
echo Proximos passos:
echo 1. Se o Cloud Run nao estava conectado, execute: DEPLOY_TUDO_AUTOMATICO.bat
echo 2. Verifique o status: VERIFICAR_DEPLOY.bat
echo 3. Acesse a URL do sistema e teste o login
echo.
echo ========================================
echo.
pause

endlocal

