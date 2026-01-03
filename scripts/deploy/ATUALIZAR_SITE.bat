@echo off
REM Script para Atualizar o Site no Google Cloud Run
cd /d "%~dp0"

echo ========================================
echo   ATUALIZAR SITE MONPEC
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set SERVICE_NAME=monpec
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo 🔨 Construindo nova imagem Docker...
echo (Aguarde, isso pode levar alguns minutos...)
echo.

REM Build da imagem com tag latest
gcloud builds submit --tag %IMAGE_NAME%:latest --timeout=30m

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao construir imagem
    pause
    exit /b 1
)

echo.
echo ✅ Imagem construída!
echo.
echo 🚀 Atualizando serviço no Cloud Run...
echo.

REM Deploy com --no-traffic para testar primeiro (opcional)
REM Ou deploy direto para atualizar imediatamente
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10 ^
    --min-instances 1 ^
    --port 8080 ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" ^
    --clear-cache

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao atualizar serviço
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ SITE ATUALIZADO COM SUCESSO!
echo ========================================
echo.

REM Obter URL
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo URL do serviço: %SERVICE_URL%
echo.
echo ⚠️  IMPORTANTE:
echo.
echo 1. Limpe o cache do navegador (Ctrl+Shift+Delete)
echo 2. Ou use modo anônimo (Ctrl+Shift+N)
echo 3. Ou force atualização (Ctrl+F5)
echo.
echo O site pode levar alguns segundos para atualizar completamente.
echo.

pause













































