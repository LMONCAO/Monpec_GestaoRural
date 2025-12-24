@echo off
chcp 65001 >nul
echo ========================================
echo DEPLOY NO GOOGLE CLOUD - MONPEC
echo ========================================
echo.

echo [1/5] Habilitando APIs necessárias...
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
echo [OK] APIs habilitadas
echo.

echo [2/5] Coletando arquivos estáticos...
python manage.py collectstatic --noinput
echo [OK] Arquivos estáticos coletados
echo.

echo [3/5] Verificando Dockerfile...
if not exist "Dockerfile" (
    echo [AVISO] Dockerfile não encontrado, será criado automaticamente pelo Cloud Run
)
echo.

echo [4/5] Fazendo deploy no Cloud Run...
echo Serviço: monpec-gestao-rural
echo Região: southamerica-east1
echo.
echo Isso pode levar alguns minutos...
echo.

gcloud run deploy monpec-gestao-rural ^
    --source . ^
    --region southamerica-east1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10

if errorlevel 1 (
    echo.
    echo [ERRO] Falha no deploy
    echo Verifique os logs acima para mais detalhes
    pause
    exit /b 1
)

echo.
echo ========================================
echo DEPLOY CONCLUÍDO COM SUCESSO!
echo ========================================
echo.

echo [5/5] Obtendo URL do serviço...
gcloud run services describe monpec-gestao-rural --region southamerica-east1 --format="value(status.url)"

echo.
echo ========================================
echo PRÓXIMOS PASSOS:
echo ========================================
echo.
echo 1. Configurar variáveis de ambiente no GCP Console:
echo    - Ir para Cloud Run ^> monpec-gestao-rural ^> Editar e implantar nova revisão
echo    - Adicionar variáveis de ambiente:
echo      * DEBUG=False
echo      * SECRET_KEY=(sua chave secreta)
echo      * ALLOWED_HOSTS=(URL do serviço)
echo      * DATABASE_URL=(se usar Cloud SQL)
echo      * STRIPE_SECRET_KEY=(sua chave Stripe)
echo      * STRIPE_PUBLISHABLE_KEY=(sua chave pública)
echo      * STRIPE_WEBHOOK_SECRET=(seu webhook secret)
echo      * EMAIL_HOST=(servidor de email)
echo      * EMAIL_PORT=587
echo      * EMAIL_HOST_USER=(usuário email)
echo      * EMAIL_HOST_PASSWORD=(senha email)
echo.
echo 2. Executar migrações (se necessário):
echo    gcloud run services update monpec-gestao-rural --region southamerica-east1 --command "python" --args "manage.py,migrate"
echo.
echo 3. Testar o sistema acessando a URL acima
echo.
pause







