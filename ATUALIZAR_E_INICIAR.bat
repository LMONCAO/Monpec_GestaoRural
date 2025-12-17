@echo off
chcp 65001 >nul
title MONPEC - ATUALIZAR E INICIAR
color 0E

echo ========================================
echo   MONPEC - ATUALIZAR E INICIAR
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"

REM ========================================
REM ATUALIZAR DO GITHUB
REM ========================================
echo [1/2] Atualizando do GitHub...
call ATUALIZAR_GITHUB.bat
if errorlevel 1 (
    echo [ERRO] Falha na atualização!
    pause
    exit /b 1
)
echo.

REM ========================================
REM INICIAR SERVIDOR
REM ========================================
echo [2/2] Iniciando servidor...
echo.
call INICIAR.bat



