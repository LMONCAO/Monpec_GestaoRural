@echo off
REM ========================================
REM OTIMIZAÇÃO DE DESEMPENHO DO NOTEBOOK
REM ========================================
title OTIMIZAR DESEMPENHO

echo ========================================
echo   OTIMIZACAO DE DESEMPENHO
echo ========================================
echo.
echo [INFO] Execute como Administrador para otimizacoes completas
echo [INFO] Clique com botao direito e selecione "Executar como administrador"
echo.
pause

PowerShell -ExecutionPolicy Bypass -File "%~dp0OTIMIZAR_DESEMPENHO_NOTEBOOK.ps1"

pause




























