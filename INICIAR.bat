@echo off
chcp 65001 >nul
title MONPEC - SERVIDOR
color 0A

echo ========================================
echo   MONPEC - INICIAR SERVIDOR
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM ========================================
REM PARAR SERVIDORES ANTERIORES
REM ========================================
echo [1/4] Parando servidores anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Servidores anteriores parados
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [2/4] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Usando Python local
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python não encontrado!
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
    echo [OK] Usando Python do sistema
)

%PYTHON_CMD% --version
echo.

REM ========================================
REM VERIFICAR SISTEMA
REM ========================================
echo [3/4] Verificando sistema...
%PYTHON_CMD% manage.py check --deploy >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Alguns avisos encontrados (pode ser normal)
) else (
    echo [OK] Sistema verificado
)
echo.

REM ========================================
REM INICIAR SERVIDOR
REM ========================================
echo [4/4] Iniciando servidor Django...
echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [INFO] Servidor: http://localhost:8000
echo [INFO] Login: admin / Senha: admin
echo.
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.
echo ========================================
echo.

%PYTHON_CMD% manage.py runserver 0.0.0.0:8000

if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    echo.
    pause
)


























