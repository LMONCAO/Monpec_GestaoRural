@echo off
REM ============================================
REM DEPLOY DEFINITIVO - CÓDIGO LOCAL
REM ============================================
REM Este script faz deploy DIRETO do código LOCAL
REM Funciona no Prompt de Comando (cmd.exe)
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   DEPLOY DEFINITIVO - CODIGO LOCAL
echo ========================================
echo.

REM ============================================
REM CONFIGURAÇÕES
REM ============================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1
set DB_PASSWORD=L6171r12@@jjms
set SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE

echo [CONFIGURACOES]
echo   Projeto: %PROJECT_ID%
echo   Servico: %SERVICE_NAME%
echo   Regiao: %REGION%
echo.

REM ============================================
REM ETAPA 1: VERIFICAÇÕES LOCAIS
REM ============================================
echo [ETAPA 1] Verificando codigo local...

if not exist "Dockerfile.prod" (
    echo [ERRO] Dockerfile.prod nao encontrado!
    pause
    exit /b 1
)
echo [OK] Dockerfile.prod encontrado

if not exist "manage.py" (
    echo [ERRO] manage.py nao encontrado! Voce esta no diretorio correto?
    pause
    exit /b 1
)
echo [OK] manage.py encontrado

if not exist "sistema_rural\settings_gcp.py" (
    echo [ERRO] sistema_rural\settings_gcp.py nao encontrado!
    pause
    exit /b 1
)
echo [OK] settings_gcp.py encontrado

REM Verificar requirements
if not exist "requirements_producao.txt" (
    echo [INFO] requirements_producao.txt nao encontrado, criando...
    if exist "requirements.txt" (
        copy "requirements.txt" "requirements_producao.txt" >nul
        echo [OK] Copiado de requirements.txt
    ) else (
        echo [ERRO] Nenhum arquivo requirements encontrado!
        pause
        exit /b 1
    )
)

REM Garantir openpyxl
findstr /C:"openpyxl" requirements_producao.txt >nul
if errorlevel 1 (
    echo [INFO] Adicionando openpyxl ao requirements...
    echo openpyxl^>=3.1.5 >> requirements_producao.txt
    echo [OK] openpyxl adicionado
)

echo [OK] Codigo local verificado!
echo.

REM ============================================
REM ETAPA 2: AUTENTICAÇÃO GOOGLE CLOUD
REM ============================================
echo [ETAPA 2] Autenticando no Google Cloud...

gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Nao autenticado. Fazendo login...
    gcloud auth login
    if errorlevel 1 (
        echo [ERRO] Falha na autenticacao!
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%a in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>nul') do set AUTH_EMAIL=%%a
    echo [OK] Autenticado: !AUTH_EMAIL!
)

REM Configurar projeto
echo [INFO] Configurando projeto: %PROJECT_ID%
gcloud config set project %PROJECT_ID% >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Erro ao configurar projeto!
    pause
    exit /b 1
)
echo [OK] Projeto configurado
echo.

REM ============================================
REM ETAPA 3: CORRIGIR SENHA DO BANCO
REM ============================================
echo [ETAPA 3] Corrigindo senha do banco...

gcloud sql users set-password monpec_user --instance=monpec-db --password=%DB_PASSWORD% >nul 2>&1
if errorlevel 1 (
    echo [INFO] Aviso: Nao foi possivel atualizar senha (pode ser normal)
) else (
    echo [OK] Senha do banco atualizada
)
echo.

REM ============================================
REM ETAPA 4: BUILD DA IMAGEM (CÓDIGO LOCAL)
REM ============================================
echo [ETAPA 4] Buildando imagem Docker (CODIGO LOCAL)
echo [INFO] IMPORTANTE: O build vai usar os arquivos DESTE diretorio local!
echo [INFO] Isso garante que a versao mais recente seja enviada.
echo.

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "TIMESTAMP=%YYYY%%MM%%DD%%HH%%Min%%Sec%"

set IMAGE_TAG=gcr.io/%PROJECT_ID%/%SERVICE_NAME%:%TIMESTAMP%

echo [INFO] Tag da imagem: %IMAGE_TAG%
echo [INFO] Tempo estimado: 5-10 minutos
echo.

REM Fazer build DIRETO do código local
echo [INFO] Enviando codigo local para o Cloud Build...
gcloud builds submit --tag %IMAGE_TAG% --timeout=20m --ignore-file=.gcloudignore

if errorlevel 1 (
    echo [ERRO] Erro no build!
    echo [INFO] Verifique os logs acima para mais detalhes.
    pause
    exit /b 1
)

echo [OK] Build concluido! Imagem: %IMAGE_TAG%
echo.

REM ============================================
REM ETAPA 5: DEPLOY NO CLOUD RUN
REM ============================================
echo [ETAPA 5] Deployando no Cloud Run...

set ENV_VARS=DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%PROJECT_ID%:%REGION%:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%

echo [INFO] Variaveis de ambiente configuradas
echo [INFO] Tempo estimado: 2-5 minutos
echo.

gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_TAG% ^
    --region=%REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%PROJECT_ID%:%REGION%:monpec-db ^
    --set-env-vars %ENV_VARS% ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=600 ^
    --min-instances=0 ^
    --max-instances=10

if errorlevel 1 (
    echo [ERRO] Erro no deploy!
    pause
    exit /b 1
)

echo [OK] Deploy concluido!
echo.

REM ============================================
REM ETAPA 6: OBTER URL E VERIFICAR
REM ============================================
echo [ETAPA 6] Obtendo URL do servico...

for /f "tokens=*" %%a in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" 2^>nul') do set SERVICE_URL=%%a

if defined SERVICE_URL (
    echo.
    echo ========================================
    echo   [OK] DEPLOY CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    echo [URL] URL do Servico:
    echo    %SERVICE_URL%
    echo.
    echo [CREDENCIAIS] Credenciais para Login:
    echo    Username: admin
    echo    Senha: L6171r12@@
    echo.
    echo [IMAGEM] Imagem criada:
    echo    %IMAGE_TAG%
    echo.
    echo [INFO] Aguarde 30-60 segundos para o servico inicializar completamente.
    echo [INFO] Depois acesse a URL acima e faca login.
    echo.
) else (
    echo [ERRO] Nao foi possivel obter a URL do servico!
    echo [INFO] Verifique manualmente no console: https://console.cloud.google.com/run
)

echo.
echo [OK] Processo concluido!
echo.
pause


