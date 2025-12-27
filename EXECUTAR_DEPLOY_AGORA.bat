@echo off
echo ========================================
echo DEPLOY AUTOMATICO - MONPEC.COM.BR
echo ========================================
echo.
echo Executando deploy completo...
echo.

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -File "DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"

pause










