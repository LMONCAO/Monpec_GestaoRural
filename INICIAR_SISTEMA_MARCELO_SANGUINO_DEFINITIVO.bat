@echo off
REM ========================================
REM INICIAR SISTEMA MARCELO SANGUINO - DEFINITIVO
REM Este script GARANTE que o sistema use o banco correto
REM ========================================
title MONPEC - MARCELO SANGUINO (DEFINITIVO)

color 0A
echo ========================================
echo   INICIAR SISTEMA - MARCELO SANGUINO
echo   FAZENDA CANTA GALO
echo   (VERSAO DEFINITIVA)
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretorio: %CD%
echo.

REM ========================================
REM PARAR TODOS OS PROCESSOS PYTHON
REM ========================================
echo [1/6] Parando TODOS os processos Python...
echo.

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1
wmic process where "name='python.exe'" delete >nul 2>&1
timeout /t 3 /nobreak >nul

echo [OK] Processos Python parados
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [2/6] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Usando Python local
) else (
    set PYTHON_CMD=python
    echo [OK] Usando Python do sistema
)

%PYTHON_CMD% --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)
echo.

REM ========================================
REM VERIFICAR ARQUIVO DO BANCO
REM ========================================
echo [3/6] Verificando arquivo do banco de dados...
if not exist "db.sqlite3" (
    echo [ERRO] Arquivo db.sqlite3 nao encontrado!
    echo [ERRO] O banco de dados deve estar neste diretorio
    pause
    exit /b 1
)
echo [OK] Arquivo db.sqlite3 encontrado
echo.

REM ========================================
REM VERIFICAR CONTEUDO DO BANCO
REM ========================================
echo [4/6] Verificando conteudo do banco de dados...
echo [INFO] Procurando por: Marcelo Sanguino e Fazenda Canta Galo
echo.
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERRO CRITICO - BANCO INCORRETO!
    echo ========================================
    echo.
    echo O banco de dados NAO contem:
    echo   - Produtor: Marcelo Sanguino
    echo   - Fazenda: Canta Galo
    echo.
    echo [ACAO NECESSARIA]
    echo 1. Verifique se o arquivo db.sqlite3 esta correto
    echo 2. Certifique-se de que esta usando o banco da Fazenda Canta Galo
    echo 3. Se necessario, restaure o backup do banco correto
    echo.
    echo [INFO] O sistema NAO sera iniciado com banco incorreto
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Banco de dados CORRETO confirmado!
echo.

REM ========================================
REM VERIFICAR ARQUIVOS DO SISTEMA
REM ========================================
echo [5/6] Verificando arquivos do sistema...
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)
if not exist "sistema_rural\settings.py" (
    echo [ERRO] Arquivo settings.py nao encontrado!
    pause
    exit /b 1
)
echo [OK] Arquivos do sistema encontrados
echo.

REM ========================================
REM INICIAR SERVIDOR
REM ========================================
echo [6/6] Iniciando servidor Django...
echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [CONFIRMADO] Banco: Marcelo Sanguino / Fazenda Canta Galo
echo [CONFIRMADO] Propriedade ID: 2
echo [CONFIRMADO] Settings: sistema_rural.settings
echo.
echo ========================================
echo   COMO ACESSAR O SISTEMA
echo ========================================
echo.
echo   URL PRINCIPAL (USE ESTA):
echo   http://localhost:8000/login/
echo.
echo   O sistema redireciona automaticamente para o login
echo   Se aparecer a landing page, aguarde o redirecionamento
echo   ou acesse diretamente: http://localhost:8000/login/
echo.
echo   IMPORTANTE:
echo   - Use SEMPRE: localhost:8000
echo   - NAO use outras URLs que possam estar em cache
echo   - Limpe o cache do navegador se necessario
echo.
echo ========================================
echo.
echo [INFO] Pressione Ctrl+C para parar o servidor
echo [INFO] Ou feche esta janela
echo.
echo ========================================
echo.

REM Iniciar servidor Django
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se o servidor parar
if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    echo.
    pause
)


