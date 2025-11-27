@echo off
REM ========================================
REM MONPEC - SERVIDOR PERMANENTE
REM Este script mantém o servidor sempre online
REM Reinicia automaticamente se o servidor parar
REM ========================================
title MONPEC - Servidor Permanente (Auto-Restart)

echo ========================================
echo   MONPEC - SERVIDOR PERMANENTE
echo   Auto-Restart Ativado
echo ========================================
echo.

REM Ir para o diretório do script
cd /d "%~dp0"

:LOOP
echo [%date% %time%] Iniciando servidor MONPEC...

REM Parar processos Python existentes
taskkill /F /IM python.exe 2>nul >nul
timeout /t 2 /nobreak >nul

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    echo Pressione qualquer tecla para tentar novamente...
    pause >nul
    goto LOOP
)

echo [INFO] Configuracao: sistema_rural.settings (DESENVOLVIMENTO)
echo [INFO] Servidor: http://127.0.0.1:8000/
echo.

REM Iniciar servidor Django
REM O servidor ficará rodando até ser interrompido
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se chegou aqui, o servidor parou
echo.
echo [AVISO] Servidor parou em %date% %time%
echo [INFO] Reiniciando em 5 segundos...
echo [INFO] Pressione Ctrl+C para parar completamente
timeout /t 5 /nobreak >nul

REM Reiniciar o loop
goto LOOP

