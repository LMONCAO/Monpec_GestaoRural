@echo off
REM Script de Deploy Rápido - MONPEC para Google Cloud Run
cd /d "%~dp0"

echo ========================================
echo   DEPLOY MONPEC - Google Cloud Run
echo ========================================
echo.

REM Verificar se gcloud está instalado
where gcloud >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Google Cloud SDK não está instalado
    echo Instale em: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo ✅ Google Cloud SDK encontrado
echo.

REM Configurar projeto
set PROJECT_ID=monpec-sistema-rural
set REGION=us-central1
set SERVICE_NAME=monpec
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo Projeto: %PROJECT_ID%
echo Região: %REGION%
echo Serviço: %SERVICE_NAME%
echo.

REM Habilitar APIs
echo Habilitando APIs necessárias...
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

echo.
echo 🔨 Construindo imagem Docker...
echo (Isso pode levar alguns minutos...)
echo.

REM Build da imagem
gcloud builds submit --tag %IMAGE_NAME% --timeout=30m

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao construir imagem Docker
    echo Verifique se o Dockerfile existe no diretório atual
    pause
    exit /b 1
)

echo.
echo ✅ Imagem construída com sucesso!
echo.
echo 🚀 Fazendo deploy no Cloud Run...
echo.

REM Deploy no Cloud Run
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10 ^
    --min-instances 1 ^
    --port 8080 ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao fazer deploy
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ DEPLOY CONCLUÍDO COM SUCESSO!
echo ========================================
echo.

REM Obter URL do serviço
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo URL do serviço: %SERVICE_URL%
echo.
echo ⚠️  PRÓXIMOS PASSOS:
echo.
echo 1. Configurar variáveis de ambiente:
echo    gcloud run services update %SERVICE_NAME% --region %REGION% --update-env-vars "SECRET_KEY=sua-chave-secreta,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=sua-senha"
echo.
echo 2. Conectar ao Cloud SQL (se usar):
echo    gcloud run services update %SERVICE_NAME% --region %REGION% --add-cloudsql-instances %PROJECT_ID%:us-central1:monpec-db
echo.
echo 3. Executar migrações:
echo    gcloud run jobs execute monpec-migrate --region %REGION%
echo.
echo 4. Criar usuário admin:
echo    Execute criar_admin_cloud_run.ps1
echo.
echo 5. Configurar domínio personalizado (opcional):
echo    gcloud run domain-mappings create --service %SERVICE_NAME% --domain monpec.com.br --region %REGION%
echo.

pause













































