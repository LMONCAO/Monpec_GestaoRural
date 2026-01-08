@echo off
chcp 65001 >nul
title MONPEC - Servidor HTTPS

echo ========================================
echo 🔒 SISTEMA MONPEC - SERVIDOR HTTPS
echo ========================================
echo.
echo Servidor com suporte HTTPS para desenvolvimento
echo Certificado auto-gerado (aceite o aviso de segurança)
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
echo 🔒 SERVIDOR HTTPS INICIANDO
echo ========================================
echo.
echo ⚠️  AVISO IMPORTANTE:
echo Quando aparecer "Starting development server with SSL"
echo o servidor estará pronto.
echo.
echo 🔐 O navegador mostrará aviso de certificado não confiável
echo Clique em "Avançado" → "Continuar para localhost (não seguro)"
echo ou "Aceitar o risco e continuar"
echo.
echo 🌐 URLs disponíveis:
echo    https://localhost:8000/      (HTTPS - recomendado)
echo    http://localhost:8000/       (HTTP - fallback)
echo    https://127.0.0.1:8000/      (HTTPS alternativo)
echo.

python manage.py runsslserver 0.0.0.0:8000

echo.
echo [INFO] Servidor HTTPS encerrado.
pause


