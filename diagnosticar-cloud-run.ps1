# Script de diagnóstico para Cloud Run
# Verifica logs, status do serviço e variáveis de ambiente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO CLOUD RUN - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host "1. Verificando status do serviço..." -ForegroundColor Yellow
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.conditions)" 2>&1

Write-Host "`n2. Verificando últimas revisões..." -ForegroundColor Yellow
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=5 --format="table(metadata.name,status.conditions.type,status.conditions.status,metadata.creationTimestamp)"

Write-Host "`n3. Verificando logs recentes (últimas 50 linhas)..." -ForegroundColor Yellow
Write-Host "--- LOGS DE ERRO ---" -ForegroundColor Red
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=50 --project=$PROJECT_ID --format="table(timestamp,severity,textPayload,jsonPayload.message)" 2>&1

Write-Host "`n--- LOGS GERAIS (últimas 20) ---" -ForegroundColor Green
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=20 --project=$PROJECT_ID --format="table(timestamp,severity,textPayload)" 2>&1

Write-Host "`n4. Verificando variáveis de ambiente configuradas..." -ForegroundColor Yellow
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(spec.template.spec.containers[0].env)" 2>&1

Write-Host "`n5. Verificando recursos alocados..." -ForegroundColor Yellow
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(spec.template.spec.containers[0].resources)" 2>&1

Write-Host "`n6. Verificando timeout e configurações..." -ForegroundColor Yellow
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(spec.template.spec.timeoutSeconds,spec.template.spec.containerConcurrency)" 2>&1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO CONCLUÍDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPara ver logs em tempo real, execute:" -ForegroundColor Yellow
Write-Host "gcloud logging tail `"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME`" --project=$PROJECT_ID" -ForegroundColor White


