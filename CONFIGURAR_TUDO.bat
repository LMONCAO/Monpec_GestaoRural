@echo off
REM Script Completo para Configurar Tudo - Banco, Senha e Variáveis
cd /d "%~dp0"

echo ========================================
echo   CONFIGURAÇÃO COMPLETA - MONPEC
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set SERVICE_NAME=monpec
set CONNECTION_NAME=%PROJECT_ID%:us-central1:monpec-db
set SECRET_KEY=E4-jbkGNP1rDcuZ8w-sKsb2jSPS1yWp7IbKvmrTXY0FIeR9GvKjugvgG6PBWLCoRIR0

echo.
echo ⚠️  IMPORTANTE: Você precisa da senha do banco de dados
echo.
set /p DB_PASSWORD="Digite a senha do usuário 'monpec_user' do banco: "

if "%DB_PASSWORD%"=="" (
    echo.
    echo ❌ Senha não pode estar vazia!
    echo.
    echo Se não souber a senha, você pode:
    echo 1. Redefinir a senha no Cloud SQL Console
    echo 2. Ou criar uma nova senha com:
    echo    gcloud sql users set-password monpec_user --instance=monpec-db --password=SUA_SENHA
    pause
    exit /b 1
)

echo.
echo 🔐 Configurando senha do banco (se necessário)...
gcloud sql users set-password monpec_user --instance=monpec-db --password=%DB_PASSWORD% --quiet

echo.
echo 🚀 Atualizando Cloud Run com todas as configurações...
echo.

gcloud run services update %SERVICE_NAME% ^
    --region %REGION% ^
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao atualizar Cloud Run
    pause
    exit /b 1
)

echo.
echo ✅ Configuração aplicada!
echo.
echo 🔄 Aguardando alguns segundos para o serviço reiniciar...
timeout /t 5 /nobreak >nul

echo.
echo 📋 Criando job de migração...
echo.

REM Criar job de migração
gcloud run jobs create monpec-migrate ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region %REGION% ^
    --add-cloudsql-instances %CONNECTION_NAME% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%" ^
    --command python ^
    --args manage.py,migrate ^
    --max-retries 1 ^
    --task-timeout 300 ^
    --quiet 2>nul

echo.
echo 🚀 Executando migrações...
echo.

gcloud run jobs execute monpec-migrate --region %REGION% --wait

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migrações executadas com sucesso!
) else (
    echo.
    echo ⚠️  Verifique os logs das migrações
)

echo.
echo ========================================
echo   ✅ CONFIGURAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo ⚠️  PRÓXIMOS PASSOS:
echo.
echo 1. Teste o login no site:
echo    https://monpec.com.br/login/
echo.
echo 2. Se o login não funcionar, crie o usuário admin:
echo    Execute criar_admin_cloud_run.ps1
echo.
echo 3. Limpe o cache do navegador (Ctrl+Shift+Delete)
echo    ou use modo anônimo (Ctrl+Shift+N)
echo.

pause




















