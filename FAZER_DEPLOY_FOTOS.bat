@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   DEPLOY COM CORREÇÃO DAS FOTOS
echo ========================================
echo.

REM Verificar se está no diretório correto
if not exist "manage.py" (
    echo ❌ Erro: Execute este script na raiz do projeto!
    echo    O arquivo manage.py deve estar no diretório atual.
    pause
    exit /b 1
)

echo ✅ Diretório do projeto encontrado
echo.

REM Verificar fotos
echo 🔍 Verificando se as fotos existem...
dir /b static\site\foto*.jpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Fotos encontradas!
) else (
    echo ⚠️  Fotos não encontradas em static\site\
)
echo.

REM Configurações
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%
set CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db
set DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it

echo 1️⃣ Fazendo build da imagem Docker...
echo    Isso pode levar vários minutos...
echo.
gcloud builds submit --tag %IMAGE_NAME%:latest --timeout=20m
if %errorlevel% neq 0 (
    echo ❌ Erro no build da imagem!
    pause
    exit /b 1
)
echo ✅ Build concluído com sucesso!
echo.

echo 2️⃣ Fazendo deploy no Cloud Run...
echo.
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%,DEBUG=False" ^
    --add-cloudsql-instances=%CONNECTION_NAME% ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=300 ^
    --max-instances=10 ^
    --min-instances=1 ^
    --port=8080 ^
    --quiet

if %errorlevel% neq 0 (
    echo ❌ Erro no deploy!
    pause
    exit /b 1
)
echo ✅ Deploy concluído com sucesso!
echo.

echo 3️⃣ Verificando URL do serviço...
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" 2^>nul') do set SERVICE_URL=%%i
if defined SERVICE_URL (
    echo ✅ Serviço disponível em: %SERVICE_URL%
) else (
    echo ⚠️  Não foi possível obter a URL do serviço
)
echo.

echo ========================================
echo ✅ DEPLOY CONCLUÍDO!
echo ========================================
echo.
echo 📋 Próximos passos:
echo   1. Acesse o site: https://monpec.com.br
echo   2. Verifique se as fotos aparecem no slideshow
echo   3. Teste as URLs diretas das fotos:
echo      - https://monpec.com.br/static/site/foto1.jpeg
echo      - https://monpec.com.br/static/site/foto2.jpeg
echo.
pause
