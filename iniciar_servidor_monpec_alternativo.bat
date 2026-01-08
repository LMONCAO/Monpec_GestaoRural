@echo off
chcp 65001 >nul
title MONPEC - Servidor Alternativo

echo ========================================
echo 🚀 SISTEMA MONPEC - ACESSO ALTERNATIVO
echo ========================================
echo.
echo Este script oferece múltiplas formas de acesso
echo caso o navegador tenha problemas com localhost.
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo Diretório atual: %CD%
    pause
    exit /b 1
)

echo [INFO] Diretório do projeto: %CD%
echo.

REM Parar processos na porta 8000
echo [INFO] Liberando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Carregar configurações do banco oficial
echo [INFO] Carregando configurações do banco oficial...
call config_monpec_oficial.bat

echo.
echo ========================================
echo 🌐 OPÇÕES DE ACESSO DISPONÍVEIS:
echo ========================================
echo.
echo 1. http://localhost:8000/          (Padrão)
echo 2. http://127.0.0.1:8000/          (IP local)
echo 3. http://0.0.0.0:8000/            (Todos IPs)
echo.
echo 📋 DICAS PARA ACESSO:
echo • Use apenas HTTP (não HTTPS)
echo • Tente um navegador diferente
echo • Limpe o cache do navegador
echo • Desative extensões temporariamente
echo.

REM Iniciar servidor
echo ========================================
echo   🚀 INICIANDO SERVIDOR DJANGO
echo ========================================
echo.
echo Servidor iniciando... Aguarde alguns segundos.
echo.
echo Quando aparecer "Starting development server"
echo o servidor estará pronto para acesso.
echo.

python manage.py runserver 0.0.0.0:8000

echo.
echo [INFO] Servidor encerrado.
echo.
echo Se ainda tiver problemas de acesso:
echo 1. Execute: iniciar_servidor_monpec_oficial.bat
echo 2. Ou tente: python manage.py runserver 127.0.0.1:8000
echo 3. Acesse: http://127.0.0.1:8000/
echo.
pause


