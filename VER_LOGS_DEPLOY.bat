@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para ver logs em tempo real do deploy

echo ========================================
echo   LOGS DO DEPLOY - TEMPO REAL
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.
echo Mostrando logs em tempo real (pressione Ctrl+C para parar)...
echo.

REM Mostrar logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --project=%PROJECT_ID% --format="table(timestamp,severity,textPayload,jsonPayload.message)"

pause

