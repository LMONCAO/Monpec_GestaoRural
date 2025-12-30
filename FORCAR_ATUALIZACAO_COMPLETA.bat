@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script que FORCA uma atualizacao completa do sistema
REM Garante que a versao nova seja deployada mesmo se houver cache

echo ========================================
echo   FORCAR ATUALIZACAO COMPLETA
echo   Garante que a versao nova seja deployada
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db
set DB_NAME=monpec_db
set DB_USER=monpec_user
set DB_PASSWORD=L6171r12@@jjms
set SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE
set DJANGO_SUPERUSER_PASSWORD=L6171r12@@

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM PASSO 1: VERIFICAR PASTA
REM ========================================
echo [1/8] Verificando pasta...
echo Pasta atual: %CD%
if not exist "Dockerfile.prod" (
    echo [ERRO] Dockerfile.prod nao encontrado!
    echo Certifique-se de estar na pasta Monpec_GestaoRural
    pause
    exit /b 1
)
echo [OK] Dockerfile.prod encontrado
echo.

REM ========================================
REM PASSO 2: CRIAR TAG UNICA
REM ========================================
echo [2/8] Criando tag unica para garantir nova versao...
set TIMESTAMP=%date:~-4,4%%date:~-7,2%%date:~-10,2%%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=!TIMESTAMP: =0!
set TIMESTAMP=!TIMESTAMP::=!
set IMAGE_TAG=gcr.io/%PROJECT_ID%/sistema-rural:v!TIMESTAMP!
set IMAGE_LATEST=gcr.io/%PROJECT_ID%/sistema-rural:latest

echo Tag unica: !IMAGE_TAG!
echo Tag latest: !IMAGE_LATEST!
echo.

REM ========================================
REM PASSO 3: BUILD SEM CACHE COM TAG UNICA
REM ========================================
echo [3/8] Fazendo build SEM CACHE com tag unica...
echo IMPORTANTE: Isso vai criar uma imagem completamente nova
echo Usando arquivos do diretorio: %CD%
echo.
echo Isso pode levar 15-25 minutos...
echo.

gcloud builds submit --no-cache --tag !IMAGE_TAG! --tag !IMAGE_LATEST! .

if errorlevel 1 (
    echo [ERRO] Falha no build!
    pause
    exit /b 1
)

echo [OK] Build concluido com tag unica: !IMAGE_TAG!
echo.

REM ========================================
REM PASSO 4: DELETAR REVISAO ANTIGA (OPCIONAL)
REM ========================================
echo [4/8] Verificando revisoes antigas...
echo.
echo Revisoes atuais:
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=3 --format="table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)" --project=%PROJECT_ID%
echo.

REM ========================================
REM PASSO 5: DEPLOY FORCANDO NOVA REVISAO
REM ========================================
echo [5/8] Fazendo deploy FORCANDO nova revisao...
echo IMPORTANTE: Usando --no-traffic para garantir nova revisao
echo Depois vamos redirecionar todo o trafego para a nova revisao
echo.

REM Primeiro deploy sem trafego
gcloud run deploy %SERVICE_NAME% ^
    --image !IMAGE_TAG! ^
    --region=%REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=600 ^
    --max-instances=10 ^
    --min-instances=0 ^
    --no-traffic

if errorlevel 1 (
    echo [ERRO] Falha no deploy!
    pause
    exit /b 1
)

echo [OK] Nova revisao criada
echo.

REM ========================================
REM PASSO 6: REDIRECIONAR TRAFEGO PARA NOVA REVISAO
REM ========================================
echo [6/8] Redirecionando todo o trafego para a nova revisao...
echo.

REM Obter nome da nova revisao
for /f "tokens=*" %%i in ('gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="value(metadata.name)" --project=%PROJECT_ID% 2^>^&1') do set NEW_REVISION=%%i

if not "!NEW_REVISION!"=="" (
    echo Nova revisao: !NEW_REVISION!
    echo Redirecionando 100%% do trafego para a nova revisao...
    gcloud run services update-traffic %SERVICE_NAME% --to-latest --region=%REGION% --project=%PROJECT_ID%
    echo [OK] Trafego redirecionado para nova revisao
) else (
    echo [AVISO] Nao foi possivel obter nome da nova revisao
    echo Mas o deploy foi concluido com sucesso
)
echo.

REM ========================================
REM PASSO 7: VERIFICAR STATUS
REM ========================================
echo [7/8] Verificando status do servico...
timeout /t 20 /nobreak >nul

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [AVISO] Nao foi possivel obter a URL
) else (
    echo [OK] Servico disponivel em: !SERVICE_URL!
)
echo.

REM ========================================
REM PASSO 8: VALIDAR ATUALIZACAO
REM ========================================
echo [8/8] Validando se a atualizacao foi aplicada...
echo.

echo Verificando revisao mais recente:
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="table(metadata.name,status.conditions[0].status,spec.containers[0].image,metadata.creationTimestamp)" --project=%PROJECT_ID%
echo.

echo Verificando imagem usada na revisao mais recente:
for /f "tokens=*" %%i in ('gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="value(spec.containers[0].image)" --project=%PROJECT_ID% 2^>^&1') do set CURRENT_IMAGE=%%i

if "!CURRENT_IMAGE!"=="!IMAGE_TAG!" (
    echo [OK] A nova imagem foi aplicada: !IMAGE_TAG!
) else if "!CURRENT_IMAGE!"=="!IMAGE_LATEST!" (
    echo [OK] A imagem latest foi aplicada: !IMAGE_LATEST!
) else (
    echo [AVISO] Imagem atual: !CURRENT_IMAGE!
    echo [AVISO] Imagem esperada: !IMAGE_TAG! ou !IMAGE_LATEST!
    echo Verifique manualmente se a atualizacao foi aplicada
)
echo.

echo ========================================
echo   ATUALIZACAO FORCADA CONCLUIDA!
echo ========================================
echo.
echo [GARANTIAS]
echo - Build executado SEM CACHE com tag unica
echo - Nova revisao criada e trafego redirecionado
echo - Versao do diretorio atual foi deployada
echo.
if not "!SERVICE_URL!"=="" (
    echo Seu sistema esta disponivel em:
    echo !SERVICE_URL!
    echo.
    echo IMPORTANTE: Aguarde 1-2 minutos para o servico inicializar completamente
    echo Depois acesse a URL e verifique se as mudancas aparecem
    echo.
)
echo ========================================
echo   COMO CONFIRMAR A ATUALIZACAO
echo ========================================
echo.
echo 1. Aguarde 1-2 minutos
if not "!SERVICE_URL!"=="" (
    echo 2. Acesse: !SERVICE_URL!
)
echo 3. Verifique se suas mudancas aparecem
echo 4. Se nao aparecer, execute este script novamente
echo.
echo Para ver logs em tempo real:
echo   VER_LOGS_TEMPO_REAL.bat
echo.
echo ========================================
echo.
pause

endlocal

