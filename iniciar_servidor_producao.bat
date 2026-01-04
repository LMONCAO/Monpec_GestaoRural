@echo off
chcp 65001 >nul
title MONPEC - Servidor Produção

echo ========================================
echo 🚀 INICIANDO SERVIDOR MONPEC - PRODUÇÃO
echo ========================================
echo.

REM Navegar para o diretório do projeto (onde está o script)
cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo Diretório atual: %CD%
    echo Certifique-se de executar este script na raiz do projeto.
    pause
    exit /b 1
)

echo [INFO] Diretório do projeto: %CD%
echo.

REM Parar processos na porta 8000
echo [INFO] Verificando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Encerrando processo %%a na porta 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Configurar settings
set DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
set DEBUG=False

echo [INFO] Settings: sistema_rural.settings_producao
echo [INFO] Porta: 8000
echo [INFO] Host: 0.0.0.0
echo.

REM Verificar Python e módulos
echo [INFO] Verificando Python e módulos...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado!
    pause
    exit /b 1
)

REM Testar importação do WSGI
python -c "import sistema_rural.wsgi" 2>&1
if errorlevel 1 (
    echo [ERRO] Não foi possível importar sistema_rural.wsgi
    echo Verifique se está no diretório correto do projeto.
    pause
    exit /b 1
)
echo [OK] Módulo WSGI pode ser importado
echo.

REM Tentar usar waitress, se não conseguir usar runserver
python -c "import waitress" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Waitress encontrado
    echo.
    echo ========================================
    echo   SERVIDOR INICIANDO (WAITRESS)
    echo ========================================
    echo.
    echo [INFO] Servidor disponível em: http://localhost:8000/
    echo [INFO] Login: http://localhost:8000/login/
    echo [INFO] Pressione Ctrl+C para parar o servidor
    echo.
    python -m waitress.serve --host=0.0.0.0 --port=8000 sistema_rural.wsgi:application
) else (
    echo [AVISO] Waitress não encontrado. Usando runserver.
    echo [INFO] Para instalar waitress: python -m pip install waitress
    echo.
    echo ========================================
    echo   SERVIDOR INICIANDO (RUNSERVER)
    echo ========================================
    echo.
    echo [INFO] Servidor disponível em: http://localhost:8000/
    echo [INFO] Login: http://localhost:8000/login/
    echo [INFO] Pressione Ctrl+C para parar o servidor
    echo.
    python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao
)

echo.
echo [INFO] Servidor encerrado.
pause


