@echo off
REM ========================================
REM INICIAR SISTEMA MARCELO SANGUINO
REM ========================================
title MONPEC - Marcelo Sanguino

echo ========================================
echo   MONPEC - MARCELO SANGUINO
echo   FAZENDA CANTA GALO
echo ========================================
echo.

cd /d "%~dp0"

REM Parar processos Python
echo [INFO] Parando processos Python...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM Verificar banco
echo [INFO] Verificando banco de dados...
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo [ERRO] Banco incorreto!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [IMPORTANTE] Para acessar o sistema:
echo.
echo   URL DO LOGIN (USE ESTA):
echo   http://localhost:8000/login/
echo.
echo   OU se aparecer a landing page:
echo   - Clique em "Ja sou cliente" (canto superior direito)
echo   - OU digite na barra: /login/
echo.
echo ========================================
echo.

%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

pause


