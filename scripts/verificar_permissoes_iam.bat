@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   VERIFICACAO DE PERMISSOES IAM
echo   Google Cloud Platform
echo ========================================
echo.

REM Configurações
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_INSTANCE=monpec-db

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo [CONFIG] Cloud SQL Instance: %DB_INSTANCE%
echo.

REM Verificar se gcloud está instalado
where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gcloud nao encontrado!
    echo Baixe: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Configurar projeto
gcloud config set project %PROJECT_ID% >nul 2>&1

echo ========================================
echo 1. VERIFICANDO SERVICE ACCOUNT DO CLOUD RUN
echo ========================================
echo.

REM Obter service account do Cloud Run
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(spec.template.spec.serviceAccountName)" 2^>^&1') do set SERVICE_ACCOUNT=%%i

if "!SERVICE_ACCOUNT!"=="" (
    echo [AVISO] Nao foi possivel obter service account automaticamente
    echo Tentando obter service account padrao do projeto...
    for /f "tokens=*" %%i in ('gcloud iam service-accounts list --format="value(email)" --filter="displayName:Compute Engine default service account" 2^>^&1') do set SERVICE_ACCOUNT=%%i
)

if "!SERVICE_ACCOUNT!"=="" (
    echo [ERRO] Nao foi possivel identificar o service account
    echo O service account padrao geralmente e: %PROJECT_ID%@appspot.gserviceaccount.com
    set SERVICE_ACCOUNT=%PROJECT_ID%@appspot.gserviceaccount.com
)

echo Service Account: !SERVICE_ACCOUNT!
echo.

echo ========================================
echo 2. VERIFICANDO PERMISSOES IAM
echo ========================================
echo.

echo Verificando role: roles/cloudsql.client
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:!SERVICE_ACCOUNT!" >nul 2>&1

echo.
echo Verificando se o service account tem a role necessaria...
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:!SERVICE_ACCOUNT!" | findstr /i "cloudsql.client" >nul 2>&1

if errorlevel 1 (
    echo [ERRO] Service account NAO TEM a role roles/cloudsql.client
    echo.
    echo ========================================
    echo   SOLUCAO: ADICIONAR PERMISSAO
    echo ========================================
    echo.
    echo Execute o comando abaixo para adicionar a permissao:
    echo.
    echo gcloud projects add-iam-policy-binding %PROJECT_ID% ^
    echo     --member="serviceAccount:!SERVICE_ACCOUNT!" ^
    echo     --role="roles/cloudsql.client"
    echo.
    echo Deseja adicionar a permissao agora? (S/N)
    set /p ADICIONAR_PERMISSAO=
    if /i "!ADICIONAR_PERMISSAO!"=="S" (
        echo Adicionando permissao...
        gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:!SERVICE_ACCOUNT!" --role="roles/cloudsql.client"
        if errorlevel 1 (
            echo [ERRO] Falha ao adicionar permissao
        ) else (
            echo [OK] Permissao adicionada com sucesso!
        )
    )
) else (
    echo [OK] Service account TEM a role roles/cloudsql.client
)

echo.
echo ========================================
echo 3. VERIFICANDO CONFIGURACAO DO CLOUD RUN
echo ========================================
echo.

echo Verificando se --add-cloudsql-instances foi configurado...
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(spec.template.spec.containers[0].env)" | findstr /i "CLOUD_SQL" >nul 2>&1

if errorlevel 1 (
    echo [AVISO] CLOUD_SQL_CONNECTION_NAME pode nao estar configurado nas variaveis de ambiente
) else (
    echo [OK] CLOUD_SQL_CONNECTION_NAME encontrado nas variaveis de ambiente
)

gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(spec.template.spec.containers[0].env)" | findstr /i "cloudsql" >nul 2>&1

if errorlevel 1 (
    echo [AVISO] Cloud SQL instances pode nao estar conectado
    echo.
    echo Verifique se o deploy foi feito com: --add-cloudsql-instances
) else (
    echo [OK] Cloud SQL instances configurado
)

echo.
echo ========================================
echo 4. VERIFICANDO CLOUD SQL INSTANCE
echo ========================================
echo.

echo Verificando se a instancia existe e esta rodando...
gcloud sql instances describe %DB_INSTANCE% --format="value(state)" 2>nul | findstr /i "RUNNABLE" >nul 2>&1

if errorlevel 1 (
    echo [ERRO] Instancia %DB_INSTANCE% nao encontrada ou nao esta rodando
    echo.
    echo Verifique:
    echo   1. Nome da instancia esta correto?
    echo   2. Instancia esta na regiao %REGION%?
    echo   3. Instancia esta rodando?
) else (
    echo [OK] Instancia %DB_INSTANCE% esta rodando
)

echo.
echo ========================================
echo 5. VERIFICANDO CONNECTION NAME
echo ========================================
echo.

set EXPECTED_CONNECTION_NAME=%PROJECT_ID%:%REGION%:%DB_INSTANCE%
echo Connection Name esperado: %EXPECTED_CONNECTION_NAME%
echo.
echo Verifique se esta configurado no Cloud Run como:
echo   CLOUD_SQL_CONNECTION_NAME=%EXPECTED_CONNECTION_NAME%

echo.
echo ========================================
echo   VERIFICACAO CONCLUIDA
echo ========================================
echo.
pause

endlocal



