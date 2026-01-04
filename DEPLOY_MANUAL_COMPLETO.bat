@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   DEPLOY MANUAL - GOOGLE CLOUD RUN
echo ========================================
echo.

REM Configura????es
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set IMAGE_NAME=gcr.io/%PROJECT_ID%/monpec
set IMAGE_TAG=%IMAGE_NAME%:latest

echo ???? Configura????es:
echo    Projeto: %PROJECT_ID%
echo    Servi??o: %SERVICE_NAME%
echo    Regi??o: %REGION%
echo    Imagem: %IMAGE_TAG%
echo.

REM Verificar se gcloud est?? instalado
echo ???? Verificando Google Cloud SDK...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ??? ERRO: Google Cloud SDK n??o est?? instalado!
    echo    Instale em: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ??? Google Cloud SDK encontrado
echo.

REM Verificar autentica????o
echo ???? Verificando autentica????o...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if errorlevel 1 (
    echo ??????  Voc?? n??o est?? autenticado. Fazendo login...
    gcloud auth login
    if errorlevel 1 (
        echo ??? ERRO: Falha na autentica????o!
        pause
        exit /b 1
    )
)
echo ??? Autenticado
echo.

REM Configurar projeto
echo ??????  Configurando projeto...
gcloud config set project %PROJECT_ID%
if errorlevel 1 (
    echo ??? ERRO: Falha ao configurar projeto!
    pause
    exit /b 1
)
echo ??? Projeto configurado
echo.

REM Verificar se Dockerfile existe
echo ???? Verificando Dockerfile...
if not exist Dockerfile (
    echo ??? ERRO: Dockerfile n??o encontrado!
    echo    Certifique-se de que o Dockerfile est?? na raiz do projeto.
    pause
    exit /b 1
)
echo ??? Dockerfile encontrado
echo.

REM Build da imagem Docker
echo ========================================
echo   PASSO 1: BUILD DA IMAGEM DOCKER
echo ========================================
echo.
echo ???? Iniciando build da imagem...
echo    Isso pode levar 5-10 minutos...
echo.

gcloud builds submit --tag %IMAGE_TAG% --timeout=1800s --machine-type=E2_HIGHCPU_8 .
if errorlevel 1 (
    echo.
    echo ??? ERRO: Falha no build da imagem!
    echo    Verifique os logs acima para mais detalhes.
    pause
    exit /b 1
)

echo.
echo ??? Build conclu??do com sucesso!
echo.

REM Verificar se a imagem foi criada
echo ???? Verificando se a imagem foi criada...
gcloud container images describe %IMAGE_TAG% >nul 2>&1
if errorlevel 1 (
    echo ??? ERRO: Imagem n??o encontrada ap??s o build!
    pause
    exit /b 1
)
echo ??? Imagem verificada
echo.

REM Deploy no Cloud Run
echo ========================================
echo   PASSO 2: DEPLOY NO CLOUD RUN
echo ========================================
echo.
echo ???? Iniciando deploy...
echo    Isso pode levar 2-3 minutos...
echo.

REM Construir connection string do Cloud SQL
set CLOUD_SQL_CONN=%PROJECT_ID%:%REGION%:%DB_INSTANCE%

REM Fazer deploy
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_TAG% ^
    --region=%REGION% ^
    --platform=managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%CLOUD_SQL_CONN% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=600 ^
    --max-instances=10 ^
    --min-instances=0

if errorlevel 1 (
    echo.
    echo ??? ERRO: Falha no deploy!
    echo    Verifique os logs acima para mais detalhes.
    pause
    exit /b 1
)

echo.
echo ??? Deploy conclu??do com sucesso!
echo.

REM Obter URL do servi??o
echo ========================================
echo   PASSO 3: VERIFICAR STATUS
echo ========================================
echo.
echo ???? Obtendo URL do servi??o...

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" 2^>nul') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo ??????  N??o foi poss??vel obter a URL automaticamente.
    echo    Verifique manualmente no Console do Google Cloud.
) else (
    echo.
    echo ????????? DEPLOY CONCLU??DO COM SUCESSO! ?????????
    echo.
    echo ???? URL do servi??o:
    echo    !SERVICE_URL!
    echo.
    echo ???? Status do servi??o:
    gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.url)"
    echo.
)

echo ========================================
echo   PR??XIMOS PASSOS
echo ========================================
echo.
echo 1. Acesse a URL acima para testar o sistema
echo 2. Verifique se as imagens do slide aparecem
echo 3. Teste o formul??rio de demonstra????o
echo 4. Verifique os logs se houver problemas
echo.

pause