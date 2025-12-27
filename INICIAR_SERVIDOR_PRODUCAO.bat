@echo off
REM ==========================================
REM INICIAR SERVIDOR EM PRODUÇÃO
REM Sistema MONPEC - Gestão Rural
REM ==========================================

title MONPEC - Servidor Produção

echo ========================================
echo 🚀 INICIANDO SERVIDOR MONPEC
echo ========================================
echo.

cd /d "%~dp0"

REM Parar processos Python
echo [INFO] Parando processos Python existentes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python311\python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM Carregar variáveis de ambiente do .env_producao
if exist ".env_producao" (
    echo [INFO] Carregando variáveis de ambiente...
    for /f "tokens=1,2 delims==" %%a in (.env_producao) do (
        if not "%%a"=="" if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Configurar variáveis mínimas
if "%SECRET_KEY%"=="" (
    set SECRET_KEY=YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE
)
set DEBUG=False
set DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao

echo.
echo ========================================
echo   SERVIDOR INICIANDO
echo ========================================
echo.
echo [IMPORTANTE] Para acessar o sistema:
echo.
echo   URL DO LOGIN:
echo   http://localhost:8000/login/
echo.
echo   OU se estiver em produção:
echo   https://monpec.com.br/login/
echo.
echo ========================================
echo.

REM Iniciar servidor
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao

pause









