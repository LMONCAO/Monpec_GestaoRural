@echo off
REM ========================================
REM Script de Deploy Completo para Google Cloud Run
REM Projeto: monpec-sistema-rural
REM ========================================

echo ========================================
echo ???? DEPLOY COMPLETO - GOOGLE CLOUD RUN
echo ========================================
echo.

REM Verificar se gcloud est?? instalado
echo ???? Verificando Google Cloud SDK...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ??? Google Cloud SDK n??o encontrado!
    echo    Instale em: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ??? Google Cloud SDK encontrado
echo.

REM Configurar projeto
set PROJECT_ID=monpec-sistema-rural
echo ???? Configurando projeto: %PROJECT_ID%
gcloud config set project %PROJECT_ID%
echo.

REM Verificar autentica????o
echo ???? Verificando autentica????o...
gcloud config get-value account >nul 2>&1
if errorlevel 1 (
    echo ??????  N??o autenticado. Fazendo login...
    gcloud auth login
) else (
    echo ??? Autenticado
)
echo.

REM Habilitar APIs necess??rias
echo ???? Habilitando APIs necess??rias...
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage-api.googleapis.com
echo.

REM Verificar se Cloud SQL existe
echo ???????  Verificando inst??ncia Cloud SQL...
gcloud sql instances describe monpec-db --format="value(name)" >nul 2>&1
if errorlevel 1 (
    echo ??????  Inst??ncia Cloud SQL n??o encontrada. Criando...
    echo    Isso pode levar alguns minutos...
    gcloud sql instances create monpec-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=us-central1 --root-password=L6171r12@@jjms
    if errorlevel 1 (
        echo ??? Erro ao criar inst??ncia Cloud SQL
        pause
        exit /b 1
    )
    echo ??? Inst??ncia Cloud SQL criada!
    
    REM Criar banco de dados
    echo    Criando banco de dados 'sistema_rural'...
    gcloud sql databases create sistema_rural --instance=monpec-db
    
    REM Criar usu??rio
    echo    Criando usu??rio 'postgres'...
    gcloud sql users create postgres --instance=monpec-db --password=L6171r12@@jjms
) else (
    echo ??? Inst??ncia Cloud SQL j?? existe
)
echo.

REM Verificar se banco sistema_rural existe
echo ???????  Verificando banco de dados 'sistema_rural'...
gcloud sql databases list --instance=monpec-db --format="value(name)" | findstr /C:"sistema_rural" >nul 2>&1
if errorlevel 1 (
    echo ??????  Banco 'sistema_rural' n??o encontrado. Criando...
    gcloud sql databases create sistema_rural --instance=monpec-db
    echo ??? Banco 'sistema_rural' criado!
) else (
    echo ??? Banco 'sistema_rural' j?? existe
)
echo.

REM Obter connection name
echo ???? Obtendo connection name...
for /f "delims=" %%i in ('gcloud sql instances describe monpec-db --format="value(connectionName)"') do set CONNECTION_NAME=%%i
echo    Connection Name: %CONNECTION_NAME%
echo.

REM Verificar se Dockerfile existe
echo ???? Verificando arquivos necess??rios...
if not exist "Dockerfile" (
    echo ??? Dockerfile n??o encontrado!
    echo    Certifique-se de estar no diret??rio do projeto
    pause
    exit /b 1
)
if not exist "entrypoint.sh" (
    echo ??? entrypoint.sh n??o encontrado!
    pause
    exit /b 1
)
if not exist "requirements_producao.txt" (
    echo ??? requirements_producao.txt n??o encontrado!
    pause
    exit /b 1
)
if not exist "manage.py" (
    echo ??? manage.py n??o encontrado!
    pause
    exit /b 1
)
echo ??? Todos os arquivos necess??rios encontrados
echo.

REM Fazer deploy
echo ???? Fazendo deploy para Cloud Run...
echo    Isso pode levar alguns minutos...
echo.

gcloud run deploy monpec ^
    --source . ^
    --platform managed ^
    --region us-central1 ^
    --allow-unauthenticated ^
    --port 8080 ^
    --memory 4Gi ^
    --cpu 2 ^
    --timeout 900 ^
    --add-cloudsql-instances=%CONNECTION_NAME% ^
    --set-env-vars="CLOUD_SQL_CONNECTION_NAME=%CONNECTION_NAME%,DB_NAME=sistema_rural,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,SECRET_KEY=rfzjy1t$$d_cmjb2n-wda0oi+)p!(_4!4$na-n-1a60$2gyspo,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" ^
    --max-instances=10 ^
    --min-instances=0

if errorlevel 1 (
    echo.
    echo ??? Erro no deploy. Verifique os logs acima.
    pause
    exit /b 1
)

echo.
echo ??? Deploy conclu??do com sucesso!
echo.

REM Obter URL do servi??o
echo ???? Obtendo URL do servi??o...
for /f "delims=" %%i in ('gcloud run services describe monpec --region=us-central1 --format="value(status.url)"') do set SERVICE_URL=%%i
echo.
echo ========================================
echo ???? DEPLOY CONCLU??DO!
echo ========================================
echo.
echo URL do servi??o: %SERVICE_URL%
echo.
echo ???? Pr??ximos passos:
echo    1. Acesse: %SERVICE_URL%
echo    2. Verifique os logs: gcloud run services logs read monpec --region=us-central1
echo    3. Configure dom??nio customizado (opcional) no Cloud Run Console
echo.
pause
