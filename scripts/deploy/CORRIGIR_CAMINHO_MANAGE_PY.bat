@echo off
REM ============================================
REM CORRIGIR CAMINHO DO manage.py
REM ============================================
REM Este script corrige scripts que estão tentando
REM acessar manage.py no caminho incorreto
REM ============================================

echo.
echo ========================================
echo   CORRIGINDO CAMINHO DO manage.py
echo ========================================
echo.

REM Verificar se estamos no diretório raiz
cd /d "%~dp0\..\.."
if not exist "manage.py" (
    echo [ERRO] manage.py nao encontrado na raiz do projeto!
    echo [INFO] Certifique-se de executar este script a partir da raiz do projeto.
    pause
    exit /b 1
)

echo [OK] manage.py encontrado na raiz do projeto
echo [INFO] Diretorio atual: %CD%
echo.

REM Verificar se há scripts tentando usar o caminho incorreto
echo [INFO] Verificando scripts em scripts\deploy\...
findstr /S /I /M "scripts\\deploy\\manage.py" scripts\deploy\*.bat scripts\deploy\*.ps1 scripts\deploy\*.sh >nul 2>&1
if errorlevel 1 (
    echo [OK] Nenhum script encontrado usando o caminho incorreto
) else (
    echo [AVISO] Encontrados scripts usando caminho incorreto
    echo [INFO] Verifique manualmente os scripts listados acima
)

echo.
echo ========================================
echo   SOLUCAO
echo ========================================
echo.
echo Se voce esta executando um script de dentro de scripts\deploy\,
echo certifique-se de que o script muda para o diretorio raiz antes
echo de executar manage.py, ou use o caminho relativo correto:
echo.
echo   CORRETO: python ..\..\manage.py
echo   CORRETO: cd ..\.. ^&^& python manage.py
echo   INCORRETO: python scripts\deploy\manage.py
echo.
echo ========================================
echo.
pause

