@echo off
REM ============================================
REM FORÇAR APLICAÇÃO DA MIGRAÇÃO 0034
REM ============================================
REM Este script força a criação da tabela
REM gestao_rural_anexolancamentofinanceiro
REM ============================================

chcp 65001 >nul
title MONPEC - Forçar Migração 0034

echo.
echo ========================================
echo   FORÇAR APLICAÇÃO DA MIGRAÇÃO 0034
echo ========================================
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo [INFO] Certifique-se de executar este script na raiz do projeto.
    pause
    exit /b 1
)

echo [1/2] Verificando se a tabela já existe...
echo.
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_anexolancamentofinanceiro'\"); result = cursor.fetchone(); print('✓ Tabela já existe!' if result else '✗ Tabela NÃO existe.')"

echo.
echo [2/2] Criando tabela diretamente (sem rollback de migrações)...
echo [INFO] Este método é seguro e não afeta outras migrações.
echo.
python criar_tabela_direto.py
if errorlevel 1 (
    echo.
    echo [ERRO] Não foi possível criar a tabela.
    echo [INFO] Você pode fazer o dump excluindo esta tabela:
    echo        python manage.py dumpdata --natural-foreign --natural-primary --exclude gestao_rural.AnexoLancamentoFinanceiro -o dados_backup.json
    pause
    exit /b 1
)

echo.
echo ========================================
echo   [OK] PROCESSO CONCLUÍDO!
echo ========================================
echo.
echo Agora você pode executar o dump:
echo python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
echo.
pause

