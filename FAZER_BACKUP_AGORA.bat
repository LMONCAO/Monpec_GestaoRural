@echo off
chcp 65001 >nul
echo ========================================
echo BACKUP COMPLETO DO SISTEMA MONPEC
echo ========================================
echo.

set BACKUP_DIR=backups\backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

echo Criando diretório de backup...
if not exist "backups" mkdir backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%BACKUP_DIR%\database" mkdir "%BACKUP_DIR%\database"
if not exist "%BACKUP_DIR%\codigo" mkdir "%BACKUP_DIR%\codigo"
if not exist "%BACKUP_DIR%\config" mkdir "%BACKUP_DIR%\config"
if not exist "%BACKUP_DIR%\media" mkdir "%BACKUP_DIR%\media"

echo.
echo [1/5] Fazendo backup do banco de dados...
if exist "db.sqlite3" (
    copy "db.sqlite3" "%BACKUP_DIR%\database\" >nul
    echo   [OK] db.sqlite3 copiado
)
if exist "tenants" (
    xcopy "tenants\*" "%BACKUP_DIR%\database\tenants\" /E /I /Y >nul
    echo   [OK] Bancos de tenant copiados
)

echo.
echo [2/5] Fazendo backup do código fonte...
xcopy "gestao_rural\*" "%BACKUP_DIR%\codigo\gestao_rural\" /E /I /Y /EXCLUDE:exclude.txt >nul 2>&1
echo   [OK] gestao_rural copiado
xcopy "sistema_rural\*" "%BACKUP_DIR%\codigo\sistema_rural\" /E /I /Y /EXCLUDE:exclude.txt >nul 2>&1
echo   [OK] sistema_rural copiado
xcopy "templates\*" "%BACKUP_DIR%\codigo\templates\" /E /I /Y >nul 2>&1
echo   [OK] templates copiado
xcopy "static\*" "%BACKUP_DIR%\codigo\static\" /E /I /Y >nul 2>&1
echo   [OK] static copiado
if exist "staticfiles" (
    xcopy "staticfiles\*" "%BACKUP_DIR%\codigo\staticfiles\" /E /I /Y >nul 2>&1
    echo   [OK] staticfiles copiado
)

echo.
echo [3/5] Fazendo backup de configurações...
if exist "deploy" (
    xcopy "deploy\*" "%BACKUP_DIR%\config\deploy\" /E /I /Y >nul 2>&1
    echo   [OK] Configurações de deploy copiadas
)
copy "manage.py" "%BACKUP_DIR%\codigo\" >nul 2>&1
copy "requirements.txt" "%BACKUP_DIR%\codigo\" >nul 2>&1
if exist "requirements_producao.txt" copy "requirements_producao.txt" "%BACKUP_DIR%\codigo\" >nul 2>&1
if exist "Dockerfile" copy "Dockerfile" "%BACKUP_DIR%\codigo\" >nul 2>&1
echo   [OK] Arquivos de configuração copiados

echo.
echo [4/5] Fazendo backup de arquivos de mídia...
if exist "media" (
    xcopy "media\*" "%BACKUP_DIR%\media\" /E /I /Y >nul 2>&1
    echo   [OK] Arquivos de mídia copiados
) else (
    echo   [!] Diretório media não encontrado
)

echo.
echo [5/5] Exportando dados do Django...
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > "%BACKUP_DIR%\dumpdata.json" 2>nul
if exist "%BACKUP_DIR%\dumpdata.json" (
    echo   [OK] Dados exportados para dumpdata.json
) else (
    echo   [!] Erro ao exportar dados
)

echo.
echo Copiando documentação...
if exist "BACKUP_COMPLETO.md" copy "BACKUP_COMPLETO.md" "%BACKUP_DIR%\" >nul 2>&1
if exist "DEPLOY_INSTRUCOES.md" copy "DEPLOY_INSTRUCOES.md" "%BACKUP_DIR%\" >nul 2>&1
if exist "RESUMO_DEPLOY.md" copy "RESUMO_DEPLOY.md" "%BACKUP_DIR%\" >nul 2>&1

echo.
echo ========================================
echo BACKUP CONCLUÍDO COM SUCESSO!
echo ========================================
echo.
echo Localização: %BACKUP_DIR%
echo.
echo Próximos passos:
echo 1. Verificar o conteúdo do backup
echo 2. Fazer upload para Google Cloud Storage (opcional)
echo 3. Manter backup em local seguro
echo.
pause






