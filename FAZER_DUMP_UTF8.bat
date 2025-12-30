@echo off
REM ============================================
REM FAZER DUMP COM ENCODING UTF-8
REM ============================================

chcp 65001 >nul
title MONPEC - Fazer Dump UTF-8

echo.
echo ========================================
echo   FAZER DUMP DOS DADOS (UTF-8)
echo ========================================
echo.

python fazer_dump_utf8_v2.py
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao fazer dump.
    pause
    exit /b 1
)

echo.
pause

