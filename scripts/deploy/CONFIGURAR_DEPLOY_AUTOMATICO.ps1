# Script para Configurar Deploy Automático - GitHub Actions para Google Cloud
# Execute este script para configurar tudo automaticamente

param(
    [switch]$ApenasVerificar
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Configuração Deploy Automático" -ForegroundColor Cyan
Write-Host "MONPEC - Google Cloud Run via GitHub Actions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$SA_NAME = "github-actions-deploy"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Funções auxiliares
function Write-Step {
    param([string]$Message)
    Write-Host "📌 $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Verificar gcloud CLI
Write-Step "Verificando gcloud CLI..."
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Error "gcloud CLI não encontrado!"
    Write-Info "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Success "gcloud CLI encontrado: $($gcloudPath.Source)"

# Verificar autenticação
Write-Step "Verificando autenticação no Google Cloud..."
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $currentAccount -or $currentAccount -match "ERROR") {
    Write-Info "Fazendo login no Google Cloud..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
} else {
    Write-Success "Autenticado como: $currentAccount"
}

# Configurar projeto
Write-Step "Configurando projeto GCP: $PROJECT_ID"
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    Write-Info "Certifique-se de ter acesso ao projeto: $PROJECT_ID"
    exit 1
}
Write-Success "Projeto configurado!"

# Verificar se a service account existe
Write-Step "Verificando Service Account: $SA_EMAIL"
$saExists = gcloud iam service-accounts describe $SA_EMAIL 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Service Account não existe. Criando..."
    Write-Host ""
    Write-Host "🔧 Criando Service Account..." -ForegroundColor Yellow
    
    # Criar service account
    gcloud iam service-accounts create $SA_NAME `
        --display-name="GitHub Actions Deploy" `
        --description="Service account para deploy automático via GitHub Actions" `
        --quiet 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao criar service account!"
        Write-Info "Tente criar manualmente no console: https://console.cloud.google.com/iam-admin/serviceaccounts?project=$PROJECT_ID"
        exit 1
    }
    Write-Success "Service Account criada!"
    
    # Aguardar um pouco para a service account ser propagada
    Start-Sleep -Seconds 2
    
} else {
    Write-Success "Service Account já existe!"
}

# Definir roles necessárias
$roles = @(
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/cloudbuild.builds.editor",
    "roles/storage.admin",
    "roles/cloudsql.client"
)

Write-Step "Configurando permissões da Service Account..."
foreach ($role in $roles) {
    Write-Host "  Adicionando: $role" -ForegroundColor Gray
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SA_EMAIL" `
        --role="$role" `
        --condition=None `
        --quiet 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ $role" -ForegroundColor Green
    } else {
        Write-Host "    ⚠️  $role (pode já estar atribuída)" -ForegroundColor Yellow
    }
}

Write-Success "Permissões configuradas!"

# Habilitar APIs necessárias
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Habilitando: $api" -ForegroundColor Gray
    gcloud services enable $api --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ $api" -ForegroundColor Green
    }
}
Write-Success "APIs habilitadas!"

# Criar chave JSON
Write-Step "Criando chave JSON para Service Account..."
$keyFile = "github-actions-deploy-key.json"
if (Test-Path $keyFile) {
    Write-Info "Arquivo $keyFile já existe. Removendo..."
    Remove-Item $keyFile -Force
}

Write-Host "  Gerando chave JSON..." -ForegroundColor Gray
gcloud iam service-accounts keys create $keyFile `
    --iam-account=$SA_EMAIL `
    --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao criar chave JSON!"
    Write-Info "Tente criar manualmente no console do GCP"
    exit 1
}

Write-Success "Chave JSON criada: $keyFile"
Write-Host ""

# Verificar conteúdo do arquivo
$keyContent = Get-Content $keyFile -Raw
if ($keyContent -match '"private_key"') {
    Write-Success "Chave JSON válida!"
} else {
    Write-Error "Chave JSON inválida!"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ CONFIGURAÇÃO NO GOOGLE CLOUD CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 📤 Configure o Secret no GitHub:" -ForegroundColor Cyan
Write-Host "   a) Abra o arquivo: $keyFile" -ForegroundColor White
Write-Host "   b) Copie TODO o conteúdo (desde o { até o })" -ForegroundColor White
Write-Host "   c) Acesse: https://github.com/LMONCAO/monpec/settings/secrets/actions" -ForegroundColor White
Write-Host "   d) Clique em 'New repository secret'" -ForegroundColor White
Write-Host "   e) Name: GCP_SA_KEY" -ForegroundColor White
Write-Host "   f) Secret: Cole o conteúdo do arquivo JSON" -ForegroundColor White
Write-Host "   g) Clique em 'Add secret'" -ForegroundColor White
Write-Host ""
Write-Host "2. 📤 Faça push do código para o GitHub:" -ForegroundColor Cyan
Write-Host "   git add .github/workflows/deploy-gcp.yml" -ForegroundColor White
Write-Host "   git commit -m 'Configurar deploy automático'" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "3. ✅ Pronto! O deploy será executado automaticamente!" -ForegroundColor Green
Write-Host ""

Write-Host "🔒 SEGURANÇA:" -ForegroundColor Yellow
Write-Host "   - O arquivo $keyFile contém credenciais sensíveis" -ForegroundColor White
Write-Host "   - NÃO faça commit deste arquivo no Git!" -ForegroundColor Red
Write-Host "   - Após configurar no GitHub, você pode deletar o arquivo local" -ForegroundColor White
Write-Host "   - O arquivo está em: $((Get-Item $keyFile).FullName)" -ForegroundColor Gray
Write-Host ""

# Verificar se arquivo está no .gitignore
$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    if ($gitignoreContent -notmatch $keyFile) {
        Write-Host "📝 Adicionando $keyFile ao .gitignore..." -ForegroundColor Yellow
        Add-Content $gitignorePath "`n# GitHub Actions Service Account Key`n$keyFile"
        Write-Success "Arquivo adicionado ao .gitignore"
    }
} else {
    Write-Host "📝 Criando .gitignore..." -ForegroundColor Yellow
    Set-Content $gitignorePath "# GitHub Actions Service Account Key`n$keyFile"
    Write-Success ".gitignore criado"
}

Write-Host ""
Write-Host "🎉 Configuração concluída com sucesso!" -ForegroundColor Green
Write-Host ""








