@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para verificar erros especificos no deploy

echo ========================================
echo   VERIFICAR ERROS NO DEPLOY
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

REM ========================================
REM VERIFICAR ERROS NOS LOGS
REM ========================================
echo [1/3] Buscando erros nos logs (ultimas 50 linhas)...
echo.

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND (severity>=ERROR OR textPayload=~\"error\" OR textPayload=~\"Error\" OR textPayload=~\"ERROR\" OR textPayload=~\"Exception\" OR textPayload=~\"Traceback\")" --limit=50 --format="table(timestamp,severity,textPayload,jsonPayload.message)" --project=%PROJECT_ID% 2>&1 | findstr /V "Listed 0\|^$" || echo [OK] Nenhum erro encontrado nos logs recentes!
echo.

REM ========================================
REM VERIFICAR STATUS DAS CONDICOES
REM ========================================
echo [2/3] Verificando condicoes do servico...
echo.

gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].reason,status.conditions[0].message)" --project=%PROJECT_ID%
echo.

REM ========================================
REM VERIFICAR BUILD RECENTE
REM ========================================
echo [3/3] Verificando ultimo build da imagem...
echo.

gcloud builds list --limit=1 --format="table(id,status,createTime,source.repoSource.branchName)" --project=%PROJECT_ID%
echo.

REM ========================================
REM VERIFICAR REVISAO MAIS RECENTE
REM ========================================
echo Verificando revisao mais recente...
echo.

for /f "tokens=*" %%i in ('gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="value(metadata.name)" --project=%PROJECT_ID% 2^>^&1') do set LATEST_REVISION=%%i

if "!LATEST_REVISION!"=="" (
    echo [ERRO] Nenhuma revisao encontrada!
) else (
    echo Revisao mais recente: !LATEST_REVISION!
    echo.
    echo Detalhes da revisao:
    gcloud run revisions describe !LATEST_REVISION! --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].reason,status.conditions[0].message)" --project=%PROJECT_ID%
)
echo.

REM ========================================
REM RESUMO
REM ========================================
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo Se encontrar erros, verifique:
echo 1. Logs completos: VER_LOGS_DEPLOY.bat
echo 2. Status geral: VERIFICAR_DEPLOY.bat
echo 3. Builds: gcloud builds list --limit=10
echo.
echo ========================================
echo.
pause

endlocal

