@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para ver logs do servidor em tempo real
REM Fica aberto mostrando logs conforme aparecem

echo ========================================
echo   LOGS DO SERVIDOR - TEMPO REAL
echo   Pressione Ctrl+C para sair
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo.
echo Mostrando logs em tempo real...
echo Pressione Ctrl+C para parar
echo.
echo ========================================
echo.

REM Mostrar logs em tempo real (não fecha automaticamente)
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --project=%PROJECT_ID% --format="table(timestamp,severity,textPayload)"

REM Se o comando acima terminar (erro), mostrar mensagem
echo.
echo ========================================
echo Logs finalizados ou erro ao conectar
echo ========================================
pause

endlocal

