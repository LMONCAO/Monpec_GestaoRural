@echo off
title VERIFICAR SERVIDOR MONPEC
color 0B
echo.
echo ========================================
echo   VERIFICAR STATUS DO SERVIDOR MONPEC
echo ========================================
echo.

cd /d "%~dp0"

PowerShell -ExecutionPolicy Bypass -File "VERIFICAR_SERVIDOR.ps1"

pause






