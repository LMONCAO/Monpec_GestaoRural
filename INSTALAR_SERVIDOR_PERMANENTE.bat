@echo off
title INSTALAR SERVIDOR PERMANENTE MONPEC
color 0B
echo.
echo ========================================
echo   INSTALAR SERVIDOR PERMANENTE MONPEC
echo ========================================
echo.
echo Este script configura o servidor para:
echo   - Iniciar automaticamente com o Windows
echo   - Reiniciar automaticamente se cair
echo   - Manter rodando sempre
echo.
echo ========================================
echo.

REM Verificar se está rodando como Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute este arquivo como Administrador!
    echo.
    echo Clique com botao direito no arquivo e selecione
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [1/2] Configurando servidor permanente...
echo.

PowerShell -ExecutionPolicy Bypass -File "INSTALAR_SERVIDOR_PERMANENTE.ps1"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   INSTALACAO CONCLUIDA!
    echo ========================================
    echo.
    echo O servidor agora inicia automaticamente!
    echo.
) else (
    echo.
    echo [ERRO] Falha na instalacao!
    echo.
)

pause





