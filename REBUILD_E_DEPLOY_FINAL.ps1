# Rebuild e Deploy Final com todas as correções
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "🔨 Passo 1: Fazendo rebuild da imagem Docker..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar alguns minutos..." -ForegroundColor Cyan
gcloud builds submit --tag $IMAGE_NAME --timeout=20m

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Passo 2: Fazendo deploy no Cloud Run..." -ForegroundColor Yellow

gcloud run deploy monpec `
  --image=$IMAGE_NAME `
  --region=$REGION `
  --platform=managed `
  --allow-unauthenticated `
  --memory=2Gi `
  --cpu=2 `
  --timeout=300 `
  --max-instances=10 `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --no-cpu-throttling

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Teste o sistema em:" -ForegroundColor Cyan
Write-Host "   https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor White
Write-Host ""
Write-Host "📋 Para verificar logs em caso de erro:" -ForegroundColor Yellow
Write-Host "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR\" --limit=5 --format=\"value(timestamp,textPayload)\" --freshness=10m" -ForegroundColor Gray


