@echo off
REM ============================================
REM CRIAR TABELA SIMPLES (MÉTODO DIRETO)
REM ============================================

chcp 65001 >nul
title MONPEC - Criar Tabela Simples

echo.
echo ========================================
echo   CRIAR TABELA ANEXOLANCAMENTOFINANCEIRO
echo ========================================
echo.

python criar_tabela_simples.py
if errorlevel 1 (
    echo.
    echo [ERRO] Não foi possível criar a tabela.
    pause
    exit /b 1
)

echo.
echo [OK] Processo concluído!
echo.
pause

