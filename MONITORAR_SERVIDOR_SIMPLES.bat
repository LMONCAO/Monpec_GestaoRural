@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script SIMPLES que fica aberto mostrando informações do servidor
REM Atualiza automaticamente - NÃO FECHA

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

:INICIO
cls
echo ========================================
echo   MONITOR DO SERVIDOR
echo   Atualizado: %date% %time%
echo   Pressione Ctrl+C para sair
echo ========================================
echo.

echo [STATUS DO SERVICO]
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>nul') do (
    echo URL: %%i
)
echo.

echo [ULTIMO BUILD]
for /f "tokens=*" %%i in ('gcloud builds list --limit=1 --format="value(status)" --project=%PROJECT_ID% 2^>nul') do (
    echo Status: %%i
)
echo.

echo [LOGS RECENTES - Ultimas 5 linhas]
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=5 --format="value(textPayload)" --project=%PROJECT_ID% 2>nul
echo.

echo ========================================
echo Atualizando em 10 segundos...
echo Pressione Ctrl+C para sair
echo ========================================

timeout /t 10 /nobreak >nul 2>nul
goto INICIO

