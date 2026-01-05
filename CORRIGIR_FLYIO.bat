@echo off
chcp 65001 >nul
echo ========================================
echo   CORRIGIR PROBLEMAS FLY.IO
echo ========================================
echo.

REM Verificar se flyctl está instalado
where flyctl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ flyctl não está instalado!
    echo Execute: powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    pause
    exit /b 1
)

REM Verificar autenticação
flyctl auth whoami >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Você não está logado!
    echo Execute: flyctl auth login
    pause
    exit /b 1
)

echo ✅ Autenticado!
echo.

echo ========================================
echo   1. VERIFICANDO MÁQUINAS
echo ========================================
flyctl machines list -a monpec-gestaorural

echo.
echo ========================================
echo   2. INICIANDO MÁQUINAS PARADAS
echo ========================================
echo Iniciando todas as máquinas...
flyctl machines start -a monpec-gestaorural

if %ERRORLEVEL% EQU 0 (
    echo ✅ Máquinas iniciadas!
) else (
    echo ⚠️ Erro ao iniciar máquinas. Pode ser que não existam máquinas ainda.
    echo Vamos fazer deploy para criar as máquinas.
)

echo.
echo ========================================
echo   3. VERIFICANDO VARIÁVEIS DE AMBIENTE
echo ========================================
flyctl secrets list -a monpec-gestaorural

echo.
echo ⚠️ IMPORTANTE: Verifique se DATABASE_URL está configurado!
echo Se não estiver, execute: ADICIONAR_DATABASE_URL.bat
echo.

echo ========================================
echo   4. VERIFICANDO STATUS
echo ========================================
timeout /t 5 /nobreak >nul
flyctl status -a monpec-gestaorural

echo.
echo ========================================
echo   5. TESTANDO APLICAÇÃO
echo ========================================
echo Aguardando aplicação iniciar...
timeout /t 10 /nobreak >nul

echo Verificando se a aplicação está respondendo...
curl -s -o nul -w "Status: %%{http_code}\n" https://monpec-gestaorural.fly.dev/ || (
    echo ⚠️ Aplicação ainda não está respondendo.
    echo Verifique os logs: flyctl logs -a monpec-gestaorural
)

echo.
echo ========================================
echo   CORREÇÃO CONCLUÍDA
echo ========================================
echo.
echo Se ainda houver problemas:
echo 1. Execute: DEPLOY_FLYIO.bat (para fazer rebuild completo)
echo 2. Verifique logs: flyctl logs -a monpec-gestaorural
echo 3. Verifique status: flyctl status -a monpec-gestaorural
echo.
pause
