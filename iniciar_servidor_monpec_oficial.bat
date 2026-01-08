@echo off
chcp 65001 >nul
title MONPEC - Servidor Oficial (PostgreSQL)

echo ========================================
echo 🚀 SISTEMA MONPEC - BANCO OFICIAL
echo ========================================
echo.
echo Banco: PostgreSQL - monpec_oficial
echo Usuario: postgres
echo Status: PRODUÇÃO (DEBUG=False)
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

REM Parar processos na porta 8000
echo [INFO] Liberando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Encerrando processo %%a na porta 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Carregar configurações do banco oficial
echo [INFO] Carregando configurações do banco oficial...
call config_monpec_oficial.bat
echo.

REM Verificar Python
echo [INFO] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado!
    echo Instale o Python 3.11+ e tente novamente.
    pause
    exit /b 1
)
echo [OK] Python encontrado
echo.

REM Verificar conexão com PostgreSQL
echo [INFO] Testando conexão com PostgreSQL...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port='5432', user='postgres', password='L6171r12@@jjms', database='monpec_oficial'); conn.close(); print('[OK] Conexão com PostgreSQL estabelecida')" 2>nul
if errorlevel 1 (
    echo [ERRO] Não foi possível conectar ao banco monpec_oficial!
    echo.
    echo POSSÍVEIS SOLUÇÕES:
    echo 1. Certifique-se de que o PostgreSQL está rodando
    echo 2. Verifique se o banco 'monpec_oficial' existe
    echo 3. Execute: iniciar_servidor_monpec_oficial.bat como Administrador
    echo.
    pause
    exit /b 1
)
echo [OK] Banco de dados acessível
echo.

REM Testar importação básica do Django
echo [INFO] Verificando Django...
python -c "import django; from django.conf import settings; settings.configure(DEBUG=False); print('[OK] Django verificado')" 2>nul
if errorlevel 1 (
    echo [ERRO] Django não pode ser importado ou configurado
    echo Verifique se as dependências estão instaladas.
    pause
    exit /b 1
)
echo.

REM Iniciar servidor
echo ========================================
echo     🐄 SISTEMA MONPEC INICIANDO
echo ========================================
echo.
echo [INFO] Servidor disponível em:
echo        http://localhost:8000/
echo.
echo [INFO] Credenciais de acesso:
echo        Usuario: admin
echo        Senha: L6171r12@@
echo.
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 0.0.0.0:8000

echo.
echo [INFO] Servidor encerrado.
pause
