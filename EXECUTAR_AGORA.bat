@echo off
echo ========================================
echo Configuracao PostgreSQL Automatica
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando arquivo .env...
if not exist .env (
    echo Arquivo .env nao encontrado!
    pause
    exit /b 1
)

echo.
echo Criando banco de dados e aplicando migracoes...
echo.

python criar_banco_e_migrar.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Configuracao concluida com sucesso!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Erro na configuracao. Verifique acima.
    echo ========================================
)

pause

