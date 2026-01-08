@echo off
REM Script simples para fazer backup antes do deploy (Windows)
REM Uso: scripts\backup_antes_deploy_simples.bat

setlocal

echo ==========================================
echo BACKUP ANTES DO DEPLOY
echo ==========================================
echo.

REM Configurações do banco (ajustar conforme necessário)
if "%DB_NAME%"=="" set DB_NAME=sistema_rural
if "%DB_USER%"=="" set DB_USER=monpec
if "%DB_HOST%"=="" set DB_HOST=localhost
if "%DB_PORT%"=="" set DB_PORT=5432

REM Criar diretório de backups se não existir
if not exist "backups" mkdir backups

REM Nome do arquivo de backup com timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set BACKUP_FILE=backups\backup_antes_deploy_%TIMESTAMP%.sql

echo Fazendo backup do banco de dados...
echo    Banco: %DB_NAME%
echo    Usuario: %DB_USER%
echo    Host: %DB_HOST%:%DB_PORT%
echo.

REM Fazer backup
if "%DB_PASSWORD%"=="" (
    echo Digite a senha do banco de dados:
    pg_dump -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% > %BACKUP_FILE%
) else (
    set PGPASSWORD=%DB_PASSWORD%
    pg_dump -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% > %BACKUP_FILE%
    set PGPASSWORD=
)

REM Verificar se backup foi criado com sucesso
if exist "%BACKUP_FILE%" (
    for %%A in ("%BACKUP_FILE%") do set SIZE=%%~zA
    echo.
    echo Backup criado com sucesso!
    echo    Arquivo: %BACKUP_FILE%
    echo    Tamanho: %SIZE% bytes
    echo.
    
    echo ==========================================
    echo BACKUP CONCLUIDO COM SUCESSO!
    echo ==========================================
    echo.
    echo Arquivo de backup: %BACKUP_FILE%
    echo.
    echo Para restaurar este backup, use:
    echo    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% ^< %BACKUP_FILE%
    echo.
) else (
    echo.
    echo ERRO: Falha ao criar backup!
    exit /b 1
)

pause







