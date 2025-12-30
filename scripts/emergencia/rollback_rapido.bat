@echo off
REM Rollback rápido do sistema em caso de emergência (Windows)
REM Uso: scripts\emergencia\rollback_rapido.bat

echo ⚠️ ==========================================
echo ⚠️ ROLLBACK DE EMERGÊNCIA
echo ⚠️ ==========================================
echo.

REM Verificar se estamos em um repositório Git
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Não estamos em um repositório Git!
    pause
    exit /b 1
)

REM 1. Listar backups disponíveis
echo 📦 Backups disponíveis (últimos 5):
if exist "backups" (
    dir /b /o-d backups\backup_completo_*.zip 2>nul | findstr /n "^" | more +1 | more +5
) else (
    echo    ⚠️ Diretório de backups não encontrado
)

echo.
echo 🏷️ Tags Git de backup disponíveis (últimas 5):
git fetch --tags 2>nul
git tag -l "backup-*" | powershell -Command "$input | Select-Object -Last 5"

echo.
echo 📝 Commits recentes (últimos 5):
git log --oneline -5

echo.
echo ==========================================
set /p TAG="Digite a tag Git ou hash do commit para restaurar (ou 'cancelar' para sair): "

if "%TAG%"=="cancelar" (
    echo ❌ Rollback cancelado.
    pause
    exit /b 0
)

if "%TAG%"=="" (
    echo ❌ Tag/commit não especificado.
    pause
    exit /b 1
)

REM Verificar se tag/commit existe
git rev-parse "%TAG%" >nul 2>&1
if errorlevel 1 (
    echo ❌ Tag/commit '%TAG%' não encontrado!
    pause
    exit /b 1
)

REM Confirmar ação
echo.
echo ⚠️ ATENÇÃO: Você está prestes a reverter o código para: %TAG%
echo ⚠️ Isso irá descartar todas as mudanças após este ponto!
set /p CONFIRMACAO="Tem certeza? Digite 'SIM' para confirmar: "

if not "%CONFIRMACAO%"=="SIM" (
    echo ❌ Rollback cancelado.
    pause
    exit /b 0
)

REM Fazer backup do estado atual
echo.
echo 💾 Fazendo backup do estado atual antes de reverter...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set BACKUP_BRANCH=backup-antes-rollback-%datetime:~0,8%_%datetime:~8,6%
git branch "%BACKUP_BRANCH%" 2>nul
echo ✅ Estado atual salvo na branch: %BACKUP_BRANCH%

REM Fazer rollback do código
echo.
echo 🔄 Revertendo código para: %TAG%
git checkout -b "rollback-emergencia-%datetime:~0,8%_%datetime:~8,6%" "%TAG%" 2>nul
if errorlevel 1 (
    git reset --hard "%TAG%"
)

echo.
echo ✅ Código revertido para: %TAG%

REM Perguntar se precisa restaurar banco
echo.
set /p RESTAURAR_DB="Restaurar banco de dados também? (s/N): "

if /i "%RESTAURAR_DB%"=="s" (
    echo.
    echo 📦 Procurando backups de banco de dados...
    
    if exist "backups\backup_completo_*\db_principal_*.sqlite3" (
        echo Backups encontrados:
        dir /b /s backups\backup_completo_*\db_principal_*.sqlite3
        echo.
        set /p BACKUP_DB="Digite o caminho completo do backup do banco: "
    ) else (
        set /p BACKUP_DB="Digite o caminho completo do backup do banco: "
    )
    
    if exist "%BACKUP_DB%" (
        echo.
        echo 🔄 Restaurando banco de dados de: %BACKUP_DB%
        
        REM Fazer backup do banco atual
        if exist "db.sqlite3" (
            set BACKUP_ANTES=db.sqlite3.backup-antes-rollback-%datetime:~0,8%_%datetime:~8,6%
            copy "db.sqlite3" "%BACKUP_ANTES%" >nul
            echo ✅ Backup do banco atual criado: %BACKUP_ANTES%
        )
        
        REM Restaurar banco
        copy "%BACKUP_DB%" "db.sqlite3" >nul
        echo ✅ Banco de dados restaurado!
    ) else (
        echo ❌ Arquivo de backup não encontrado: %BACKUP_DB%
    )
)

echo.
echo ==========================================
echo ✅ ROLLBACK CONCLUÍDO!
echo ==========================================
echo.
echo 📋 Próximos passos:
echo 1. Testar o sistema: python manage.py runserver
echo 2. Se estiver OK, fazer deploy
echo.
echo ⚠️ LEMBRE-SE:
echo    - O código foi revertido para: %TAG%
echo    - Estado anterior salvo em: %BACKUP_BRANCH%
echo    - Se precisar voltar: git checkout %BACKUP_BRANCH%
echo.
pause






