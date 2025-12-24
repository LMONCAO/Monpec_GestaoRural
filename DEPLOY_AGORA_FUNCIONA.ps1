# Script de Deploy Completo - MONPEC para Google Cloud Run
# Versão que funciona mesmo com problemas de codificação de caminho

$ErrorActionPreference = "Stop"

# Configurações
$ProjectId = "monpec-sistema-rural"
$Region = "us-central1"
$ServiceName = "monpec"
$ImageName = "gcr.io/$ProjectId/$ServiceName"
$AdminPassword = "L6171r12@@"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "  Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar o diretório do projeto
$projDir = Get-ChildItem -Path "C:\Users\lmonc\Desktop" -Recurse -Directory -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -eq "Monpec_GestaoRural" } | 
    Select-Object -First 1 -ExpandProperty FullName

if (-not $projDir) {
    Write-Host "❌ Diretório do projeto não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Diretório do projeto: $projDir" -ForegroundColor Green
Set-Location $projDir
Write-Host ""

# Verificar gcloud
Write-Host "Verificando Google Cloud SDK..." -ForegroundColor Yellow
$gcloudPath = "C:\Users\lmonc\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
if (-not (Test-Path $gcloudPath)) {
    Write-Host "❌ Google Cloud SDK não encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Google Cloud SDK encontrado" -ForegroundColor Green
Write-Host ""

# Verificar autenticação
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
& $gcloudPath auth list --filter=status:ACTIVE --format="value(account)" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Fazendo login..." -ForegroundColor Yellow
    & $gcloudPath auth login
}

Write-Host "✅ Autenticado" -ForegroundColor Green
Write-Host ""

# Configurar projeto
Write-Host "Configurando projeto: $ProjectId" -ForegroundColor Yellow
& $gcloudPath config set project $ProjectId
Write-Host "✅ Projeto configurado" -ForegroundColor Green
Write-Host ""

# Habilitar APIs
Write-Host "Habilitando APIs necessárias..." -ForegroundColor Yellow
& $gcloudPath services enable run.googleapis.com --quiet
& $gcloudPath services enable cloudbuild.googleapis.com --quiet
& $gcloudPath services enable sqladmin.googleapis.com --quiet
& $gcloudPath services enable containerregistry.googleapis.com --quiet
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Build da imagem
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 1: BUILD DA IMAGEM DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔨 Construindo imagem Docker..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos...)" -ForegroundColor Gray
Write-Host ""

& $gcloudPath builds submit --tag $ImageName --timeout=30m

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao construir imagem Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Imagem construída com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy no Cloud Run
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 2: DEPLOY NO CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
Write-Host ""

# Verificar se o serviço já existe
$existingService = & $gcloudPath run services describe $ServiceName --region $Region --format="value(metadata.name)" 2>&1

if ($existingService -and $existingService -ne "" -and $existingService -notmatch "ERROR") {
    Write-Host "Serviço existente encontrado. Atualizando..." -ForegroundColor Gray
} else {
    Write-Host "Criando novo serviço..." -ForegroundColor Gray
}

& $gcloudPath run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao fazer deploy" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL do serviço
$ServiceUrl = & $gcloudPath run services describe $ServiceName --region $Region --format="value(status.url)" 2>&1
Write-Host "URL do serviço: $ServiceUrl" -ForegroundColor Cyan
Write-Host ""

# Executar migrações
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 3: EXECUTAR MIGRAÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 Executando migrações do banco de dados..." -ForegroundColor Yellow
Write-Host ""

# Criar job de migração se não existir
$migrateJobExists = & $gcloudPath run jobs describe monpec-migrate --region $Region --format="value(metadata.name)" 2>&1

if (-not $migrateJobExists -or $migrateJobExists -match "ERROR") {
    Write-Host "Criando job de migração..." -ForegroundColor Gray
    & $gcloudPath run jobs create monpec-migrate `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args manage.py,migrate `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
}

# Executar migração
Write-Host "Executando migrações..." -ForegroundColor Yellow
& $gcloudPath run jobs execute monpec-migrate --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Aviso: Erro ao executar migrações" -ForegroundColor Yellow
    Write-Host "Você pode executar manualmente depois" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✅ Migrações executadas com sucesso!" -ForegroundColor Green
}
Write-Host ""

# Criar usuário admin
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 4: CRIAR USUÁRIO ADMIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Criando usuário administrador..." -ForegroundColor Yellow
Write-Host ""

# Criar job de criação de admin se não existir
$adminJobExists = & $gcloudPath run jobs describe monpec-create-admin --region $Region --format="value(metadata.name)" 2>&1

if (-not $adminJobExists -or $adminJobExists -match "ERROR") {
    Write-Host "Criando job de criação de admin..." -ForegroundColor Gray
    & $gcloudPath run jobs create monpec-create-admin `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args criar_admin.py `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
}

# Executar criação de admin
Write-Host "Executando criação do usuário admin..." -ForegroundColor Yellow
& $gcloudPath run jobs execute monpec-create-admin --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Aviso: Erro ao criar usuário admin" -ForegroundColor Yellow
    Write-Host "Você pode executar manualmente depois" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✅ Usuário admin criado com sucesso!" -ForegroundColor Green
}
Write-Host ""

# Resumo final
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY COMPLETO CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 INFORMAÇÕES DE ACESSO:" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL do Sistema: $ServiceUrl" -ForegroundColor White
Write-Host ""
Write-Host "Credenciais de Acesso:" -ForegroundColor Yellow
Write-Host "  Usuário: admin" -ForegroundColor White
Write-Host "  Senha: $AdminPassword" -ForegroundColor White
Write-Host ""
















