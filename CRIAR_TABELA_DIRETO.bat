@echo off
REM ============================================
REM CRIAR TABELA DIRETAMENTE (SEM ROLLBACK)
REM ============================================
REM Este script cria a tabela diretamente no banco
REM sem fazer rollback de migrações
REM ============================================

chcp 65001 >nul
title MONPEC - Criar Tabela Direto

echo.
echo ========================================
echo   CRIAR TABELA DIRETAMENTE
echo   (Sem rollback de migrações)
echo ========================================
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    pause
    exit /b 1
)

echo [INFO] Criando tabela gestao_rural_anexolancamentofinanceiro...
echo [INFO] Este método NÃO faz rollback de migrações.
echo.

python criar_tabela_direto.py
if errorlevel 1 (
    echo.
    echo [ERRO] Não foi possível criar a tabela.
    pause
    exit /b 1
)

echo.
echo [OK] Tabela criada! Agora você pode fazer o dump.
echo.
pause

