@echo off
chcp 65001 >nul
title OTIMIZAR TUDO
echo ========================================
echo   OTIMIZACAO COMPLETA DO SISTEMA
echo ========================================
echo.
PowerShell -ExecutionPolicy Bypass -File "%~dp0OTIMIZAR_TUDO.ps1"
pause




























