@echo off
REM ========================================
REM PARAR TUDO E INICIAR COM BANCO CORRETO
REM MARCELO SANGUINO / FAZENDA CANTA GALO
REM ========================================
title MONPEC - Parar e Iniciar CORRETO

echo ========================================
echo   PARANDO TODOS OS PROCESSOS PYTHON
echo ========================================
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"

REM PARAR TODOS OS PROCESSOS PYTHON (MULTIPLAS TENTATIVAS)
echo [1/5] Parando processos Python (tentativa 1)...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
taskkill /F /IM python3.13.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/5] Parando processos Python (tentativa 2)...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/5] Verificando processos restantes...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /I "PID"') do (
    echo [AVISO] Processo Python ainda rodando (PID: %%a) - tentando parar...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [OK] Processos Python parados
echo.

REM Verificar Python
echo [4/5] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Python local encontrado
) else (
    set PYTHON_CMD=python
    echo [OK] Python do sistema
)

REM Verificar banco de dados ANTES de iniciar
echo.
echo [5/5] VERIFICANDO BANCO DE DADOS (OBRIGATORIO)...
echo ========================================
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERRO CRITICO] BANCO DE DADOS INCORRETO!
    echo ========================================
    echo.
    echo O sistema NAO PODE iniciar porque o banco nao contem:
    echo   - Produtor: Marcelo Sanguino
    echo   - Fazenda: Fazenda Canta Galo
    echo.
    echo VERIFIQUE:
    echo   1. Se o arquivo db.sqlite3 esta no diretorio raiz
    echo   2. Se o banco contem os dados corretos
    echo   3. Se nao ha outro banco sendo usado
    echo.
    echo O sistema NAO SERA INICIADO ate que o banco esteja correto.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BANCO DE DADOS CORRETO CONFIRMADO!
echo   INICIANDO SERVIDOR...
echo ========================================
echo.
echo [INFO] Settings: sistema_rural.settings
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo [INFO] Para parar: feche esta janela ou Ctrl+C
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



























