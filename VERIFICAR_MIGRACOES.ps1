# ========================================
# VERIFICAR STATUS DAS MIGRAÇÕES
# ========================================

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$JOB_NAME = "migrate-monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO STATUS DAS MIGRAÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
gcloud config set project $PROJECT_ID 2>$null

# Obter a última execução
Write-Host "1. Buscando última execução do job..." -ForegroundColor Yellow
$LATEST_EXECUTION = gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>$null | Select-Object -First 1

if ([string]::IsNullOrEmpty($LATEST_EXECUTION)) {
    Write-Host "❌ Nenhuma execução encontrada!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Execução encontrada: $LATEST_EXECUTION" -ForegroundColor Green
Write-Host ""

# Verificar status
Write-Host "2. Verificando status da execução..." -ForegroundColor Yellow
$STATUS = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>$null
$COMPLETED_COUNT = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.succeededCount)" 2>$null
$FAILED_COUNT = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.failedCount)" 2>$null

if ([string]::IsNullOrEmpty($COMPLETED_COUNT)) { $COMPLETED_COUNT = "0" }
if ([string]::IsNullOrEmpty($FAILED_COUNT)) { $FAILED_COUNT = "0" }

Write-Host "   Status: $STATUS"
Write-Host "   Tarefas concluídas: $COMPLETED_COUNT"
Write-Host "   Tarefas falhadas: $FAILED_COUNT"
Write-Host ""

if ($STATUS -eq "True" -and [int]$COMPLETED_COUNT -gt 0) {
    Write-Host "✅✅✅ SUCESSO! MIGRAÇÕES EXECUTADAS COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Seu sistema está pronto:" -ForegroundColor Cyan
    Write-Host "   https://monpec-29862706245.us-central1.run.app" -ForegroundColor Green
    Write-Host ""
    exit 0
}
elseif ($STATUS -eq "False" -or [int]$FAILED_COUNT -gt 0) {
    Write-Host "❌ ERRO NA EXECUÇÃO!" -ForegroundColor Red
    Write-Host ""
    Write-Host "3. Buscando logs do erro..." -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Tentar obter logs da execução
    $logQuery = "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION AND resource.labels.execution_name=$LATEST_EXECUTION"
    gcloud logging read $logQuery --project $PROJECT_ID --limit=100 --format="table(timestamp,severity,textPayload)" --freshness=1h 2>$null | Select-Object -First 50
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Para ver mais detalhes:" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💡 Para ver logs completos:" -ForegroundColor Yellow
    Write-Host "   gcloud logging read `"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME`" --limit=200 --format=`"table(timestamp,severity,textPayload)`"" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
else {
    Write-Host "⏳ Execução ainda em andamento..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Para acompanhar em tempo real:" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --watch" -ForegroundColor Gray
    Write-Host ""
    exit 0
}








