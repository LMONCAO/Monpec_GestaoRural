@echo off
REM ========================================
REM FORÇAR INÍCIO - MARCELO SANGUINO
REM Para TODOS os processos e inicia corretamente
REM ========================================
title MONPEC - FORÇAR INÍCIO MARCELO SANGUINO

color 0A
echo ========================================
echo   FORCAR INICIO - MARCELO SANGUINO
echo   FAZENDA CANTA GALO
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretorio: %CD%
echo.

REM ========================================
REM PARAR TODOS OS PROCESSOS PYTHON
REM ========================================
echo [1/5] Parando TODOS os processos Python...
echo.

REM Tentar parar de várias formas
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1
taskkill /F /IM python3.13.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Tentar com wmic (mais agressivo)
wmic process where "name='python.exe'" delete >nul 2>&1
wmic process where "name='python311.exe'" delete >nul 2>&1
timeout /t 2 /nobreak >nul

REM Verificar se ainda há processos
tasklist | findstr /i python >nul 2>&1
if errorlevel 1 (
    echo [OK] Nenhum processo Python encontrado
) else (
    echo [AVISO] Ainda ha processos Python rodando:
    tasklist | findstr /i python
    echo.
    echo [AVISO] Voce pode precisar fecha-los manualmente
    echo [AVISO] Ou reiniciar o computador
    echo.
    pause
)

echo.
echo [OK] Processos Python parados
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [2/5] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Usando Python local (python311\python.exe)
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
REM VERIFICAR BANCO DE DADOS
REM ========================================
echo [3/5] Verificando banco de dados...
echo.
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo [ERRO] BANCO DE DADOS INCORRETO!
    echo [ERRO] Nao encontrou Marcelo Sanguino ou Fazenda Canta Galo
    echo.
    echo [INFO] Verifique se o arquivo db.sqlite3 esta correto
    echo [INFO] O arquivo deve estar em: %CD%\db.sqlite3
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Banco de dados CORRETO confirmado!
echo.

REM ========================================
REM VERIFICAR ARQUIVOS
REM ========================================
echo [4/5] Verificando arquivos do sistema...
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)
if not exist "db.sqlite3" (
    echo [ERRO] Arquivo db.sqlite3 nao encontrado!
    pause
    exit /b 1
)
echo [OK] Arquivos encontrados
echo.

REM ========================================
REM INICIAR SERVIDOR
REM ========================================
echo [5/5] Iniciando servidor...
echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [INFO] Settings: sistema_rural.settings
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] Propriedade ID: 2
echo.
echo ========================================
echo   COMO ACESSAR O SISTEMA
echo ========================================
echo.
echo   URL PRINCIPAL (USE ESTA):
echo   http://localhost:8000/
echo.
echo   O sistema agora redireciona automaticamente para:
echo   http://localhost:8000/login/
echo.
echo   Se aparecer a landing page, aguarde o redirecionamento
echo   ou acesse diretamente: http://localhost:8000/login/
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














