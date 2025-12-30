@echo off
REM Script Batch para executar o deploy completo
REM Resolve problemas de caminho e codificação

cd /d "%~dp0"

echo ========================================
echo   EXECUTANDO DEPLOY COMPLETO
echo ========================================
echo.

REM Verificar se o arquivo existe
if not exist "DEPLOY_COMPLETO.ps1" (
    echo.
    echo ❌ ERRO: Arquivo DEPLOY_COMPLETO.ps1 não encontrado!
    echo.
    echo Diretório atual: %CD%
    echo.
    echo Verificando arquivos .ps1 no diretório atual...
    dir /b *.ps1 2>nul
    echo.
    echo ========================================
    echo   SOLUÇÃO
    echo ========================================
    echo.
    echo 1. Navegue para o diretório do projeto:
    echo    cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
    echo.
    echo 2. Execute novamente:
    echo    EXECUTAR_DEPLOY.bat
    echo.
    echo OU execute diretamente:
    echo    powershell.exe -ExecutionPolicy Bypass -File "DEPLOY_COMPLETO.ps1"
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivo encontrado!
echo.
echo Executando deploy completo...
echo.

REM Executar o script PowerShell
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0DEPLOY_COMPLETO.ps1" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro durante o deploy
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Deploy completo finalizado!
pause

