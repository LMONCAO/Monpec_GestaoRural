# Rebuild e Deploy com correções de ProgrammingError
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "🔨 Fazendo rebuild da imagem Docker..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME --timeout=20m

Write-Host ""
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
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

Write-Host ""
Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host "🌐 Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan

