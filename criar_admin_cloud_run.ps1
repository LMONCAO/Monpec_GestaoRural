# Script para criar/corrigir usuário admin no Cloud Run
# Executa o script criar_admin.py via Cloud Run Job

$ErrorActionPreference = "Stop"

$ProjectId = "monpec-sistema-rural"
$Region = "us-central1"
$ImageName = "gcr.io/$ProjectId/monpec"
$gcloudPath = "C:\Users\lmonc\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIANDO/CORRIGINDO USUÁRIO ADMIN" -ForegroundColor Cyan
Write-Host "  Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o job existe
Write-Host "Verificando job de criação de admin..." -ForegroundColor Yellow
$adminJob = & $gcloudPath run jobs describe monpec-create-admin --region $Region --format="value(metadata.name)" 2>&1

if ($adminJob -match "ERROR" -or -not $adminJob) {
    Write-Host "Criando job de criação de admin..." -ForegroundColor Yellow
    & $gcloudPath run jobs create monpec-create-admin `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args criar_admin.py `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao criar job" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Job criado!" -ForegroundColor Green
} else {
    Write-Host "✅ Job encontrado, atualizando..." -ForegroundColor Green
    & $gcloudPath run jobs update monpec-create-admin `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args criar_admin.py `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
}

Write-Host ""
Write-Host "Executando criação do usuário admin..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos...)" -ForegroundColor Gray
Write-Host ""

& $gcloudPath run jobs execute monpec-create-admin --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao executar criação de admin" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verificando logs..." -ForegroundColor Yellow
    & $gcloudPath logging read "resource.type=cloud_run_job AND resource.labels.job_name=monpec-create-admin" --limit 20 --format="value(textPayload)" --project $ProjectId | Select-Object -Last 20
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ USUÁRIO ADMIN CRIADO/CORRIGIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Credenciais:" -ForegroundColor Cyan
Write-Host "  Usuário: admin" -ForegroundColor White
Write-Host "  Senha: L6171r12@@" -ForegroundColor White
Write-Host "  Email: admin@monpec.com.br" -ForegroundColor White
Write-Host ""
Write-Host "Agora você pode fazer login no sistema!" -ForegroundColor Green
Write-Host ""


































