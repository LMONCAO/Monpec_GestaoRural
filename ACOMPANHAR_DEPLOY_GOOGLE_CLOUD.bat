@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para acompanhar deploy no Google Cloud Console
REM Abre os links diretos para ver builds, logs e erros

echo ========================================
echo   ACOMPANHAR DEPLOY NO GOOGLE CLOUD
echo   Abrindo links do Google Cloud Console
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

echo ========================================
echo   LINKS DO GOOGLE CLOUD CONSOLE
echo ========================================
echo.
echo 1. Cloud Build (ver builds e erros):
echo    https://console.cloud.google.com/cloud-build/builds?project=%PROJECT_ID%
echo.
echo 2. Cloud Run (ver servico e revisoes):
echo    https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%?project=%PROJECT_ID%
echo.
echo 3. Logs do Cloud Run (ver logs em tempo real):
echo    https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22
echo.
echo 4. Erros do Cloud Run (filtrar apenas erros):
echo    https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22%20AND%20severity%3E%3D%22ERROR%22
echo.
echo 5. Container Registry (ver imagens):
echo    https://console.cloud.google.com/gcr/images/%PROJECT_ID%?project=%PROJECT_ID%
echo.

echo ========================================
echo   ABRINDO LINKS NO NAVEGADOR
echo ========================================
echo.
echo Deseja abrir os links no navegador? (S/N)
set /p ABRIR_LINKS=

if /i "!ABRIR_LINKS!"=="S" (
    echo.
    echo Abrindo Cloud Build...
    start https://console.cloud.google.com/cloud-build/builds?project=%PROJECT_ID%
    timeout /t 2 /nobreak >nul
    
    echo Abrindo Cloud Run...
    start https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%?project=%PROJECT_ID%
    timeout /t 2 /nobreak >nul
    
    echo Abrindo Logs...
    start https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22
    timeout /t 2 /nobreak >nul
    
    echo Abrindo Erros...
    start https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22%20AND%20severity%3E%3D%22ERROR%22
    
    echo.
    echo [OK] Links abertos no navegador!
    echo.
    echo IMPORTANTE:
    echo - Os links abrem em abas separadas
    echo - Atualize as paginas para ver informacoes em tempo real
    echo - Na pagina de Logs, clique em "Stream logs" para ver em tempo real
    echo - Na pagina de Erros, voce vera apenas os erros
    echo.
) else (
    echo.
    echo Copie os links acima e cole no navegador manualmente
    echo.
)

echo ========================================
echo   COMANDOS PARA VER ERROS NO TERMINAL
echo ========================================
echo.
echo Para ver erros recentes:
echo   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND severity>=ERROR" --limit=50 --project=%PROJECT_ID%
echo.
echo Para ver logs em tempo real:
echo   gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --project=%PROJECT_ID%
echo.
echo Para ver status do ultimo build:
echo   gcloud builds list --limit=1 --project=%PROJECT_ID%
echo.

pause

endlocal

