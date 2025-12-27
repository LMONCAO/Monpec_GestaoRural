@echo off
REM ==========================================
REM SCRIPT DE DEPLOY E CORREÇÃO COMPLETA
REM Sistema MONPEC - Gestão Rural
REM ==========================================

title MONPEC - Deploy e Correção

echo ========================================
echo 🚀 DEPLOY E CORREÇÃO DO SISTEMA MONPEC
echo ========================================
echo.

cd /d "%~dp0"

REM Executar script PowerShell
powershell.exe -ExecutionPolicy Bypass -File "DEPLOY_E_CORRIGIR.ps1"

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar o script de deploy
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ DEPLOY CONCLUÍDO!
echo ========================================
echo.
echo Deseja iniciar o servidor agora? (S/N)
set /p iniciar=

if /i "%iniciar%"=="S" (
    echo.
    echo Iniciando servidor...
    call INICIAR_SERVIDOR_PRODUCAO.bat
) else (
    echo.
    echo Para iniciar o servidor depois, execute:
    echo   INICIAR_SERVIDOR_PRODUCAO.bat
    echo.
    pause
)









