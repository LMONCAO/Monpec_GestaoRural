@echo off
chcp 65001 >nul
title MONPEC - Servidor Produção Correto

echo ========================================
echo 🚀 INICIANDO SERVIDOR MONPEC - PRODUÇÃO
echo ========================================
echo.

REM Navegar para o diretório do projeto
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

REM Configurar arquivo .env para PostgreSQL
echo [INFO] Configurando ambiente para PostgreSQL...

REM Criar .env com configurações corretas
(
echo # Configurações do Mercado Pago - PRODUÇÃO
echo MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940
echo MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3
echo.
echo # URLs de callback
echo MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
echo MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/
echo.
echo # Configurações básicas do Django - PRODUÇÃO
echo DEBUG=False
echo SECRET_KEY=producao-secret-key-monpec-2025-secure-random-key-change-this
echo.
echo # BANCO POSTGRESQL DE PRODUÇÃO
echo DB_NAME=gestao_rural
echo DB_USER=postgres
echo DB_PASSWORD=postgres
echo DB_HOST=localhost
echo DB_PORT=5432
) > .env

echo [OK] Arquivo .env configurado para PostgreSQL
echo.

REM Parar processos na porta 8000
echo [INFO] Verificando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Encerrando processo %%a na porta 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Verificar PostgreSQL
echo [INFO] Verificando PostgreSQL...
bin\psql --version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] PostgreSQL não encontrado em bin\. Usando configuração padrão.
) else (
    echo [OK] PostgreSQL encontrado

    REM Verificar se PostgreSQL está rodando
    bin\psql -h localhost -U postgres -d postgres -c "SELECT 1;" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Iniciando PostgreSQL...
        bin\pg_ctl start -D data >nul 2>&1
        timeout /t 3 /nobreak >nul
    ) else (
        echo [OK] PostgreSQL já está rodando
    )
)
echo.

REM Configurar variáveis de ambiente
set DJANGO_SETTINGS_MODULE=sistema_rural.settings
set PGCLIENTENCODING=utf-8
set LANG=pt_BR.UTF-8

echo [INFO] Settings: sistema_rural.settings
echo [INFO] Porta: 8000
echo [INFO] Host: 0.0.0.0
echo [INFO] Banco: PostgreSQL
echo.

REM Verificar Python e módulos
echo [INFO] Verificando Python e módulos...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado!
    pause
    exit /b 1
)

REM Testar importação do Django
python -c "import django; print('Django versão:', django.VERSION)" 2>&1
if errorlevel 1 (
    echo [ERRO] Django não pode ser importado
    pause
    exit /b 1
)

REM Testar conexão com banco
echo [INFO] Testando conexão com banco...
python -c "
try:
    import os, django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    django.setup()
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1;')
    print('[OK] Conexão com PostgreSQL estabelecida')
except Exception as e:
    print('[ERRO] Falha na conexão:', str(e)[:100])
" 2>&1

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

REM Iniciar servidor com runserver (produção com DEBUG=False)
echo ========================================
echo   SERVIDOR DE PRODUÇÃO INICIANDO
echo ========================================
echo.
echo [INFO] Ambiente: PRODUÇÃO
echo [INFO] DEBUG: False
echo [INFO] Servidor disponível em: http://localhost:8000/
echo [INFO] Login: http://localhost:8000/login/
echo [INFO] Dashboard: http://localhost:8000/dashboard/
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 0.0.0.0:8000 --noreload

echo.
echo [INFO] Servidor encerrado.
pause



