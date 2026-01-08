@echo off
chcp 65001 >nul
title MONPEC - Servidor de Desenvolvimento

echo ========================================
echo 🚀 INICIANDO SERVIDOR MONPEC
echo ========================================
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo Certifique-se de executar este script na raiz do projeto.
    pause
    exit /b 1
)

echo [INFO] Diretório: %CD%
echo.

REM Parar processos na porta 8000 (se houver)
echo [INFO] Verificando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Encerrando processo %%a na porta 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado!
    echo Instale Python e tente novamente.
    pause
    exit /b 1
)

python --version
echo.

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [INFO] Servidor disponível em: http://localhost:8000/
echo [INFO] Servidor disponível em: http://127.0.0.1:8000/
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 0.0.0.0:8000

echo.
echo [INFO] Servidor encerrado.
pause
