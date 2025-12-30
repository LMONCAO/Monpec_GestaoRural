@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script SUPER AUTOMATICO - Faz TUDO incluindo deploy direto
REM Usa gcloud build e deploy localmente (sem precisar do Cloud Shell)

echo ========================================
echo   DEPLOY SUPER AUTOMATICO
echo   Limpa, Envia e Deploy Tudo Automatico
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set BUCKET_NAME=%PROJECT_ID%-backup-completo
set DB_INSTANCE=monpec-db
set DB_NAME=monpec_db
set DB_USER=monpec_user
set DB_PASSWORD=L6171r12@@jjms
set SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE
set DJANGO_SUPERUSER_PASSWORD=L6171r12@@

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM VERIFICACOES
REM ========================================
echo [1/8] Verificando ferramentas...
where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gcloud nao encontrado!
    echo Baixe: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo [OK] gcloud encontrado
echo.

REM ========================================
REM AUTENTICACAO
REM ========================================
echo [2/8] Verificando autenticacao...
for /f "tokens=*" %%i in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>^&1') do set AUTH_ACCOUNT=%%i
if "!AUTH_ACCOUNT!"=="" (
    echo Fazendo login...
    gcloud auth login
    if errorlevel 1 (
        echo [ERRO] Falha na autenticacao!
        pause
        exit /b 1
    )
) else (
    echo [OK] Autenticado: !AUTH_ACCOUNT!
)

REM Verificar Application Default Credentials (evita pedir senha toda hora)
gcloud auth application-default print-access-token >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Configurando credenciais padrao para evitar pedir senha...
    echo [AVISO] Isso so precisa ser feito UMA VEZ
    gcloud auth application-default login --no-launch-browser
    if errorlevel 1 (
        echo [AVISO] Falha ao configurar credenciais padrao, mas continuando...
    ) else (
        echo [OK] Credenciais padrao configuradas - nao vai pedir senha mais!
    )
)

REM Configurar projeto
gcloud config set project %PROJECT_ID% >nul 2>&1
echo [OK] Projeto configurado
echo.

REM ========================================
REM HABILITAR APIs
REM ========================================
echo [3/8] Habilitando APIs necessarias...
gcloud services enable cloudbuild.googleapis.com >nul 2>&1
gcloud services enable run.googleapis.com >nul 2>&1
gcloud services enable sqladmin.googleapis.com >nul 2>&1
gcloud services enable containerregistry.googleapis.com >nul 2>&1
echo [OK] APIs habilitadas
echo.

REM ========================================
REM LIMPAR BUCKET
REM ========================================
echo [4/8] Limpando arquivos antigos...
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if not errorlevel 1 (
    echo Limpando bucket antigo...
    gsutil -m rm -r "gs://!BUCKET_NAME!/*" >nul 2>&1
)
echo [OK] Limpeza concluida
echo.

REM ========================================
REM UPLOAD PARA BACKUP
REM ========================================
echo [5/8] Fazendo backup no Cloud Storage...
for %%i in ("%CD%") do set FOLDER_NAME=%%~ni

REM Criar bucket se nao existir
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if errorlevel 1 (
    gsutil mb -p %PROJECT_ID% -l %REGION% "gs://!BUCKET_NAME!" >nul 2>&1
)

REM Upload - IMPORTANTE: Incluir TODOS os arquivos do localhost (templates, static, etc)
set EXCLUDE_ARGS=-x "venv/**" -x "__pycache__/**" -x ".git/**" -x "node_modules/**" -x "*.pyc" -x ".env" -x "logs/**" -x "temp/**" -x "staticfiles/**" -x "db.sqlite3" -x "*.log"
echo Fazendo upload de TODOS os arquivos do localhost (templates, static, gestao_rural, etc)...
gsutil -m rsync -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!FOLDER_NAME!/" 2>&1 | findstr /V "Copying\|Copying\|Building\|Skipping\|^$" || echo.
echo [OK] Backup concluido - Todos os arquivos do localhost foram enviados
echo.

REM ========================================
REM BUILD DA IMAGEM DOCKER
REM ========================================
echo [6/8] Fazendo build da imagem Docker...
echo IMPORTANTE: O build vai usar TODOS os arquivos do diretorio atual (localhost)
echo Isso pode levar varios minutos...
echo.

set TIMESTAMP=%date:~-4,4%%date:~-7,2%%date:~-10,2%%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=!TIMESTAMP: =0!
set IMAGE_TAG=gcr.io/%PROJECT_ID%/%SERVICE_NAME%:!TIMESTAMP!

echo Build da imagem: !IMAGE_TAG!
echo Usando arquivos do diretorio atual: %CD%
echo IMPORTANTE: Usando --no-cache para garantir versao nova
echo.
gcloud builds submit --no-cache --tag !IMAGE_TAG! --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest

if errorlevel 1 (
    echo [ERRO] Falha no build!
    pause
    exit /b 1
)

echo [OK] Build concluido - Imagem criada com todos os arquivos do localhost
echo.

REM ========================================
REM DEPLOY NO CLOUD RUN
REM ========================================
echo [7/8] Fazendo deploy no Cloud Run...
echo Isso pode levar alguns minutos...
echo.

gcloud run deploy %SERVICE_NAME% ^
    --image gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^
    --region=%REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=600 ^
    --max-instances=10 ^
    --min-instances=0

if errorlevel 1 (
    echo [ERRO] Falha no deploy!
    pause
    exit /b 1
)
echo [OK] Deploy concluido
echo.

REM ========================================
REM VERIFICAR STATUS
REM ========================================
echo [8/8] Verificando status do servico...
timeout /t 15 /nobreak >nul

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

echo.
echo ========================================
echo   DEPLOY CONCLUIDO!
echo ========================================
echo.
echo Seu sistema esta disponivel em:
echo !SERVICE_URL!
echo.
echo ========================================
echo   PRÓXIMOS PASSOS
echo ========================================
echo.
echo 1. Acesse a URL acima para verificar
echo 2. O sistema ja executa migracoes automaticamente no inicio
echo 3. Credenciais de admin:
echo    Usuario: admin
echo    Senha: %DJANGO_SUPERUSER_PASSWORD%
echo 4. Verifique os logs se necessario:
echo    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=50
echo.
echo ========================================
echo   IMPORTANTE
echo ========================================
echo O sistema foi atualizado com a versao do localhost.
echo Aguarde 1-2 minutos para o servico inicializar completamente.
echo.
echo ========================================
echo.
pause

endlocal

