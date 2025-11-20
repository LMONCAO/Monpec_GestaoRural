@echo off
title MONPEC - Popular Dados Fazenda 2
color 0B
echo.
echo ========================================
echo   MONPEC - POPULAR DADOS FAZENDA 2
echo   Simulacao Completa do Ano 2025
echo ========================================
echo.

cd /d "%~dp0"

REM Procurar Python - primeiro local, depois sistema
set PYTHON_CMD=
if exist python311\python.exe (
    set PYTHON_CMD=python311\python.exe
    echo [OK] Python local encontrado (python311)
    goto :python_found
)
if exist python\python.exe (
    set PYTHON_CMD=python\python.exe
    echo [OK] Python local encontrado (python)
    goto :python_found
)

REM Tentar Python do sistema
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo [OK] Python do sistema encontrado
    goto :python_found
)

REM Tentar py launcher
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    echo [OK] Python encontrado via py launcher
    goto :python_found
)

echo [ERRO] Python nao encontrado!
echo.
echo Possiveis solucoes:
echo 1. Instale o Python em python311\ (portable)
echo 2. Instale o Python no sistema e adicione ao PATH
echo 3. Use o Python Launcher (py) do Windows
echo.
pause
exit /b 1

:python_found
REM Verificar se o Python realmente funciona
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python encontrado mas nao funciona!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Populando dados para Fazenda Monpec 2
echo   Simulacao: Janeiro 2025 - Dezembro 2025
echo ========================================
echo.
echo Aguarde, isso pode levar alguns minutos...
echo.

REM Executar comando para propriedade ID 2
%PYTHON_CMD% manage.py popular_todos_modulos_todas_fazendas --propriedade-id 2

echo.
echo ========================================
echo   Processo concluido!
echo   Recarregue a pagina do dashboard
echo ========================================
echo.
pause

