@echo off
chcp 65001 >nul
echo ========================================
echo   DIAGNÓSTICO FLY.IO
echo ========================================
echo.

REM Verificar se flyctl está instalado
where flyctl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ flyctl não está instalado!
    echo.
    echo Para instalar o flyctl:
    echo 1. Acesse: https://fly.io/docs/getting-started/installing-flyctl/
    echo 2. Ou execute: powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    echo.
    pause
    exit /b 1
)

echo ✅ flyctl encontrado!
echo.

REM Verificar se está logado
echo Verificando autenticação...
flyctl auth whoami >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Você não está logado no Fly.io!
    echo.
    echo Execute: flyctl auth login
    echo.
    pause
    exit /b 1
)

echo ✅ Autenticado no Fly.io!
echo.

REM Verificar status do app
echo ========================================
echo   STATUS DO APP
echo ========================================
flyctl status -a monpec-gestaorural

echo.
echo ========================================
echo   LISTA DE MÁQUINAS
echo ========================================
flyctl machines list -a monpec-gestaorural

echo.
echo ========================================
echo   VARIÁVEIS DE AMBIENTE
echo ========================================
flyctl secrets list -a monpec-gestaorural

echo.
echo ========================================
echo   LOGS RECENTES
echo ========================================
echo Últimas 50 linhas de log:
flyctl logs -a monpec-gestaorural --limit 50

echo.
echo ========================================
echo   DIAGNÓSTICO COMPLETO
echo ========================================
echo.
echo ✅ Verificações concluídas!
echo.
echo PROBLEMAS COMUNS:
echo 1. Máquinas paradas (auto_stop_machines = true)
echo    Solução: Execute CORRIGIR_FLYIO.bat
echo.
echo 2. DATABASE_URL não configurado
echo    Solução: Execute ADICIONAR_DATABASE_URL.bat
echo.
echo 3. Build antigo ou com erros
echo    Solução: Execute DEPLOY_FLYIO.bat
echo.
pause
