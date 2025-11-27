@echo off
REM ========================================
REM MONPEC DESENVOLVIMENTO - SERVIDOR PERMANENTE
REM ========================================
title MONPEC - Servidor Desenvolvimento

echo ========================================
echo   MONPEC - SERVIDOR DESENVOLVIMENTO
echo ========================================
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM Parar processos Python existentes
echo [INFO] Parando processos Python existentes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processos parados
echo.

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [INFO] Usando Python local (python311\python.exe)
) else (
    set PYTHON_CMD=python
    echo [INFO] Usando Python do sistema
)

REM Verificar se Python está disponível
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.8 ou superior
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    echo Execute este script na pasta raiz do projeto
    pause
    exit /b 1
)

echo ========================================
echo   INICIANDO SERVIDOR DESENVOLVIMENTO
echo ========================================
echo.
echo [INFO] Settings: sistema_rural.settings (DESENVOLVIMENTO)
echo [INFO] URL: http://127.0.0.1:8000/
echo [INFO] Para parar o servidor, feche esta janela ou pressione Ctrl+C
echo.
echo ========================================
echo.

REM Verificar banco de dados correto antes de iniciar
echo [INFO] Verificando banco de dados (Marcelo Sanguino / Fazenda Canta Galo)...
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo [ERRO] Banco de dados incorreto! Nao encontrou Marcelo Sanguino ou Fazenda Canta Galo
    echo [INFO] Verifique se esta usando o banco correto (db.sqlite3)
    echo [INFO] Use o script INICIAR_SISTEMA_CORRETO.bat para garantir o banco correto
    echo.
    pause
    exit /b 1
)

echo [OK] Banco de dados correto confirmado!

echo.
echo ========================================
echo   INICIANDO SERVIDOR DESENVOLVIMENTO
echo ========================================
echo [INFO] Settings: sistema_rural.settings (DESENVOLVIMENTO)
echo [INFO] Banco: db.sqlite3 (com Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo.
echo ========================================
echo   IMPORTANTE - COMO ACESSAR
echo ========================================
echo.
echo   Para acessar o sistema MARCELO SANGUINO:
echo.
echo   OPCAO 1 (RECOMENDADO):
echo      http://localhost:8000/login/
echo.
echo   OPCAO 2: Se aparecer a landing page:
echo      - Clique no botao "Ja sou cliente" (canto superior direito)
echo      - OU digite na barra de endereco: /login/
echo.
echo   OPCAO 3: Se ja estiver logado:
echo      http://localhost:8000/dashboard/
echo.
echo   [ATENCAO] Certifique-se de usar: localhost:8000
echo            NAO use outras URLs que possam estar em cache
echo.
echo ========================================
echo.

REM Iniciar servidor Django com settings de desenvolvimento
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se o servidor parar, manter a janela aberta
if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    pause
)
