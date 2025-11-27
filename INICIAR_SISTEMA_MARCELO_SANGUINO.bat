@echo off
chcp 65001 >nul
echo ========================================================================
echo INICIANDO SISTEMA MARCELO SANGUINO
echo ========================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Verificar se está no diretório correto
if not exist "manage.py" (
    echo ERRO: Arquivo manage.py nao encontrado!
    echo Certifique-se de estar no diretorio do projeto.
    pause
    exit /b 1
)

echo [1/3] Verificando migracoes...
python manage.py migrate --noinput

echo.
echo [2/3] Coletando arquivos estaticos...
python manage.py collectstatic --noinput >nul 2>&1

echo.
echo [3/3] Iniciando servidor...
echo.
echo ========================================================================
echo SISTEMA INICIADO COM SUCESSO!
echo ========================================================================
echo.
echo Acesse: http://localhost:8000
echo.
echo Dashboard Consolidado: http://localhost:8000/relatorios-consolidados/
echo Justificativa: http://localhost:8000/justificativa-endividamento/
echo.
echo Pressione Ctrl+C para parar o servidor
echo ========================================================================
echo.

python manage.py runserver

pause
