@echo off
REM ============================================================================
REM DEPLOY AUTOMÁTICO - GOOGLE CLOUD (Windows)
REM ============================================================================
REM Execute este arquivo .bat para fazer deploy automático no Google Cloud
REM ============================================================================

echo ==========================================
echo 🚀 DEPLOY AUTOMÁTICO - GOOGLE CLOUD
echo ==========================================
echo.

REM Verificar se PowerShell está disponível
powershell -ExecutionPolicy Bypass -File "DEPLOY_GOOGLE_CLOUD_COMPLETO_AUTOMATICO.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro no deploy!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Deploy concluído!
echo.
pause



