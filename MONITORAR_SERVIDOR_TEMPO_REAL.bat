@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script que fica aberto mostrando informações do servidor em tempo real
REM Atualiza automaticamente a cada 10 segundos

echo ========================================
echo   MONITOR DO SERVIDOR - TEMPO REAL
echo   Pressione Ctrl+C para sair
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set INTERVALO=10

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo [CONFIG] Atualizando a cada %INTERVALO% segundos
echo.
echo Pressione Ctrl+C para parar o monitoramento
echo.
timeout /t 3 /nobreak >nul

:LOOP
cls
echo ========================================
echo   MONITOR DO SERVIDOR - TEMPO REAL
echo   Atualizado em: %date% %time%
echo   Pressione Ctrl+C para sair
echo ========================================
echo.

REM ========================================
REM STATUS DO SERVICO
REM ========================================
echo [STATUS DO SERVICO]
echo ----------------------------------------
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [AVISO] Servico nao encontrado ou ainda nao foi deployado
) else (
    echo [OK] URL: !SERVICE_URL!
    echo.
    echo Condicoes do servico:
    gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status)" --project=%PROJECT_ID% 2>nul
)
echo.

REM ========================================
REM BUILDS RECENTES
REM ========================================
echo [BUILDS RECENTES]
echo ----------------------------------------
gcloud builds list --limit=3 --format="table(id,status,createTime,duration)" --project=%PROJECT_ID% 2>nul
echo.

REM ========================================
REM REVISOES RECENTES
REM ========================================
echo [REVISOES RECENTES]
echo ----------------------------------------
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=3 --format="table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)" --project=%PROJECT_ID% 2>nul
echo.

REM ========================================
REM LOGS RECENTES (ULTIMAS 10 LINHAS)
REM ========================================
echo [LOGS RECENTES - Ultimas 10 linhas]
echo ----------------------------------------
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=10 --format="table(timestamp,severity,textPayload)" --project=%PROJECT_ID% 2>nul | findstr /V "Listed 0\|^$" || echo Nenhum log encontrado ainda.
echo.

REM ========================================
REM PROXIMA ATUALIZACAO
REM ========================================
echo ========================================
echo Proxima atualizacao em %INTERVALO% segundos...
echo Pressione Ctrl+C para sair
echo ========================================

timeout /t %INTERVALO% /nobreak >nul
goto LOOP
