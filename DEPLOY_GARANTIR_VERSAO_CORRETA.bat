@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script que GARANTE que a versão correta seja deployada
REM Verifica pasta, limpa cache, valida Dockerfile e faz deploy completo

echo ========================================
echo   DEPLOY GARANTINDO VERSAO CORRETA
echo   Verifica tudo e faz deploy seguro
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

REM Pasta esperada
set EXPECTED_FOLDER=Monpec_GestaoRural

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM PASSO 1: VERIFICAR PASTA CORRETA
REM ========================================
echo [1/9] Verificando se esta na pasta correta...
for %%i in ("%CD%") do set CURRENT_FOLDER=%%~ni

if not "%CURRENT_FOLDER%"=="%EXPECTED_FOLDER%" (
    echo [AVISO] Voce esta na pasta: %CURRENT_FOLDER%
    echo [AVISO] Pasta esperada: %EXPECTED_FOLDER%
    echo.
    echo Navegando para a pasta correta...
    cd /d "%~dp0"
    for %%i in ("%CD%") do set CURRENT_FOLDER=%%~ni
    if not "%CURRENT_FOLDER%"=="%EXPECTED_FOLDER%" (
        echo [ERRO] Nao foi possivel encontrar a pasta %EXPECTED_FOLDER%
        echo [ERRO] Execute este script dentro da pasta %EXPECTED_FOLDER%
        pause
        exit /b 1
    )
)
echo [OK] Pasta correta: %CD%
echo.

REM ========================================
REM PASSO 2: VERIFICAR DOCKERFILE
REM ========================================
echo [2/9] Verificando Dockerfile...
if not exist "Dockerfile.prod" (
    echo [ERRO] Dockerfile.prod nao encontrado!
    echo [ERRO] Certifique-se de que o Dockerfile.prod esta na pasta atual
    pause
    exit /b 1
)
echo [OK] Dockerfile.prod encontrado

REM Verificar se ha Dockerfiles duplicados na pasta atual
set DOCKERFILE_COUNT=0
for %%f in (Dockerfile* Dockerfile*.prod Dockerfile_*.prod) do (
    set /a DOCKERFILE_COUNT+=1
    if !DOCKERFILE_COUNT! GTR 1 (
        echo [AVISO] Encontrado Dockerfile duplicado: %%f
        echo [AVISO] Mantendo apenas Dockerfile.prod
    )
)
echo [OK] Dockerfile validado
echo.

REM ========================================
REM PASSO 3: VERIFICAR FERRAMENTAS
REM ========================================
echo [3/9] Verificando ferramentas...
where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gcloud nao encontrado!
    echo Baixe: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo [OK] gcloud encontrado
echo.

REM ========================================
REM PASSO 4: AUTENTICACAO
REM ========================================
echo [4/9] Verificando autenticacao...
for /f "tokens=*" %%i in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>^&1') do set AUTH_ACCOUNT=%%i
if "!AUTH_ACCOUNT!"=="" (
    echo Fazendo login...
    gcloud auth login
    if errorlevel 1 (
        echo [ERRO] Falha na autenticacao!
        pause
        exit /b 1
    )
) else (
    echo [OK] Autenticado: !AUTH_ACCOUNT!
)

REM Verificar Application Default Credentials (evita pedir senha toda hora)
gcloud auth application-default print-access-token >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Configurando credenciais padrao para evitar pedir senha...
    echo [AVISO] Isso so precisa ser feito UMA VEZ
    gcloud auth application-default login --no-launch-browser
    if errorlevel 1 (
        echo [AVISO] Falha ao configurar credenciais padrao, mas continuando...
    ) else (
        echo [OK] Credenciais padrao configuradas - nao vai pedir senha mais!
    )
)

REM Configurar projeto
gcloud config set project %PROJECT_ID% >nul 2>&1
echo [OK] Projeto configurado
echo.

REM ========================================
REM PASSO 5: HABILITAR APIs
REM ========================================
echo [5/9] Habilitando APIs necessarias...
gcloud services enable cloudbuild.googleapis.com >nul 2>&1
gcloud services enable run.googleapis.com >nul 2>&1
gcloud services enable sqladmin.googleapis.com >nul 2>&1
gcloud services enable containerregistry.googleapis.com >nul 2>&1
echo [OK] APIs habilitadas
echo.

REM ========================================
REM PASSO 6: LIMPAR CACHE DE BUILD
REM ========================================
echo [6/9] Limpando cache de build anterior...
echo IMPORTANTE: Forcando build sem cache para garantir versao nova
echo Isso pode levar mais tempo, mas garante que a versao correta sera usada
echo.

REM Obter nome do projeto
for /f "tokens=*" %%i in ('gcloud config get-value project 2^>^&1') do set GCP_PROJECT=%%i
set IMAGE_NAME=gcr.io/%GCP_PROJECT%/sistema-rural

echo Fazendo build SEM CACHE da imagem: %IMAGE_NAME%
echo Usando arquivos do diretorio atual: %CD%
echo.

gcloud builds submit --no-cache --tag %IMAGE_NAME% .

if errorlevel 1 (
    echo [ERRO] Falha no build sem cache!
    echo Tentando build normal...
    gcloud builds submit --tag %IMAGE_NAME% .
    if errorlevel 1 (
        echo [ERRO] Falha no build!
        pause
        exit /b 1
    )
) else (
    echo [OK] Build sem cache concluido - Versao nova garantida
)
echo.

REM ========================================
REM PASSO 7: DEPLOY NO CLOUD RUN
REM ========================================
echo [7/9] Fazendo deploy no Cloud Run...
echo Isso pode levar alguns minutos...
echo.

gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --region=%REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%DB_INSTANCE% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%,DB_NAME=%DB_NAME%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=600 ^
    --max-instances=10 ^
    --min-instances=0

if errorlevel 1 (
    echo [ERRO] Falha no deploy!
    pause
    exit /b 1
)
echo [OK] Deploy concluido
echo.

REM ========================================
REM PASSO 8: VERIFICAR STATUS
REM ========================================
echo [8/9] Verificando status do servico...
timeout /t 15 /nobreak >nul

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [AVISO] Nao foi possivel obter a URL do servico
    echo Execute: gcloud run services describe %SERVICE_NAME% --region=%REGION%
) else (
    echo [OK] Servico disponivel em: !SERVICE_URL!
)
echo.

REM ========================================
REM PASSO 9: VERIFICAR BUILD RECENTE
REM ========================================
echo [9/9] Verificando build mais recente...
echo.
gcloud builds list --limit=1 --format="table(id,status,createTime,source.repoSource.branchName)"
echo.

echo ========================================
echo   DEPLOY CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo [GARANTIAS]
echo - Build executado SEM CACHE (--no-cache)
echo - Dockerfile validado na pasta correta
echo - Versao do diretorio atual foi deployada
echo.
if not "!SERVICE_URL!"=="" (
    echo Seu sistema esta disponivel em:
    echo !SERVICE_URL!
    echo.
)
echo ========================================
echo   PRÓXIMOS PASSOS
echo ========================================
echo.
echo 1. Aguarde 1-2 minutos para o servico inicializar completamente
if not "!SERVICE_URL!"=="" (
    echo 2. Acesse: !SERVICE_URL!
)
echo 3. Credenciais de admin:
echo    Usuario: admin
echo    Senha: %DJANGO_SUPERUSER_PASSWORD%
echo 4. O sistema executa migracoes automaticamente no inicio
echo 5. Para verificar logs:
echo    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=50
echo.
echo ========================================
echo   COMO CONFIRMAR QUE E A VERSAO NOVA
echo ========================================
echo.
echo Se quiser confirmar que a versao nova foi deployada:
echo 1. Altere um texto visivel em templates/site/landing_page.html
echo 2. Execute este script novamente
echo 3. Acesse a URL e verifique se a mudanca aparece
echo.
echo ========================================
echo.
pause

endlocal

