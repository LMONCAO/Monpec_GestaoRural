@echo off
REM Backup rápido antes de deploy (Windows)
REM Uso: scripts\emergencia\backup_antes_deploy.bat

echo 🔄 Fazendo backup antes de deploy...
echo.

REM Fazer backup completo comprimido
python manage.py backup_completo --compress --keep-days 7

if errorlevel 1 (
    echo ❌ Erro ao fazer backup!
    pause
    exit /b 1
)

echo.
echo 📦 Verificando Git...

REM Verificar se há mudanças não commitadas
git status --porcelain >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Há mudanças não commitadas. Fazendo commit automático...
    git add .
    git commit -m "Backup automático antes de deploy - %date% %time%" || echo ⚠️ Não foi possível fazer commit
) else (
    echo ✅ Nenhuma mudança pendente no Git
)

echo.
echo 🏷️ Criando tag de backup...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TAG_NAME=backup-%datetime:~0,8%_%datetime:~8,6%
git tag -a "%TAG_NAME%" -m "Backup automático antes de deploy - %date% %time%" || echo ⚠️ Não foi possível criar tag

REM Tentar fazer push (pode falhar se não houver conexão)
echo 📤 Tentando enviar tag para repositório remoto...
git push origin --tags 2>nul || echo ⚠️ Não foi possível enviar tag (pode estar offline)

echo.
echo ✅ Backup concluído!
echo 📁 Localização: backups\
echo 🏷️ Tag criada: %TAG_NAME%
echo.
echo 💡 Para fazer rollback, use:
echo    git reset --hard %TAG_NAME%
echo    ou
echo    scripts\emergencia\rollback_rapido.bat
echo.
pause








