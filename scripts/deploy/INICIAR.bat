@echo off
chcp 65001 >nul
title MONPEC - SERVIDOR
color 0A

echo ========================================
echo   MONPEC - INICIAR SERVIDOR
echo   Sistema de Gestao Rural
echo ========================================
echo.

cd /d "%~dp0\..\.."
echo [INFO] Diretorio: %CD%
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo [INFO] Instale Python 3.11+ e tente novamente
    pause
    exit /b 1
)
python --version
echo [OK] Python encontrado
echo.

REM ========================================
REM VERIFICAR MIGRACOES
REM ========================================
echo [2/3] Verificando migracoes...
python manage.py migrate --no-input
if errorlevel 1 (
    echo [AVISO] Erro ao executar migracoes
) else (
    echo [OK] Migracoes verificadas
)
echo.

REM ========================================
REM INICIAR SERVIDOR
REM ========================================
echo [3/3] Iniciando servidor Django...
echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [INFO] Servidor: http://localhost:8000
echo [INFO] Acesso na rede: http://192.168.0.100:8000 (ajuste o IP)
echo.
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    echo.
    pause
)
<<<<<<< Updated upstream















<<<<<<< HEAD











=======
>>>>>>> 82f662d03a852eab216d20cd9d12193f5dbd2881
=======
>>>>>>> Stashed changes












































