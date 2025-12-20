@echo off
chcp 65001 >nul
title MONPEC - IMPORTAR DADOS
color 0D

echo ========================================
echo   MONPEC - IMPORTAR DADOS
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM ========================================
REM LISTAR BACKUPS DISPONÍVEIS
REM ========================================
echo [INFO] Procurando backups disponíveis...
echo.

if not exist "backups" (
    echo [ERRO] Pasta de backups não encontrada!
    pause
    exit /b 1
)

echo Backups disponíveis:
echo.
dir /B /AD backups\export_* 2>nul
if errorlevel 1 (
    echo [AVISO] Nenhum backup encontrado na pasta backups
    echo.
    echo Você pode:
    echo 1. Copiar um arquivo db.sqlite3 para a raiz do projeto
    echo 2. Ou usar um arquivo JSON de dados
    echo.
    pause
    exit /b 1
)

echo.
set /p BACKUP_SELECIONADO="Digite o nome do backup (ou pressione Enter para usar db.sqlite3 da raiz): "

REM ========================================
REM IMPORTAR BANCO DE DADOS
REM ========================================
echo.
echo [1/2] Importando banco de dados...

if not "%BACKUP_SELECIONADO%"=="" (
    if exist "backups\%BACKUP_SELECIONADO%\db.sqlite3" (
        echo [INFO] Fazendo backup do banco atual...
        if exist "db.sqlite3" (
            copy /Y "db.sqlite3" "db.sqlite3.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%" >nul 2>&1
        )
        copy /Y "backups\%BACKUP_SELECIONADO%\db.sqlite3" "db.sqlite3"
        echo [OK] Banco de dados importado
    ) else (
        echo [ERRO] Backup não encontrado!
        pause
        exit /b 1
    )
) else (
    if exist "db.sqlite3" (
        echo [INFO] Usando db.sqlite3 da raiz do projeto
        echo [OK] Banco de dados encontrado
    ) else (
        echo [ERRO] Nenhum banco de dados encontrado!
        pause
        exit /b 1
    )
)
echo.

REM ========================================
REM IMPORTAR DADOS JSON (OPCIONAL)
REM ========================================
echo [2/2] Verificando dados JSON para importar...
if not "%BACKUP_SELECIONADO%"=="" (
    if exist "backups\%BACKUP_SELECIONADO%\dados_exportados.json" (
        echo [INFO] Importando dados JSON...
        %PYTHON_CMD% manage.py loaddata "backups\%BACKUP_SELECIONADO%\dados_exportados.json" >nul 2>&1
        if errorlevel 1 (
            echo [AVISO] Falha ao importar dados JSON (pode ser normal)
        ) else (
            echo [OK] Dados JSON importados
        )
    )
)
echo.

REM ========================================
REM APLICAR MIGRAÇÕES
REM ========================================
echo [EXTRA] Aplicando migrações...
%PYTHON_CMD% manage.py migrate --noinput
echo [OK] Migrações aplicadas
echo.

echo ========================================
echo   IMPORTAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Próximos passos:
echo 1. Execute INICIAR.bat para iniciar o servidor
echo 2. Verifique se os dados foram importados corretamente
echo.
echo ========================================
pause


























