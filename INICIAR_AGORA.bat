@echo off
title MONPEC - Servidor Django
color 0A

echo ========================================
echo   INICIANDO SERVIDOR MONPEC
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretorio: %CD%
echo.

REM Parar processos Python
echo [INFO] Parando processos Python...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar configuração
echo [INFO] Verificando configuração Django...
python manage.py check
if errorlevel 1 (
    echo [ERRO] Erro na configuracao Django!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo [INFO] URL: http://localhost:8000/
echo [INFO] Para parar: Ctrl+C ou feche esta janela
echo.
echo ========================================
echo.

REM Iniciar servidor
python manage.py runserver 0.0.0.0:8000

pause
























