@echo off
echo ========================================
echo    INICIANDO SISTEMA MONPEC
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

echo [1/4] Verificando ambiente Python...
python --version

echo [2/4] Verificando dependencias...
python -c "import django; print('Django OK')" 2>nul
if errorlevel 1 (
    echo ERRO: Django nao esta instalado!
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo [3/4] Verificando banco de dados...
python manage.py check >nul 2>&1
if errorlevel 1 (
    echo AVISO: Problemas encontrados no sistema. Executando migracoes...
    python manage.py migrate
)

echo [4/4] Iniciando servidor Django...
echo.
echo ========================================
echo Servidor iniciando na porta 8000
echo Acesse: http://127.0.0.1:8000
echo ========================================
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver

pause

















