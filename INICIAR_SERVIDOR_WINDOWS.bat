@echo off
setlocal enabledelayedexpansion
title MONPEC - Servidor Windows
color 0A
echo.
echo ========================================
echo   MONPEC - SERVIDOR WINDOWS
echo   Sistema de Gestao Rural
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist manage.py (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)

REM Procurar Python
set PYTHON_CMD=
if exist python311\python.exe (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Python local encontrado
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
    ) else (
        echo [ERRO] Python nao encontrado!
        pause
        exit /b 1
    )
)

REM Parar processos na porta 8000
echo Parando processos na porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Obter IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP_LOCAL=%%a
    set IP_LOCAL=!IP_LOCAL:~1!
    goto :ip_found
)
:ip_found

echo.
echo ========================================
echo   SERVIDOR INICIANDO...
echo ========================================
echo.
echo   IP Local: %IP_LOCAL%
echo   Porta: 8000
echo   Acesse: http://%IP_LOCAL%:8000
echo   ou: http://localhost:8000
echo.
echo   Pressione Ctrl+C para parar
echo ========================================
echo.

%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows

pause

