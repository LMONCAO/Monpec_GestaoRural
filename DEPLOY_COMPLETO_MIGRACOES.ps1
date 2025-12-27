# ========================================
# DEPLOY COMPLETO - MIGRAÇÕES
# Faz tudo automaticamente: rebuild, criar job, executar e verificar
# ========================================

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$JOB_NAME = "migrate-monpec"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETO - MIGRAÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
Write-Host "📋 Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar projeto!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Projeto configurado: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Passo 1: Criar build-config.yaml
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 1/5: Criando configuração de build..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$buildConfig = @"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '--no-cache', '--tag', 'gcr.io/`$PROJECT_ID/monpec:latest', '--file', 'Dockerfile.prod', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/`$PROJECT_ID/monpec:latest']
images:
  - 'gcr.io/`$PROJECT_ID/monpec:latest'
options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
timeout: '1800s'
"@

$buildConfig | Out-File -FilePath "build-config.yaml" -Encoding UTF8
Write-Host "✅ build-config.yaml criado" -ForegroundColor Green
Write-Host ""

# Passo 2: Rebuild da imagem Docker
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 2/5: Fazendo rebuild da imagem Docker..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⚠️  Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --config=build-config.yaml --timeout=30m

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Passo 3: Deletar job antigo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 3/5: Removendo job antigo..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>$null
if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {
    Write-Host "✅ Job antigo removido (ou não existia)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Aviso ao remover job antigo (continuando...)" -ForegroundColor Yellow
}
Write-Host ""

# Passo 4: Criar novo job
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 4/5: Criando novo job de migração..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create $JOB_NAME `
    --image ${IMAGE_NAME}:latest `
    --region $REGION `
    --project $PROJECT_ID `
    --set-env-vars $envVars `
    --command python `
    --args manage.py,migrate,--noinput `
    --max-retries 1 `
    --task-timeout 900 `
    --memory=2Gi `
    --cpu=2 `
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar job!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Job criado com sucesso!" -ForegroundColor Green
Write-Host ""

# Passo 5: Executar migrações
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 5/5: Executando migrações..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⚠️  Isso pode levar alguns minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro na execução das migrações!" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Verificando logs..." -ForegroundColor Yellow
    
    # Obter última execução
    $LATEST_EXECUTION = gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>$null | Select-Object -First 1
    
    if (-not [string]::IsNullOrEmpty($LATEST_EXECUTION)) {
        Write-Host ""
        Write-Host "📋 Logs da execução: $LATEST_EXECUTION" -ForegroundColor Cyan
        Write-Host ""
        
        $logQuery = "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION"
        gcloud logging read $logQuery --project $PROJECT_ID --limit=50 --format="table(timestamp,severity,textPayload)" --freshness=1h 2>$null | Select-Object -First 30
    }
    
    Write-Host ""
    Write-Host "💡 Para ver mais detalhes:" -ForegroundColor Yellow
    Write-Host "   .\VERIFICAR_MIGRACOES.ps1" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅✅✅ SUCESSO! MIGRAÇÕES EXECUTADAS COM SUCESSO!" -ForegroundColor Green
Write-Host ""

# Verificar resultado final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO RESULTADO FINAL..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$LATEST_EXECUTION = gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>$null | Select-Object -First 1

if (-not [string]::IsNullOrEmpty($LATEST_EXECUTION)) {
    $STATUS = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>$null
    $COMPLETED_COUNT = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.succeededCount)" 2>$null
    $FAILED_COUNT = gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.failedCount)" 2>$null
    
    if ([string]::IsNullOrEmpty($COMPLETED_COUNT)) { $COMPLETED_COUNT = "0" }
    if ([string]::IsNullOrEmpty($FAILED_COUNT)) { $FAILED_COUNT = "0" }
    
    Write-Host "Status: $STATUS" -ForegroundColor $(if ($STATUS -eq "True") { "Green" } else { "Red" })
    Write-Host "Tarefas concluídas: $COMPLETED_COUNT" -ForegroundColor Green
    Write-Host "Tarefas falhadas: $FAILED_COUNT" -ForegroundColor $(if ([int]$FAILED_COUNT -eq 0) { "Green" } else { "Red" })
    Write-Host ""
    
    if ($STATUS -eq "True" -and [int]$COMPLETED_COUNT -gt 0) {
        Write-Host "🎉🎉🎉 TUDO PRONTO! 🎉🎉🎉" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Seu sistema está disponível em:" -ForegroundColor Cyan
        Write-Host "   https://monpec-29862706245.us-central1.run.app" -ForegroundColor Green
        Write-Host "   https://monpec-fzzfjppzva-uc.a.run.app" -ForegroundColor Green
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROCESSO CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""








