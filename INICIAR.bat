@echo off
chcp 65001 >nul
echo ==========================================
echo INICIANDO MONPEC GESTAO RURAL
echo ==========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Verificar se .env existe
if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado!
    echo Execute INSTALAR.bat primeiro para configurar o sistema.
    pause
    exit /b 1
)

REM Verificar se banco de dados existe
if not exist "db.sqlite3" (
    echo [INFO] Banco de dados nao encontrado. Executando migracoes...
    python manage.py migrate
)

echo [INFO] Iniciando servidor Django...
echo [INFO] Acesse: http://127.0.0.1:8000
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.
python manage.py runserver












