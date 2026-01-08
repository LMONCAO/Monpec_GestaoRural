@echo off
chcp 65001 >nul
echo ========================================
echo   DEPLOY ALTERACOES LANDING PAGE
echo ========================================
echo.
echo Alteracoes:
echo - Modal de cadastro demo
echo - Ajustes de responsividade mobile
echo.
echo [1/4] Verificando autenticacao...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if errorlevel 1 (
    echo Fazendo login...
    gcloud auth login
)

echo.
echo [2/4] Configurando projeto...
gcloud config set project monpec-sistema-rural
if errorlevel 1 (
    echo [ERRO] Falha ao configurar projeto
    pause
    exit /b 1
)

echo.
echo [3/4] Fazendo build da imagem (SEM CACHE)...
echo [AVISO] Este processo pode levar 5-15 minutos...
echo [AVISO] Por favor, aguarde e NAO feche esta janela!
echo.

set IMAGE_NAME=gcr.io/monpec-sistema-rural/sistema-rural

gcloud builds submit --no-cache --tag %IMAGE_NAME% .
if errorlevel 1 (
    echo [ERRO] Falha no build!
    pause
    exit /b 1
)

echo.
echo [4/4] Fazendo deploy no Cloud Run...
echo [AVISO] Este processo pode levar 3-10 minutos...
echo [AVISO] Por favor, aguarde e NAO feche esta janela!
echo.

set CLOUD_SQL_CONN=monpec-sistema-rural:us-central1:monpec-db
set SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE
set DB_PASSWORD=L6171r12@@jjms
set DJANGO_SUPERUSER_PASSWORD=L6171r12@@

gcloud run deploy monpec ^
    --image %IMAGE_NAME% ^
    --region=us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=%CLOUD_SQL_CONN% ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=%SECRET_KEY%,CLOUD_SQL_CONNECTION_NAME=%CLOUD_SQL_CONN%,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=%DB_PASSWORD%,DJANGO_SUPERUSER_PASSWORD=%DJANGO_SUPERUSER_PASSWORD%,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural,DEMO_USER_PASSWORD=monpec" ^
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

echo.
echo ========================================
echo   DEPLOY CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Alteracoes aplicadas:
echo - Modal de cadastro demo funcional
echo - Header mobile responsivo
echo - Hero section otimizada para celular
echo.
echo IMPORTANTE:
echo 1. Aguarde 1-2 minutos para o servico inicializar
echo 2. Limpe o cache do navegador (Ctrl+F5 ou Ctrl+Shift+R)
echo 3. Teste no celular para verificar a responsividade
echo.
pause


