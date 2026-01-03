@echo off
REM ========================================
REM FORCAR INICIO COM BANCO CORRETO
REM MARCELO SANGUINO / FAZENDA CANTA GALO
REM ========================================
title MONPEC - FORCAR INICIO CORRETO

color 0A
echo.
echo ========================================
echo   FORCANDO INICIO COM BANCO CORRETO
echo   Marcelo Sanguino / Fazenda Canta Galo
echo ========================================
echo.

cd /d "%~dp0"

REM PARAR TODOS OS PROCESSOS PYTHON
echo [PASSO 1] Parando TODOS os processos Python...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 3 /nobreak >nul

REM Verificar processos restantes e forcar parada
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" 2^>nul ^| findstr /I "python.exe"') do (
    echo [AVISO] Processo Python encontrado - forçando parada...
    taskkill /F /IM python.exe >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo [OK] Processos Python parados
echo.

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM VERIFICAR BANCO DE DADOS (OBRIGATORIO)
echo [PASSO 2] Verificando banco de dados...
echo.
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    color 0C
    echo.
    echo ========================================
    echo   ERRO: BANCO DE DADOS INCORRETO!
    echo ========================================
    echo.
    echo O banco de dados nao contem:
    echo   - Marcelo Sanguino
    echo   - Fazenda Canta Galo
    echo.
    echo O sistema NAO SERA INICIADO.
    echo.
    pause
    exit /b 1
)

color 0A
echo.
echo [PASSO 3] Banco de dados CORRETO confirmado!
echo.

REM Verificar se db.sqlite3 existe
if not exist "db.sqlite3" (
    color 0C
    echo [ERRO] Arquivo db.sqlite3 nao encontrado!
    echo.
    pause
    exit /b 1
)

echo [PASSO 4] Arquivo db.sqlite3 encontrado
echo.

REM Mostrar informacoes do banco
echo [PASSO 5] Informacoes do banco:
%PYTHON_CMD% -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from django.conf import settings; print('   Banco:', settings.DATABASES['default']['NAME'])"
echo.

REM Iniciar servidor
color 0B
echo ========================================
echo   INICIANDO SERVIDOR CORRETO
echo ========================================
echo.
echo [INFO] Settings: sistema_rural.settings
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo.
echo ========================================
echo.

%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

if errorlevel 1 (
    color 0C
    echo.
    echo [ERRO] Servidor parou com erro!
    pause
)



























