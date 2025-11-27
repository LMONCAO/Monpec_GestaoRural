@echo off
REM ========================================
REM PARAR TODOS OS SERVIDORES E INICIAR MARCELO SANGUINO
REM ========================================
title MONPEC - Parar Tudo e Iniciar Marcelo Sanguino

echo ========================================
echo   PARAR TODOS OS SERVIDORES
echo   E INICIAR MARCELO SANGUINO
echo ========================================
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM Parar TODOS os processos Python (múltiplas tentativas)
echo [INFO] Parando TODOS os processos Python...
echo [INFO] Tentativa 1...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [INFO] Tentativa 2 (forçar)...
wmic process where "name='python.exe'" delete >nul 2>&1
wmic process where "name='python311.exe'" delete >nul 2>&1
timeout /t 2 /nobreak >nul

echo [INFO] Verificando processos restantes...
tasklist | findstr python
if errorlevel 1 (
    echo [OK] Nenhum processo Python encontrado
) else (
    echo [AVISO] Ainda há processos Python rodando
    echo [AVISO] Você pode precisar fechá-los manualmente
    echo.
    pause
)

echo.
echo [OK] Processos Python parados (ou tentativa realizada)
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
echo [OK] Propriedade ID: 2
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)

echo ========================================
echo   INICIANDO SERVIDOR MARCELO SANGUINO
echo ========================================
echo [INFO] Settings: sistema_rural.settings
echo [INFO] Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo [INFO] URL Principal: http://localhost:8000/
echo [INFO] URL Alternativa: http://127.0.0.1:8000/
echo.
echo [IMPORTANTE] Para acessar o sistema MARCELO SANGUINO:
echo.
echo   OPCAO 1 (RECOMENDADO): Acesse diretamente o login:
echo      http://localhost:8000/login/
echo.
echo   OPCAO 2: Se aparecer a landing page (pagina publica):
echo      - Clique no botao "Ja sou cliente" (canto superior direito)
echo      - OU acesse: http://localhost:8000/login/
echo.
echo   OPCAO 3: Se ja estiver logado:
echo      http://localhost:8000/dashboard/
echo.
echo [ATENCAO] Certifique-se de usar: localhost:8000
echo          NAO use outras URLs que possam estar em cache
echo.
echo [VERIFICACAO] O banco de dados esta correto:
echo          - Produtor: Marcelo Sanguino
echo          - Fazenda: FAZENDA CANTA GALO
echo          - Propriedade ID: 2
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

