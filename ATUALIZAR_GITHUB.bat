@echo off
chcp 65001 >nul
title MONPEC - ATUALIZAR DO GITHUB
color 0B

echo ========================================
echo   MONPEC - ATUALIZAR DO GITHUB
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Diretório: %CD%
echo.

REM ========================================
REM VERIFICAR GIT
REM ========================================
echo [1/5] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git não encontrado!
    echo Por favor, instale o Git: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git encontrado
git --version
echo.

REM ========================================
REM VERIFICAR STATUS
REM ========================================
echo [2/5] Verificando status do repositório...
git status --short
echo.

REM ========================================
REM FAZER BACKUP LOCAL
REM ========================================
echo [3/5] Criando backup local...
set BACKUP_DIR=backups\backup_antes_atualizacao_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

if not exist "backups" mkdir "backups"
if exist "db.sqlite3" (
    copy /Y "db.sqlite3" "%BACKUP_DIR%_db.sqlite3" >nul 2>&1
    echo [OK] Backup do banco criado
)
echo.

REM ========================================
REM ATUALIZAR DO GITHUB
REM ========================================
echo [4/5] Atualizando do GitHub...
echo [INFO] Fazendo fetch do repositório remoto...
git fetch origin
if errorlevel 1 (
    echo [ERRO] Falha ao fazer fetch!
    pause
    exit /b 1
)

echo [INFO] Verificando atualizações disponíveis...
git log HEAD..origin/master --oneline >nul 2>&1
if errorlevel 1 (
    echo [INFO] Nenhuma atualização disponível
    echo [INFO] Sistema já está atualizado
) else (
    echo [INFO] Atualizações encontradas!
    echo.
    echo Últimas atualizações:
    git log HEAD..origin/master --oneline -5
    echo.
    echo [INFO] Fazendo pull do GitHub...
    git pull origin master
    if errorlevel 1 (
        echo [ERRO] Falha ao fazer pull!
        echo [INFO] Pode haver conflitos. Verifique manualmente.
        pause
        exit /b 1
    )
    echo [OK] Código atualizado do GitHub
)
echo.

REM ========================================
REM ATUALIZAR SISTEMA
REM ========================================
echo [5/5] Atualizando sistema...

REM Verificar Python
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM Aplicar migrações
echo [INFO] Aplicando migrações...
%PYTHON_CMD% manage.py migrate --noinput
if errorlevel 1 (
    echo [AVISO] Algumas migrações podem ter falhado
) else (
    echo [OK] Migrações aplicadas
)

REM Coletar arquivos estáticos
echo [INFO] Coletando arquivos estáticos...
%PYTHON_CMD% manage.py collectstatic --noinput --clear >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Falha ao coletar estáticos (pode ser normal)
) else (
    echo [OK] Arquivos estáticos atualizados
)
echo.

echo ========================================
echo   ATUALIZAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Próximos passos:
echo 1. Execute INICIAR.bat para iniciar o servidor
echo 2. Ou execute ATUALIZAR_E_INICIAR.bat para atualizar e iniciar
echo.
echo ========================================
pause



