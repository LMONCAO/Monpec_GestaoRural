@echo off
REM ========================================
REM INICIAR SISTEMA MARCELO SANGUINO - FORÇAR BANCO CORRETO
REM ========================================
title MONPEC - Marcelo Sanguino (FORÇAR INÍCIO)

echo ========================================
echo   MONPEC - MARCELO SANGUINO
echo   FORÇAR INÍCIO COM BANCO CORRETO
echo ========================================
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM Parar TODOS os processos Python
echo [INFO] Parando TODOS os processos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 3 /nobreak >nul
echo [OK] Todos os processos Python parados
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
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar banco de dados correto
echo ========================================
echo   VERIFICANDO BANCO DE DADOS
echo ========================================
echo [INFO] Verificando banco de dados (Marcelo Sanguino / Fazenda Canta Galo)...
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo [ERRO] Banco de dados incorreto!
    echo [INFO] Nao encontrou Marcelo Sanguino ou Fazenda Canta Galo
    echo [INFO] Verifique se o arquivo db.sqlite3 esta correto
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Banco de dados CORRETO confirmado!
echo [OK] Produtor: Marcelo Sanguino
echo [OK] Fazenda: FAZENDA CANTA GALO
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)

echo ========================================
echo   INICIANDO SERVIDOR
echo ========================================
echo [INFO] Settings: sistema_rural.settings
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo [INFO] URL Alternativa: http://localhost:8000/
echo.
echo [ATENCAO] Certifique-se de acessar: http://localhost:8000/ ou http://127.0.0.1:8000/
echo [ATENCAO] NAO acesse outras URLs que possam estar em cache do navegador
echo.
echo ========================================
echo.

REM Iniciar servidor Django
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se o servidor parar, manter a janela aberta
if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    pause
)



























