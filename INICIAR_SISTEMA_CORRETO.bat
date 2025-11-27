@echo off
REM ========================================
REM MONPEC DESENVOLVIMENTO - SISTEMA CORRETO
REM Marcelo Sanguino / Fazenda Canta Galo
REM ========================================
title MONPEC - Sistema Correto (Marcelo Sanguino / Canta Galo)

echo ========================================
echo   MONPEC - SISTEMA CORRETO
echo   Marcelo Sanguino / Fazenda Canta Galo
echo ========================================
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"
echo [INFO] Diretorio: %CD%
echo.

REM Parar TODOS os processos Python (incluindo de outros diretórios)
echo [INFO] Parando TODOS os processos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
taskkill /F /IM python3.13.exe 2>nul
timeout /t 3 /nobreak >nul
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
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar banco de dados correto
echo [INFO] Verificando banco de dados...
%PYTHON_CMD% -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from gestao_rural.models import ProdutorRural, Propriedade; p = ProdutorRural.objects.filter(nome__icontains='Sanguino').first(); prop = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo').first(); print('=== BANCO DE DADOS ==='); print(f'Produtor encontrado: {p.nome if p else \"NAO ENCONTRADO\"}'); print(f'Fazenda encontrada: {prop.nome_propriedade if prop else \"NAO ENCONTRADA\"}'); exit(0 if (p and prop) else 1)" 2>nul
if errorlevel 1 (
    echo [ERRO] Banco de dados incorreto! Nao encontrou Marcelo Sanguino ou Fazenda Canta Galo
    echo [INFO] Verifique se esta usando o banco correto (db.sqlite3)
    pause
    exit /b 1
)

echo [OK] Banco de dados correto confirmado!
echo.

echo ========================================
echo   INICIANDO SERVIDOR CORRETO
echo ========================================
echo [INFO] Settings: sistema_rural.settings (DESENVOLVIMENTO)
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo [INFO] Para parar: feche esta janela ou Ctrl+C
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

