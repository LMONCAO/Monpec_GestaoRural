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

REM Verificar banco de dados antes de iniciar
echo [INFO] Verificando banco de dados...
%PYTHON_CMD% -c "import django; django.setup(); from gestao_rural.models import ProdutorRural, Propriedade; p = ProdutorRural.objects.filter(nome__icontains='Sanguino').first(); prop = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo').first(); print(f'Produtor: {p.nome if p else \"NAO ENCONTRADO\"}'); print(f'Fazenda: {prop.nome_propriedade if prop else \"NAO ENCONTRADA\"}')" 2>nul
if errorlevel 1 (
    echo [AVISO] Nao foi possivel verificar o banco de dados
)

echo.
echo ========================================
echo   INICIANDO SERVIDOR DESENVOLVIMENTO
echo ========================================
echo [INFO] Settings: sistema_rural.settings (DESENVOLVIMENTO)
echo [INFO] Banco: db.sqlite3 (com Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL: http://127.0.0.1:8000/
echo.

REM Iniciar servidor Django com settings de desenvolvimento
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se o servidor parar, manter a janela aberta
if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    pause
)
