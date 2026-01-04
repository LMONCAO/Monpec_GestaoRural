@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title TESTE AUTENTICACAO GCLOUD

echo ========================================
echo   TESTE DE AUTENTICACAO GOOGLE CLOUD
echo ========================================
echo.

:: Verificar se gcloud esta instalado
echo [1] Verificando Google Cloud SDK...
where gcloud >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Google Cloud SDK nao encontrado!
    pause
    exit /b 1
)
echo ✅ Google Cloud SDK encontrado
echo.

:: Verificar autenticacao atual
echo [2] Verificando autenticacao atual...
gcloud auth list --format="value(account)" >temp_auth.txt 2>nul
set AUTH_FOUND=0
if exist temp_auth.txt (
    for /f "usebackq delims=" %%a in ("temp_auth.txt") do (
        set AUTH_ACCOUNT=%%a
        if not "!AUTH_ACCOUNT!"=="" (
            echo ✅ Ja autenticado como: !AUTH_ACCOUNT!
            set AUTH_FOUND=1
        )
    )
)
del temp_auth.txt >nul 2>&1

if !AUTH_FOUND! EQU 0 (
    echo ⚠️  Nao autenticado
    echo.
    echo Executando login automatico...
    echo.
    gcloud auth login
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Login executado!
    ) else (
        echo ❌ Falha no login
        pause
        exit /b 1
    )
)

echo.
echo ✅ TESTE CONCLUIDO!
pause
