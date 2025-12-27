@echo off
chcp 65001 >nul
echo ==========================================
echo 🚀 DEPLOY AUTOMÁTICO - GOOGLE CLOUD
echo ==========================================
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo ❌ ERRO: manage.py não encontrado!
    echo Execute este arquivo na pasta do projeto Django
    pause
    exit /b 1
)

echo ✅ Diretório correto encontrado!
echo.

REM Executar script PowerShell
echo 🔷 Executando deploy automático...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0DEPLOY_GOOGLE_CLOUD_COMPLETO_AUTOMATICO.ps1"

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



