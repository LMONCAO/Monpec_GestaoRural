@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   VERIFICAR STATUS DO DEPLOY
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo ???? Status do servi??o:
echo.
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.url)"
echo.

echo ???? ??ltimos logs (10 linhas):
echo.
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=10 --format="table(timestamp,severity,textPayload)" --project=%PROJECT_ID%
echo.

echo ???? Erros recentes:
echo.
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME% AND severity>=ERROR" --limit=5 --format="value(textPayload)" --project=%PROJECT_ID%
echo.

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" 2^>nul') do echo ???? URL: %%i

pause