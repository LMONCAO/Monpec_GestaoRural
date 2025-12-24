# Script para corrigir usuário admin no Google Cloud Run
# Execute: .\CORRIGIR_ADMIN_GCP.ps1

$ErrorActionPreference = "Stop"

$ProjectId = "monpec-sistema-rural"
$Region = "us-central1"
$ImageName = "gcr.io/$ProjectId/monpec"
$JobName = "monpec-corrigir-admin"

# Verificar se gcloud está instalado
$gcloudPath = "gcloud"
if (Get-Command $gcloudPath -ErrorAction SilentlyContinue) {
    $gcloudPath = "gcloud"
} elseif (Test-Path "C:\Users\$env:USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd") {
    $gcloudPath = "C:\Users\$env:USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
} else {
    Write-Host "❌ gcloud não encontrado. Instale o Google Cloud SDK primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGINDO USUÁRIO ADMIN" -ForegroundColor Cyan
Write-Host "  Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
Write-Host "Configurando projeto: $ProjectId" -ForegroundColor Yellow
& $gcloudPath config set project $ProjectId

# Comando Python para corrigir admin (tudo em uma linha)
$pythonCommand = 'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model, authenticate; User = get_user_model(); username = "admin"; password = "L6171r12@@"; user, created = User.objects.get_or_create(username=username, defaults={"email": "admin@monpec.com.br", "is_staff": True, "is_superuser": True, "is_active": True}); user.set_password(password); user.is_staff = True; user.is_superuser = True; user.is_active = True; user.email = "admin@monpec.com.br"; user.save(); print("✅ Admin corrigido!"); print(f"Username: {username}"); print(f"Password: {password}"); auth = authenticate(username=username, password=password); print(f"✅ Autenticação: {\"SUCESSO\" if auth else \"FALHOU\"}")'

Write-Host "Criando/atualizando Cloud Run Job..." -ForegroundColor Yellow

# Verificar se o job existe
$jobExists = $null
try {
    $jobExists = & $gcloudPath run jobs describe $JobName --region $Region --format="value(metadata.name)" 2>&1 | Out-String
} catch {
    $jobExists = $null
}

if (-not $jobExists -or $jobExists -match "ERROR" -or $jobExists -match "Cannot find job") {
    Write-Host "Criando novo job..." -ForegroundColor Yellow
    & $gcloudPath run jobs create $JobName `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args "-c","$escapedCommand" `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao criar job" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Job criado!" -ForegroundColor Green
} else {
    Write-Host "Atualizando job existente..." -ForegroundColor Yellow
    & $gcloudPath run jobs update $JobName `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args "-c","$escapedCommand" `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao atualizar job" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Job atualizado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Executando correção do admin..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos...)" -ForegroundColor Gray
Write-Host ""

# Executar o job
& $gcloudPath run jobs execute $JobName --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao executar job" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verificando logs..." -ForegroundColor Yellow
    & $gcloudPath logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JobName" --limit 30 --format="value(textPayload)" --project $ProjectId | Select-Object -Last 30
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ ADMIN CORRIGIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Credenciais:" -ForegroundColor Cyan
Write-Host "  Usuário: admin" -ForegroundColor White
Write-Host "  Senha: L6171r12@@" -ForegroundColor White
Write-Host "  Email: admin@monpec.com.br" -ForegroundColor White
Write-Host ""
Write-Host "Acesse: https://monpec.com.br/login/" -ForegroundColor Green
Write-Host ""

# Perguntar se deseja remover o job
Write-Host "Deseja remover o job temporário? (S/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host
if ($response -eq "S" -or $response -eq "s") {
    & $gcloudPath run jobs delete $JobName --region $Region --quiet
    Write-Host "✅ Job removido" -ForegroundColor Green
} else {
    Write-Host "Job mantido para uso futuro" -ForegroundColor Gray
}

Write-Host ""

