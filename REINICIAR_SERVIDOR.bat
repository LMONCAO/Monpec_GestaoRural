@echo off
REM ========================================
REM REINICIAR SERVIDOR DJANGO COM NOVAS CONFIGURACOES
REM ========================================
title MONPEC - Reiniciar Servidor

echo ========================================
echo   REINICIANDO SERVIDOR DJANGO
echo   Configuracoes do Mercado Pago atualizadas!
echo ========================================
echo.

REM Ir para o diretório do script
cd /d "%~dp0"

REM Parar processos Python existentes
echo [INFO] Parando processos Python existentes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

echo [OK] Python: %PYTHON_CMD%
echo.

echo ========================================
echo   CONFIGURACOES DO MERCADO PAGO
echo ========================================
echo [OK] MERCADOPAGO_ACCESS_TOKEN configurado no .env
echo [OK] MERCADOPAGO_PUBLIC_KEY configurado no .env
echo [OK] PAYMENT_GATEWAY_DEFAULT=mercadopago
echo.

echo ========================================
echo   INICIANDO SERVIDOR
echo ========================================
echo [INFO] Settings: sistema_rural.settings
echo [INFO] URL: http://localhost:8000/
echo [INFO] Pagina de Assinaturas: http://localhost:8000/assinaturas/
echo.
echo [ATENCAO] O servidor vai iniciar nesta janela.
echo [ATENCAO] Para parar, pressione Ctrl+C
echo.
echo ========================================
echo.

REM Iniciar servidor Django
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

REM Se parar, manter janela aberta
if errorlevel 1 (
    echo.
    echo [ERRO] Servidor parou com erro!
    pause
)


