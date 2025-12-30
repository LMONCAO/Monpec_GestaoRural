@echo off
REM ============================================
REM APLICAR MIGRAÇÕES PENDENTES
REM ============================================
REM Execute este arquivo na raiz do projeto
REM ============================================
chcp 65001 >nul
title MONPEC - Aplicar Migrações

echo.
echo ========================================
echo   APLICANDO MIGRAÇÕES PENDENTES
echo ========================================
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo [INFO] Certifique-se de executar este script na raiz do projeto.
    echo [INFO] Diretório atual: %CD%
    pause
    exit /b 1
)

echo [OK] Diretório raiz encontrado: %CD%
echo.

REM Verificar migrações pendentes
echo [1/3] Verificando migrações pendentes...
echo.
python manage.py showmigrations gestao_rural | findstr /C:"[ ]"
if errorlevel 1 (
    echo [OK] Nenhuma migração pendente encontrada
    echo.
    pause
    exit /b 0
)

echo.
echo [2/3] Aplicando migrações...
echo.

REM Aplicar migrações
python manage.py migrate gestao_rural --noinput
if errorlevel 1 (
    echo.
    echo [ERRO] Erro ao aplicar migrações!
    echo [INFO] Verifique os erros acima e tente novamente.
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando migrações aplicadas...
echo.
python manage.py showmigrations gestao_rural | findstr /C:"[X]"

echo.
echo ========================================
echo   [OK] MIGRAÇÕES APLICADAS COM SUCESSO!
echo ========================================
echo.
pause

