@echo off
REM Script completo de deploy para produção (Windows)
REM Uso: deploy.bat [producao|gcp]

setlocal enabledelayedexpansion

echo ========================================
echo DEPLOY COMPLETO - MONPEC
echo ========================================
echo.

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=producao
if "%ENVIRONMENT%"=="gcp" (
    set SETTINGS_MODULE=sistema_rural.settings_gcp
    echo Ambiente: Google Cloud Platform
) else (
    set SETTINGS_MODULE=sistema_rural.settings_producao
    echo Ambiente: Producao Locaweb
)

echo Settings: %SETTINGS_MODULE%
echo.

echo [1/6] Fazendo backup do banco de dados...
if not exist "backups" mkdir backups

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set BACKUP_FILE=backups\backup_deploy_%TIMESTAMP%.sql

if "%DB_PASSWORD%"=="" (
    echo AVISO: Execute manualmente: pg_dump -h localhost -U monpec -d sistema_rural ^> backup.sql
) else (
    set PGPASSWORD=%DB_PASSWORD%
    pg_dump -h localhost -U monpec -d sistema_rural > %BACKUP_FILE% 2>nul
    set PGPASSWORD=
    if exist "%BACKUP_FILE%" echo Backup criado: %BACKUP_FILE%
)
echo.

echo [2/6] Verificando migracoes pendentes...
python manage.py showmigrations --settings=%SETTINGS_MODULE%
echo.

echo [3/6] Executando migracoes...
python manage.py migrate --noinput --settings=%SETTINGS_MODULE%
if errorlevel 1 (
    echo ERRO: Falha nas migracoes!
    pause
    exit /b 1
)
echo Migracoes executadas!
echo.

echo [4/6] Coletando arquivos estaticos...
python manage.py collectstatic --noinput --settings=%SETTINGS_MODULE%
if errorlevel 1 (
    echo ERRO: Falha ao coletar arquivos estaticos!
    pause
    exit /b 1
)
echo Arquivos estaticos coletados!
echo.

echo [5/6] Verificando sintaxe...
python -m py_compile gestao_rural\views.py 2>nul
if errorlevel 1 (
    echo AVISO: Verifique erros de sintaxe
) else (
    echo Sintaxe OK
)
echo.

echo ========================================
echo DEPLOY PREPARADO COM SUCESSO!
echo ========================================
echo.
echo Proximos passos:
echo   1. Reiniciar o servidor
echo   2. Verificar logs
echo   3. Acessar o sistema
echo.

pause







