@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   DEPLOY R??PIDO - GOOGLE CLOUD RUN
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set IMAGE_TAG=gcr.io/%PROJECT_ID%/monpec:latest

echo ???? Build e Deploy em um ??nico comando...
echo    Isso pode levar 10-15 minutos...
echo.

REM Build e Deploy em um comando
gcloud builds submit --tag %IMAGE_TAG% --timeout=1800s . && gcloud run deploy %SERVICE_NAME% --image %IMAGE_TAG% --region=%REGION% --platform=managed --allow-unauthenticated --memory=2Gi --cpu=2 --timeout=600

if errorlevel 1 (
    echo.
    echo ??? ERRO no deploy!
    pause
    exit /b 1
)

echo.
echo ??? Deploy conclu??do!
echo.

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" 2^>nul') do echo ???? URL: %%i

pause