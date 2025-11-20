@echo off
title MONPEC - Servidor para Acesso pelo Celular
color 0A
echo.
echo ========================================
echo   MONPEC - SERVIDOR PARA CELULAR
echo   Sistema de Gestao Rural - PRODUCAO
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

REM Obter IP local
echo.
echo Obtendo IP local da maquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP_LOCAL=%%a
    set IP_LOCAL=!IP_LOCAL:~1!
    goto :ip_found
)
:ip_found

echo.
echo ========================================
echo   CONFIGURACAO DO SERVIDOR
echo ========================================
echo.
echo   IP Local: %IP_LOCAL%
echo   Porta: 8000
echo   Settings: sistema_rural.settings_windows
echo   Escutando em: 0.0.0.0 (aceita conexoes externas)
echo.
echo ========================================
echo   ACESSO PELO CELULAR
echo ========================================
echo.
echo   No navegador do celular, digite:
echo   http://%IP_LOCAL%:8000
echo.
echo   IMPORTANTE:
echo   - Celular e PC devem estar na mesma rede Wi-Fi
echo   - Aguarde a mensagem "Starting development server"
echo   - Pressione Ctrl+C para parar o servidor
echo ========================================
echo.
echo Iniciando servidor Django...
echo.

REM Verificar configuração do Django
echo Verificando configuracao do Django...
%PYTHON_CMD% manage.py check --settings=sistema_rural.settings_windows
if errorlevel 1 (
    echo [AVISO] Verificacao encontrou problemas!
    echo Continuando mesmo assim, mas pode haver erros...
) else (
    echo [OK] Configuracao do Django OK
)

echo.
echo Iniciando servidor em 0.0.0.0:8000...
echo.

REM Iniciar servidor escutando em 0.0.0.0 para aceitar conexoes externas
REM Usando settings_windows para evitar problemas de caminho no Windows
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows

REM Se chegou aqui, o servidor foi encerrado
echo.
echo [INFO] Servidor encerrado.

pause

