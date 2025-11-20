@echo off
title MONPEC - Servidor Local
color 0A
echo.
echo ========================================
echo   MONPEC - SERVIDOR LOCAL
echo   Sistema de Gestao Rural
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist manage.py (
    echo [ERRO] Arquivo manage.py nao encontrado!
    echo Certifique-se de estar no diretorio correto do projeto.
    pause
    exit /b 1
)

REM Procurar Python - primeiro local, depois sistema
set PYTHON_CMD=
if exist python311\python.exe (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Python local encontrado (python311)
) else if exist python\python.exe (
    set PYTHON_CMD=python\python.exe
    echo [OK] Python local encontrado (python)
) else (
    REM Tentar Python do sistema
    python --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
        echo [OK] Python do sistema encontrado
    ) else (
        REM Tentar py launcher
        py --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=py
            echo [OK] Python encontrado via py launcher
        ) else (
            echo [ERRO] Python nao encontrado!
            echo.
            echo Possiveis solucoes:
            echo 1. Instale o Python em python311\ (portable)
            echo 2. Instale o Python no sistema e adicione ao PATH
            echo 3. Use o Python Launcher (py) do Windows
            echo.
            pause
            exit /b 1
        )
    )
)

echo Verificando versao do Python...
%PYTHON_CMD% --version

REM Parar processos que possam estar usando a porta 8000
echo.
echo Verificando processos usando a porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    echo [INFO] Encontrado processo usando porta 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Processo encerrado
    )
)
timeout /t 2 /nobreak >nul

REM Definir pip baseado no Python encontrado
if exist python311\Scripts\pip.exe (
    set PIP_CMD=python311\Scripts\pip.exe
) else if exist python\Scripts\pip.exe (
    set PIP_CMD=python\Scripts\pip.exe
) else (
    set PIP_CMD=%PYTHON_CMD% -m pip
)

echo.
echo Verificando dependencias...
%PYTHON_CMD% -c "import django" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Django nao encontrado!
    echo Instalando dependencias...
    %PIP_CMD% install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias!
        echo.
        echo Tente instalar manualmente:
        echo   %PIP_CMD% install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
) else (
    echo [OK] Django encontrado
)

REM Verificar configuração do Django
echo.
echo Verificando configuracao do Django...
%PYTHON_CMD% manage.py check
if errorlevel 1 (
    echo [AVISO] Verificacao encontrou problemas!
    echo Continuando mesmo assim, mas pode haver erros...
) else (
    echo [OK] Configuracao do Django OK
)

echo.
echo Aplicando migracoes do banco de dados...
%PYTHON_CMD% manage.py migrate --noinput
if errorlevel 1 (
    echo [AVISO] Erro ao aplicar migracoes!
    echo Tentando aplicar migracoes com output completo...
    %PYTHON_CMD% manage.py migrate
    echo.
    echo Continuando mesmo assim...
) else (
    echo [OK] Migracoes aplicadas
)

REM Verificar se a porta 8000 está disponível
echo.
echo Verificando se a porta 8000 esta disponivel...
netstat -ano | findstr ":8000" >nul
if not errorlevel 1 (
    echo [AVISO] Porta 8000 parece estar em uso. Tentando usar porta 8001...
    set PORTA=8001
) else (
    set PORTA=8000
    echo [OK] Porta 8000 disponivel
)

echo.
echo ========================================
echo   SERVIDOR INICIANDO...
echo ========================================
echo.
echo   ACESSO LOCAL:
echo   http://127.0.0.1:%PORTA%
echo   http://localhost:%PORTA%
echo.
echo   IMPORTANTE:
echo   - Aguarde a mensagem "Starting development server"
echo   - Se aparecer algum erro, leia a mensagem completa
echo   - Pressione Ctrl+C para parar o servidor
echo ========================================
echo.
echo Iniciando servidor Django...
echo.

REM Tentar iniciar o servidor e capturar erros
%PYTHON_CMD% manage.py runserver 127.0.0.1:%PORTA% 2>&1

REM Se chegou aqui, o servidor foi encerrado
echo.
echo [INFO] Servidor encerrado.

pause



