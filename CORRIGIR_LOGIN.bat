@echo off
REM Script para Corrigir Problema de Login - Configura Senha do Banco
cd /d "%~dp0"

echo ========================================
echo   CORRIGIR PROBLEMA DE LOGIN
echo ========================================
echo.
echo O problema é que falta a senha do banco de dados no Cloud Run.
echo.

set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set SERVICE_NAME=monpec
set CONNECTION_NAME=%PROJECT_ID%:us-central1:monpec-db
set SECRET_KEY=E4-jbkGNP1rDcuZ8w-sKsb2jSPS1yWp7IbKvmrTXY0FIeR9GvKjugvgG6PBWLCoRIR0

echo ⚠️  Você precisa da senha do usuário 'monpec_user' do banco de dados.
echo.
echo Opções:
echo 1. Se você SABE a senha, digite abaixo
echo 2. Se você NÃO SABE, vamos criar uma nova senha
echo.
set /p OPCAO="Você sabe a senha? (S/N): "

if /i "%OPCAO%"=="N" (
    echo.
    echo 🔐 Criando nova senha para o banco...
    echo.
    set /p NOVA_SENHA="Digite uma senha forte para o banco (mínimo 8 caracteres): "
    
    if "%NOVA_SENHA%"=="" (
        echo ❌ Senha não pode estar vazia
        pause
        exit /b 1
    )
    
    echo.
    echo Configurando senha no Cloud SQL...
    gcloud sql users set-password monpec_user --instance=monpec-db --password=%NOVA_SENHA%
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Erro ao configurar senha
        pause
        exit /b 1
    )
    
    set DB_PASSWORD=%NOVA_SENHA%
    echo ✅ Senha configurada no Cloud SQL!
) else (
    echo.
    set /p DB_PASSWORD="Digite a senha do usuário 'monpec_user': "
    
    if "%DB_PASSWORD%"=="" (
        echo ❌ Senha não pode estar vazia
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Atualizando Cloud Run com a senha do banco...
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
echo ✅ Cloud Run atualizado!
echo.
echo 🔄 Aguardando serviço reiniciar...
timeout /t 10 /nobreak >nul

echo.
echo 📋 Verificando conexão com banco...
echo.

REM Criar job temporário para testar conexão
gcloud run jobs create monpec-test-db ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region %REGION% ^
    --add-cloudsql-instances %CONNECTION_NAME% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%" ^
    --command python ^
    --args manage.py,check,^--database,default ^
    --max-retries 1 ^
    --task-timeout 60 ^
    --quiet 2>nul

echo Executando teste de conexão...
gcloud run jobs execute monpec-test-db --region %REGION% --wait

echo.
echo 🚀 Executando migrações do banco...
echo.

REM Criar/atualizar job de migração
gcloud run jobs create monpec-migrate ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region %REGION% ^
    --add-cloudsql-instances %CONNECTION_NAME% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%" ^
    --command python ^
    --args manage.py,migrate,^--noinput ^
    --max-retries 1 ^
    --task-timeout 300 ^
    --quiet 2>nul

gcloud run jobs execute monpec-migrate --region %REGION% --wait

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migrações executadas!
) else (
    echo.
    echo ⚠️  Verifique os logs das migrações
)

echo.
echo 👤 Criando usuário administrador...
echo.

REM Criar job para criar admin
gcloud run jobs create monpec-create-admin ^
    --image gcr.io/%PROJECT_ID%/monpec:latest ^
    --region %REGION% ^
    --add-cloudsql-instances %CONNECTION_NAME% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%" ^
    --command python ^
    --args criar_admin.py ^
    --max-retries 1 ^
    --task-timeout 60 ^
    --quiet 2>nul

gcloud run jobs execute monpec-create-admin --region %REGION% --wait

echo.
echo ========================================
echo   ✅ CONFIGURAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo 📋 Credenciais de acesso:
echo    Username: admin
echo    Senha: L6171r12@@
echo.
echo 🌐 Teste o login em:
echo    https://monpec.com.br/login/
echo.
echo ⚠️  Se ainda não funcionar:
echo    1. Limpe o cache do navegador (Ctrl+Shift+Delete)
echo    2. Ou use modo anônimo (Ctrl+Shift+N)
echo    3. Aguarde 1-2 minutos para propagação
echo.

REM Limpar jobs temporários
gcloud run jobs delete monpec-test-db --region %REGION% --quiet 2>nul

pause






































