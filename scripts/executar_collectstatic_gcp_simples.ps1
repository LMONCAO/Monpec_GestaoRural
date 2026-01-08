# Script simples para executar collectstatic no Google Cloud Run
# Sistema: Monpec - monpec.com.br

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$JOB_NAME = "collectstatic-monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COLECTAR ARQUIVOS ESTATICOS - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "Criando/atualizando job de collectstatic..." -ForegroundColor Yellow

# Verificar se Cloud SQL existe
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>&1
$cloudSqlArg = ""
if ($LASTEXITCODE -eq 0) {
    $cloudSqlArg = "--set-cloudsql-instances=$CONNECTION_NAME"
    Write-Host "Cloud SQL encontrado: $CONNECTION_NAME" -ForegroundColor Green
} else {
    Write-Host "Cloud SQL nao encontrado, continuando sem..." -ForegroundColor Yellow
}

# Criar ou atualizar job
$createCmd = "gcloud run jobs create $JOB_NAME --image=$IMAGE_NAME`:latest --region=$REGION --set-env-vars=DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp --memory=2Gi --cpu=1 --max-retries=3 --task-timeout=600 --command=python --args=manage.py,collectstatic,--noinput $cloudSqlArg --quiet"

$result = Invoke-Expression $createCmd 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Job ja existe, atualizando..." -ForegroundColor Yellow
    $updateCmd = $createCmd -replace "create", "update"
    Invoke-Expression $updateCmd 2>&1 | Out-Null
}

Write-Host ""
Write-Host "Executando collectstatic (aguarde 2-5 minutos)..." -ForegroundColor Yellow
Write-Host ""

gcloud run jobs execute $JOB_NAME --region $REGION --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "ARQUIVOS ESTATICOS COLETADOS COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "As imagens agora devem aparecer no site:" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto1.jpeg"
    Write-Host "   https://monpec.com.br/static/site/foto2.jpeg"
    Write-Host "   https://monpec.com.br/static/site/foto3.jpeg"
    Write-Host "   https://monpec.com.br/static/site/foto4.jpeg"
    Write-Host "   https://monpec.com.br/static/site/foto5.jpeg"
    Write-Host "   https://monpec.com.br/static/site/foto6.jpeg"
} else {
    Write-Host ""
    Write-Host "Erro ao executar collectstatic!" -ForegroundColor Red
    Write-Host "Verifique os logs:" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --limit=1"
}

Write-Host ""


