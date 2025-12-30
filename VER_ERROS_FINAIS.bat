@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script que mostra apenas os erros finais do deploy
REM Útil para ver o que deu errado no final do processo

echo ========================================
echo   ERROS FINAIS DO DEPLOY
echo   Mostrando apenas erros
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM ERROS DO BUILD
REM ========================================
echo ========================================
echo   ERROS DO BUILD
echo ========================================
echo.
echo Verificando builds que falharam...
echo.
gcloud builds list --limit=5 --format="table(id,status,createTime,statusDetail)" --project=%PROJECT_ID% --filter="status=FAILURE OR status=INTERNAL_ERROR OR status=TIMEOUT" 2>nul
echo.

REM ========================================
REM ERROS DO SERVICO
REM ========================================
echo ========================================
echo   ERROS DO SERVICO (ULTIMAS 30 LINHAS)
echo ========================================
echo.
echo Buscando erros, excecoes e falhas nos logs...
echo.
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND (severity>=ERROR OR textPayload=~\"error\" OR textPayload=~\"Error\" OR textPayload=~\"ERROR\" OR textPayload=~\"Exception\" OR textPayload=~\"Traceback\" OR textPayload=~\"Failed\" OR textPayload=~\"failed\" OR textPayload=~\"FAILED\")" --limit=30 --format="table(timestamp,severity,textPayload)" --project=%PROJECT_ID% 2>nul | findstr /V "Listed 0\|^$" || echo [OK] Nenhum erro encontrado!
echo.

REM ========================================
REM STATUS DAS CONDICOES
REM ========================================
echo ========================================
echo   STATUS DAS CONDICOES DO SERVICO
echo ========================================
echo.
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].reason,status.conditions[0].message)" --project=%PROJECT_ID% 2>nul
echo.

REM ========================================
REM REVISOES COM PROBLEMAS
REM ========================================
echo ========================================
echo   REVISOES COM PROBLEMAS
echo ========================================
echo.
echo Revisoes que falharam ou tem problemas:
echo.
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=5 --format="table(metadata.name,status.conditions[0].status,status.conditions[0].reason,status.conditions[0].message)" --project=%PROJECT_ID% 2>nul | findstr /V "True\|^$" || echo [OK] Todas as revisoes estao funcionando!
echo.

REM ========================================
REM LINKS DO GOOGLE CLOUD CONSOLE
REM ========================================
echo ========================================
echo   VER MAIS DETALHES NO GOOGLE CLOUD
echo ========================================
echo.
echo Para ver mais detalhes, acesse:
echo.
echo 1. Erros nos Logs:
echo    https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22%20AND%20severity%3E%3D%22ERROR%22
echo.
echo 2. Builds que falharam:
echo    https://console.cloud.google.com/cloud-build/builds?project=%PROJECT_ID%&query=status%3D%22FAILURE%22
echo.
echo 3. Cloud Run (ver revisoes):
echo    https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%?project=%PROJECT_ID%
echo.

echo Deseja abrir os links no navegador? (S/N)
set /p ABRIR_LINKS=

if /i "!ABRIR_LINKS!"=="S" (
    echo.
    echo Abrindo links...
    start https://console.cloud.google.com/logs/query?project=%PROJECT_ID%&query=resource.type%3D%22cloud_run_revision%22%20AND%20resource.labels.service_name%3D%22%SERVICE_NAME%22%20AND%20severity%3E%3D%22ERROR%22
    timeout /t 2 /nobreak >nul
    start https://console.cloud.google.com/cloud-build/builds?project=%PROJECT_ID%&query=status%3D%22FAILURE%22
    timeout /t 2 /nobreak >nul
    start https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%?project=%PROJECT_ID%
    echo.
    echo [OK] Links abertos no navegador!
    echo.
)

echo ========================================
echo.
pause

endlocal

