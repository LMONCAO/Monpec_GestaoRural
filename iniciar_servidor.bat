@echo off
echo ========================================
echo   Iniciando Servidor Django MONPEC
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo Verificando configuracoes do Django...
python manage.py check
if errorlevel 1 (
    echo AVISO: Verificacao encontrou problemas, mas continuando...
    echo.
)

echo.
echo Iniciando servidor na porta 8000...
echo Acesse: http://localhost:8000
echo Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 8000

pause
