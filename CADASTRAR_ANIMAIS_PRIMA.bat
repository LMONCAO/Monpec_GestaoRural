@echo off
chcp 65001 >nul
title MONPEC - Cadastro de Animais da Prima
color 0B

echo ========================================
echo   MONPEC - CADASTRO DE ANIMAIS PRIMA
echo   Propriedade ID: 8
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [1/4] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Usando Python local
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python não encontrado!
        echo.
        echo Por favor, instale o Python ou use um ambiente virtual.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
    echo [OK] Usando Python do sistema
)

%PYTHON_CMD% --version
echo.

REM ========================================
REM VERIFICAR ARQUIVO
REM ========================================
echo [2/4] Verificando arquivo de códigos...
if exist "c:\Users\joaoz\Downloads\animais prima.txt" (
    echo [OK] Arquivo encontrado
) else (
    echo [ERRO] Arquivo não encontrado: c:\Users\joaoz\Downloads\animais prima.txt
    pause
    exit /b 1
)
echo.

REM ========================================
REM CONFIRMAÇÃO
REM ========================================
echo [3/4] Confirmação...
echo.
echo ⚠️  ATENÇÃO:
echo   - Propriedade ID: 8
echo   - Animais existentes em outras propriedades serão EXCLUÍDOS
echo   - Serão cadastrados animais com dados completos (pesagens, vacinas, etc.)
echo.
echo [INFO] Executando automaticamente...
echo.

REM ========================================
REM EXECUTAR CADASTRO
REM ========================================
echo [4/4] Executando cadastro...
echo.
echo ========================================
echo   PROCESSANDO...
echo ========================================
echo.

%PYTHON_CMD% manage.py cadastrar_animais_prima --propriedade 8 --usuario 1 --yes

if errorlevel 1 (
    echo.
    echo [ERRO] Ocorreu um erro durante o cadastro!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   PROCESSO CONCLUÍDO!
echo ========================================
echo.
pause

