@echo off
chcp 65001 >nul
title MONPEC - INSTALADOR WINDOWS
color 0A

echo ========================================
echo   MONPEC - INSTALADOR WINDOWS
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [1/6] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Python local encontrado
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python não encontrado!
        echo.
        echo Por favor, instale o Python 3.11 ou superior
        echo Ou coloque o Python portátil na pasta python311
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
    echo [OK] Python do sistema encontrado
)

%PYTHON_CMD% --version
echo.

REM ========================================
REM INSTALAR DEPENDÊNCIAS
REM ========================================
echo [2/6] Instalando dependências...
if exist "requirements.txt" (
    %PYTHON_CMD% -m pip install --upgrade pip --quiet
    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependências!
        pause
        exit /b 1
    )
    echo [OK] Dependências instaladas
) else (
    echo [AVISO] Arquivo requirements.txt não encontrado
)
echo.

REM ========================================
REM VERIFICAR BANCO DE DADOS
REM ========================================
echo [3/6] Verificando banco de dados...
if not exist "db.sqlite3" (
    echo [INFO] Banco de dados não encontrado, será criado nas migrações
) else (
    echo [OK] Banco de dados encontrado
)
echo.

REM ========================================
REM EXECUTAR MIGRAÇÕES
REM ========================================
echo [4/6] Executando migrações...
%PYTHON_CMD% manage.py migrate --noinput
if errorlevel 1 (
    echo [ERRO] Falha ao executar migrações!
    pause
    exit /b 1
)
echo [OK] Migrações aplicadas
echo.

REM ========================================
REM COLETAR ARQUIVOS ESTÁTICOS
REM ========================================
echo [5/6] Coletando arquivos estáticos...
%PYTHON_CMD% manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo [AVISO] Falha ao coletar arquivos estáticos (pode ser normal)
) else (
    echo [OK] Arquivos estáticos coletados
)
echo.

REM ========================================
REM CRIAR SUPERUSUÁRIO
REM ========================================
echo [6/6] Verificando superusuário...
%PYTHON_CMD% -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@monpec.com.br', 'is_staff': True, 'is_superuser': True}); u.set_password('admin'); u.save(); print('[OK] Superusuário admin criado/atualizado' if created else '[OK] Superusuário admin já existe')"
echo.

REM ========================================
REM CONFIGURAR BANCO MARCELO SANGUINO
REM ========================================
echo [EXTRA] Configurando banco Marcelo Sanguino...
if exist "configurar_banco_marcelo_sanguino.py" (
    %PYTHON_CMD% configurar_banco_marcelo_sanguino.py
    echo [OK] Banco configurado
) else (
    echo [AVISO] Script de configuração não encontrado
)
echo.

echo ========================================
echo   INSTALAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Próximos passos:
echo 1. Execute INICIAR.bat para iniciar o servidor
echo 2. Acesse http://localhost:8000 no navegador
echo 3. Login: admin / Senha: admin
echo.
echo ========================================
pause


























