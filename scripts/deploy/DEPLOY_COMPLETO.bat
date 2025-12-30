@echo off
REM Script de Deploy Completo - MONPEC para Google Cloud Run
REM Este script executa o deploy completo via PowerShell

cd /d "%~dp0"

echo ========================================
echo   DEPLOY COMPLETO - MONPEC
echo   Google Cloud Run
echo ========================================
echo.

REM Verificar se PowerShell está disponível
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PowerShell não encontrado
    echo Por favor, execute o script DEPLOY_COMPLETO.ps1 manualmente
    pause
    exit /b 1
)

REM Executar script PowerShell
echo Executando deploy completo...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0DEPLOY_COMPLETO.ps1" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro durante o deploy
    pause
    exit /b 1
)

echo.
echo ✅ Deploy completo finalizado!
pause










































