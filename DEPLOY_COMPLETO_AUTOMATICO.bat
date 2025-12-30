@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   DEPLOY COMPLETO AUTOMATICO
echo   Limpando Cloud, Enviando Arquivos e Deploy
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set BUCKET_NAME=%PROJECT_ID%-backup-completo
set DB_INSTANCE=monpec-db
set DB_NAME=monpec_db
set DB_USER=monpec_user
set DB_PASSWORD=L6171r12@@jjms

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo [CONFIG] Bucket: %BUCKET_NAME%
echo.

REM ========================================
REM VERIFICACOES INICIAIS
REM ========================================
echo [1/7] Verificando ferramentas...
where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gcloud nao encontrado!
    echo Instale: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

where gsutil >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gsutil nao encontrado!
    pause
    exit /b 1
)
echo [OK] Ferramentas encontradas
echo.

REM ========================================
REM AUTENTICACAO E PROJETO
REM ========================================
echo [2/7] Configurando projeto...
gcloud config set project %PROJECT_ID% >nul 2>&1

REM Verificar autenticacao
for /f "tokens=*" %%i in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>^&1') do set AUTH_ACCOUNT=%%i
if "!AUTH_ACCOUNT!"=="" (
    echo [AVISO] Nao autenticado. Fazendo login...
    gcloud auth login
    if errorlevel 1 (
        echo [ERRO] Falha na autenticacao!
        pause
        exit /b 1
    )
) else (
    echo [OK] Autenticado como: !AUTH_ACCOUNT!
)
echo.

REM ========================================
REM LIMPAR BUCKET ANTIGO
REM ========================================
echo [3/7] Limpando arquivos antigos no Cloud Storage...
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if not errorlevel 1 (
    echo Limpando bucket: !BUCKET_NAME!
    gsutil -m rm -r "gs://!BUCKET_NAME!/*" >nul 2>&1
    echo [OK] Bucket limpo
) else (
    echo Bucket nao existe, sera criado
)
echo.

REM ========================================
REM CRIAR BUCKET SE NAO EXISTIR
REM ========================================
echo [4/7] Garantindo que bucket existe...
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if errorlevel 1 (
    echo Criando bucket: !BUCKET_NAME!
    gsutil mb -p %PROJECT_ID% -l %REGION% "gs://!BUCKET_NAME!"
    if errorlevel 1 (
        echo [ERRO] Falha ao criar bucket!
        pause
        exit /b 1
    )
    echo [OK] Bucket criado
) else (
    echo [OK] Bucket ja existe
)
echo.

REM ========================================
REM UPLOAD COMPLETO DA PASTA
REM ========================================
echo [5/7] Fazendo upload completo da pasta...
echo Isso pode levar varios minutos dependendo do tamanho...
echo.

REM Obter nome da pasta atual
for %%i in ("%CD%") do set FOLDER_NAME=%%~ni

REM Excluir arquivos desnecessarios
set EXCLUDE_ARGS=-x "venv/**" -x "__pycache__/**" -x ".git/**" -x "node_modules/**" -x "*.pyc" -x ".env" -x "logs/**" -x "temp/**" -x "staticfiles/**" -x "*.log" -x ".gitignore"

REM Fazer upload
gsutil -m rsync -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!FOLDER_NAME!/"

if errorlevel 1 (
    echo [ERRO] Falha no upload!
    pause
    exit /b 1
)
echo [OK] Upload concluido!
echo.

REM ========================================
REM PREPARAR COMANDOS PARA CLOUD SHELL
REM ========================================
echo [6/7] Preparando comandos para Cloud Shell...
echo.

REM Criar script para Cloud Shell
set CLOUD_SHELL_SCRIPT=deploy_cloud_shell_automatico.sh
(
    echo #!/bin/bash
    echo set -e
    echo.
    echo echo "========================================"
    echo echo "  DEPLOY AUTOMATICO NO CLOUD SHELL"
    echo echo "========================================"
    echo echo.
    echo PROJECT_ID="%PROJECT_ID%"
    echo SERVICE_NAME="%SERVICE_NAME%"
    echo REGION="%REGION%"
    echo BUCKET_NAME="%BUCKET_NAME%"
    echo FOLDER_NAME="!FOLDER_NAME!"
    echo DB_INSTANCE="%DB_INSTANCE%"
    echo DB_NAME="%DB_NAME%"
    echo DB_USER="%DB_USER%"
    echo DB_PASSWORD="%DB_PASSWORD%"
    echo.
    echo echo "[1] Configurando projeto..."
    echo gcloud config set project $PROJECT_ID
    echo.
    echo echo "[2] Baixando arquivos do Cloud Storage..."
    echo gsutil -m cp -r "gs://$BUCKET_NAME/$FOLDER_NAME/*" .
    echo.
    echo echo "[3] Habilitando APIs necessarias..."
    echo gcloud services enable cloudbuild.googleapis.com
    echo gcloud services enable run.googleapis.com
    echo gcloud services enable sqladmin.googleapis.com
    echo.
    echo echo "[4] Fazendo build da imagem Docker..."
    echo TIMESTAMP=$(date +%%Y%%m%%d%%H%%M%%S)
    echo IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
    echo gcloud builds submit --tag $IMAGE_TAG
    echo gcloud container images add-tag $IMAGE_TAG gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet
    echo.
    echo echo "[5] Fazendo deploy no Cloud Run..."
    echo gcloud run deploy $SERVICE_NAME ^
    echo     --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest ^
    echo     --region=$REGION ^
    echo     --platform managed ^
    echo     --allow-unauthenticated ^
    echo     --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE ^
    echo     --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" ^
    echo     --memory=2Gi ^
    echo     --cpu=2 ^
    echo     --timeout=300 ^
    echo     --max-instances=10
    echo.
    echo echo "[6] Executando migracoes..."
    echo sleep 10
    echo SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
    echo echo "Aguardando servico ficar pronto..."
    echo sleep 30
    echo.
    echo echo "[7] Verificando status..."
    echo HTTP_CODE=$(curl -s -o /dev/null -w "%%{http_code}" "$SERVICE_URL" 2^>/dev/null || echo "000")
    echo echo "URL do servico: $SERVICE_URL"
    echo echo "HTTP Status: $HTTP_CODE"
    echo.
    echo if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo     echo "========================================"
    echo     echo "  DEPLOY CONCLUIDO COM SUCESSO!"
    echo     echo "========================================"
    echo     echo "Sistema disponivel em: $SERVICE_URL"
    echo else
    echo     echo "[AVISO] Servico pode estar iniciando ainda..."
    echo     echo "Verifique os logs:"
    echo     echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20 --project=$PROJECT_ID"
    echo fi
    echo.
    echo echo "========================================"
    echo echo "  PROCESSO FINALIZADO"
    echo echo "========================================"
) > "%CLOUD_SHELL_SCRIPT%"

echo [OK] Script criado: %CLOUD_SHELL_SCRIPT%
echo.

REM ========================================
REM INSTRUCOES FINAIS
REM ========================================
echo [7/7] Instrucoes finais
echo.
echo ========================================
echo   UPLOAD CONCLUIDO!
echo ========================================
echo.
echo Seus arquivos foram enviados para:
echo gs://%BUCKET_NAME%/%FOLDER_NAME%/
echo.
echo ========================================
echo   PROXIMOS PASSOS - CLOUD SHELL
echo ========================================
echo.
echo 1. Abra o Google Cloud Shell:
echo    https://console.cloud.google.com/cloudshell?project=%PROJECT_ID%
echo.
echo 2. No Cloud Shell, execute:
echo    gsutil -m cp -r gs://%BUCKET_NAME%/%FOLDER_NAME%/* .
echo.
echo 3. Ou use o script automatico criado:
echo    bash %CLOUD_SHELL_SCRIPT%
echo.
echo 4. O script automatico fara:
echo    - Download dos arquivos
echo    - Build da imagem Docker
echo    - Deploy no Cloud Run
echo    - Configuracao automatica
echo.
echo ========================================
echo   OU USE O COMANDO DIRETO:
echo ========================================
echo.
echo Copie e cole no Cloud Shell:
echo.
echo gcloud config set project %PROJECT_ID% ^&^& ^
echo gsutil -m cp -r gs://%BUCKET_NAME%/%FOLDER_NAME%/* . ^&^& ^
echo gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^&^& ^
echo gcloud run deploy %SERVICE_NAME% --image gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest --region=%REGION% --platform managed --allow-unauthenticated --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%"
echo.
echo ========================================
echo.
pause

endlocal

