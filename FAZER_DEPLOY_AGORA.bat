@echo off
chcp 65001 >nul
echo ========================================
echo DEPLOY PARA GOOGLE CLOUD PLATFORM
echo ========================================
echo.

echo Verificando Google Cloud SDK...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Google Cloud SDK não encontrado!
    echo Instale em: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo [OK] Google Cloud SDK encontrado
echo.

echo Verificando autenticação...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Não autenticado no Google Cloud
    echo Execute: gcloud auth login
    pause
    exit /b 1
)
echo [OK] Autenticado no Google Cloud
echo.

set /p PROJECT_ID="ID do Projeto GCP: "
set /p REGION="Região (ex: southamerica-east1): "
if "%REGION%"=="" set REGION=southamerica-east1
set /p SERVICE_NAME="Nome do serviço Cloud Run (ex: monpec-gestao-rural): "
if "%SERVICE_NAME%"=="" set SERVICE_NAME=monpec-gestao-rural

echo.
echo Configurando projeto...
gcloud config set project %PROJECT_ID%
if errorlevel 1 (
    echo [ERRO] Falha ao configurar projeto
    pause
    exit /b 1
)
echo [OK] Projeto configurado: %PROJECT_ID%
echo.

echo Habilitando APIs necessárias...
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
echo [OK] APIs habilitadas
echo.

echo Coletando arquivos estáticos...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [AVISO] Erro ao coletar estáticos
)
echo [OK] Arquivos estáticos coletados
echo.

echo Fazendo deploy no Cloud Run...
gcloud run deploy %SERVICE_NAME% --source . --region %REGION% --platform managed --allow-unauthenticated --memory 1Gi --cpu 1 --timeout 300 --max-instances 10
if errorlevel 1 (
    echo [ERRO] Falha no deploy
    pause
    exit /b 1
)

echo.
echo ========================================
echo DEPLOY CONCLUÍDO COM SUCESSO!
echo ========================================
echo.
echo Próximos passos:
echo 1. Configurar variáveis de ambiente no GCP Console
echo 2. Configurar banco de dados (Cloud SQL recomendado)
echo 3. Configurar domínio personalizado (opcional)
echo 4. Testar todas as funcionalidades
echo.
pause

























