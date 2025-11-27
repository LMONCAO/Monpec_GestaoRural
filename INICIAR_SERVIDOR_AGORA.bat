@echo off
REM ========================================
REM INICIAR SERVIDOR MONPEC - RAPIDO
REM ========================================
title MONPEC - Iniciando Servidor

echo ========================================
echo   INICIANDO SERVIDOR MONPEC
echo   Marcelo Sanguino / Fazenda Canta Galo
echo ========================================
echo.

cd /d "%~dp0"

REM Parar processos Python
echo [INFO] Parando processos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM Verificar banco de dados
echo [INFO] Verificando banco de dados (Marcelo Sanguino / Fazenda Canta Galo)...
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo [ERRO] Banco de dados incorreto!
    echo [INFO] Use INICIAR_SISTEMA_CORRETO.bat para mais detalhes
    echo.
    pause
    exit /b 1
)

echo [OK] Banco de dados correto!
echo.
echo ========================================
echo   INICIANDO SERVIDOR
echo ========================================
echo [INFO] URL: http://127.0.0.1:8000/
echo [INFO] Para parar: feche esta janela ou Ctrl+C
echo.

REM Iniciar servidor
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

pause

