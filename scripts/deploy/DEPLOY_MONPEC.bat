@echo off
chcp 65001 >nul
echo ========================================
echo DEPLOY MONPEC - Google Cloud Run
echo ========================================
echo.

REM Verificar se gcloud está instalado
where gcloud >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: gcloud CLI nao encontrado!
    echo Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo Verificando autenticacao...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Fazendo login no Google Cloud...
    gcloud auth login
)

echo.
echo Verificando projeto...
gcloud config get-value project
echo.
set /p PROJECT_ID="Digite o PROJECT_ID do Google Cloud (ou pressione Enter para usar o atual): "
if "%PROJECT_ID%"=="" (
    for /f "tokens=*" %%i in ('gcloud config get-value project') do set PROJECT_ID=%%i
)
echo Projeto: %PROJECT_ID%

echo.
echo Configurando projeto...
gcloud config set project %PROJECT_ID%

echo.
echo ========================================
echo 1. Fazendo build da imagem Docker...
echo ========================================
docker build -t gcr.io/%PROJECT_ID%/monpec:latest .

if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao fazer build da imagem!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 2. Enviando imagem para Container Registry...
echo ========================================
docker push gcr.io/%PROJECT_ID%/monpec:latest

if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao enviar imagem!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 3. Fazendo deploy no Cloud Run...
echo ========================================
gcloud run deploy monpec ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" ^
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10 ^
    --min-instances 1 ^
    --port 8080

if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao fazer deploy!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 4. Configurando dominio personalizado...
echo ========================================
echo.
echo IMPORTANTE: Configure o dominio monpec.com.br no Cloud Run:
echo 1. Acesse: https://console.cloud.google.com/run
echo 2. Selecione o servico 'monpec'
echo 3. Vá em "DOMAIN MAPPING"
echo 4. Adicione: monpec.com.br e www.monpec.com.br
echo.
echo OU execute manualmente:
echo gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
echo gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
echo.

echo ========================================
echo DEPLOY CONCLUIDO!
echo ========================================
echo.
echo IMPORTANTE: Configure as variaveis de ambiente no Cloud Run:
echo - MERCADOPAGO_ACCESS_TOKEN
echo - MERCADOPAGO_PUBLIC_KEY
echo - SECRET_KEY
echo - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
echo.
echo Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec
echo.
pause





























