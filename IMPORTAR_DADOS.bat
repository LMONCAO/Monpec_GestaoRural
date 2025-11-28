@echo off
chcp 65001 >nul
echo ==========================================
echo IMPORTAR DADOS PARA O SISTEMA
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

REM Verificar se diretório de backups existe
if not exist "backups" (
    echo [ERRO] Diretorio de backups nao encontrado!
    echo Execute EXPORTAR_DADOS.bat primeiro.
    pause
    exit /b 1
)

echo [INFO] Arquivos de backup disponiveis:
echo.
dir /b backups\*.json 2>nul
if errorlevel 1 (
    echo [ERRO] Nenhum arquivo de backup encontrado!
    pause
    exit /b 1
)
echo.

set /p arquivo="Digite o nome do arquivo de backup (ex: backup_20250101_120000.json): "

if not exist "backups\%arquivo%" (
    echo [ERRO] Arquivo nao encontrado: backups\%arquivo%
    pause
    exit /b 1
)

echo.
echo [AVISO] Esta operacao vai substituir os dados atuais do banco!
set /p confirmar="Tem certeza que deseja continuar? (S/N): "

if /i not "%confirmar%"=="S" (
    echo [INFO] Operacao cancelada.
    pause
    exit /b 0
)

echo.
echo [INFO] Importando dados de: backups\%arquivo%
python manage.py loaddata backups\%arquivo%

if errorlevel 1 (
    echo [ERRO] Falha ao importar dados!
    pause
    exit /b 1
)

echo [OK] Dados importados com sucesso!
echo.
pause

