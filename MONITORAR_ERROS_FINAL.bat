@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script que monitora o deploy e mostra erros no final
REM Fica acompanhando e mostra resumo de erros quando terminar

echo ========================================
echo   MONITORAR DEPLOY E MOSTRAR ERROS
echo   Acompanha e mostra erros no final
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
echo   ACOMPANHANDO DEPLOY
echo ========================================
echo.
echo Este script vai:
echo 1. Monitorar o build em tempo real
echo 2. Monitorar o deploy
echo 3. Mostrar erros no final (se houver)
echo.
echo Pressione Ctrl+C a qualquer momento para parar e ver erros
echo.
timeout /t 5 /nobreak >nul

REM Verificar se há build em andamento
echo Verificando builds em andamento...
echo.
gcloud builds list --limit=1 --format="table(id,status,createTime)" --project=%PROJECT_ID%
echo.

echo Deseja acompanhar o build mais recente? (S/N)
set /p ACOMPANHAR_BUILD=

if /i "!ACOMPANHAR_BUILD!"=="S" (
    echo.
    echo ========================================
    echo   ACOMPANHANDO BUILD
    echo   Pressione Ctrl+C quando terminar
    echo ========================================
    echo.
    gcloud builds log --stream --project=%PROJECT_ID%
    echo.
    echo Build finalizado.
    echo.
    timeout /t 3 /nobreak >nul
)

REM Verificar erros do build
echo ========================================
echo   VERIFICANDO ERROS DO BUILD
echo ========================================
echo.
echo Buscando erros nos builds recentes...
echo.
gcloud builds list --limit=5 --format="table(id,status,createTime)" --project=%PROJECT_ID%
echo.

REM Verificar erros do servico
echo ========================================
echo   VERIFICANDO ERROS DO SERVICO
echo ========================================
echo.
echo Buscando erros nos logs do servico (ultimas 50 linhas)...
echo.
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND (severity>=ERROR OR textPayload=~\"error\" OR textPayload=~\"Error\" OR textPayload=~\"ERROR\" OR textPayload=~\"Exception\" OR textPayload=~\"Traceback\" OR textPayload=~\"Failed\")" --limit=50 --format="table(timestamp,severity,textPayload)" --project=%PROJECT_ID% 2>nul | findstr /V "Listed 0\|^$" || echo [OK] Nenhum erro encontrado nos logs recentes!
echo.

REM Verificar status do servico
echo ========================================
echo   STATUS DO SERVICO
echo ========================================
echo.
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [AVISO] Servico nao encontrado ou ainda nao foi deployado
) else (
    echo [OK] URL: !SERVICE_URL!
    echo.
    echo Condicoes do servico:
    gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].reason,status.conditions[0].message)" --project=%PROJECT_ID% 2>nul
)
echo.

REM Verificar revisoes com problemas
echo ========================================
echo   REVISOES COM PROBLEMAS
echo ========================================
echo.
echo Verificando revisoes que falharam...
echo.
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=5 --format="table(metadata.name,status.conditions[0].status,status.conditions[0].reason,metadata.creationTimestamp)" --project=%PROJECT_ID% 2>nul
echo.

REM Resumo final
echo ========================================
echo   RESUMO FINAL
echo ========================================
echo.
echo Para ver mais detalhes:
echo 1. Execute: ACOMPANHAR_DEPLOY_GOOGLE_CLOUD.bat (abre links do Google Cloud Console)
echo 2. Execute: VERIFICAR_ERROS_DEPLOY.bat (busca erros especificos)
echo 3. Execute: VER_LOGS_TEMPO_REAL.bat (ver logs em tempo real)
echo.
echo Links do Google Cloud Console:
echo - Builds: https://console.cloud.google.com/cloud-build/builds?project=%PROJECT_ID%
echo - Cloud Run: https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%?project=%PROJECT_ID%
echo - Logs: https://console.cloud.google.com/logs/query?project=%PROJECT_ID%
echo.

pause

endlocal

