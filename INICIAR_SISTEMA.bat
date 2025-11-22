@echo off
REM Script para iniciar o sistema Django
REM Este arquivo inicia o sistema a partir da pasta sincronizada

echo ========================================
echo   Iniciando Sistema Monpec Gestao Rural
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao esta instalado!
    echo Instale Python 3.8 ou superior: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se estamos na pasta correta
if not exist "manage.py" (
    echo ERRO: Arquivo manage.py nao encontrado!
    echo Execute este script na pasta raiz do projeto
    pause
    exit /b 1
)

REM Verificar se o banco de dados existe
if not exist "db.sqlite3" (
    echo Criando banco de dados...
    python manage.py migrate
    if errorlevel 1 (
        echo ERRO: Falha ao criar banco de dados
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Iniciando servidor Django...
echo ========================================
echo.
echo O sistema estara disponivel em:
echo   http://127.0.0.1:8000/
echo   http://localhost:8000/
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.

REM Iniciar servidor
python manage.py runserver

pause
