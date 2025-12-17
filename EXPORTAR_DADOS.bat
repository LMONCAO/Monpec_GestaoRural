@echo off
chcp 65001 >nul
echo ==========================================
echo EXPORTAR DADOS DO SISTEMA
echo ==========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Criar diretório de backup se não existir
if not exist "backups" mkdir backups

REM Gerar nome do arquivo com data e hora
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set datestamp=%datetime:~0,8%
set timestamp=%datetime:~8,6%
set filename=backup_%datestamp%_%timestamp%.json

echo [INFO] Exportando dados para: backups\%filename%
python manage.py dumpdata --indent 2 > backups\%filename%

if errorlevel 1 (
    echo [ERRO] Falha ao exportar dados!
    pause
    exit /b 1
)

echo [OK] Dados exportados com sucesso!
echo [INFO] Arquivo salvo em: backups\%filename%
echo.
pause












