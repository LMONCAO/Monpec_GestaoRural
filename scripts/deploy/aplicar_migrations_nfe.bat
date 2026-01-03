@echo off
chcp 65001 >nul
echo ========================================
echo Aplicando Migrations de NF-e
echo ========================================
echo.

REM Navegar para o diretório do script
cd /d "%~dp0"

echo Diretório atual: %CD%
echo.

if not exist "manage.py" (
    echo ERRO: manage.py não encontrado no diretório atual!
    echo Por favor, execute este script no diretório raiz do projeto Django.
    pause
    exit /b 1
)

echo Verificando migrations pendentes...
python manage.py showmigrations gestao_rural | findstr /C:"[ ]"
echo.

echo Aplicando migrations...
python manage.py migrate gestao_rural

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ Migrations aplicadas com sucesso!
    echo ========================================
    echo.
    echo Próximos passos:
    echo 1. Reinicie o servidor Django
    echo 2. Acesse o sistema novamente
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ Erro ao aplicar migrations!
    echo ========================================
    echo.
)

pause












































