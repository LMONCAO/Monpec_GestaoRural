# 🚀 Script Completo para Configurar GitHub Actions → Google Cloud
# Este script automatiza a configuração completa do deploy automático

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_ACCOUNT_NAME = "github-actions-deploy"
$SERVICE_ACCOUNT_EMAIL = "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$KEY_FILE = "github-actions-key.json"

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 CONFIGURAR GITHUB ACTIONS - GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
Write-Log "Verificando gcloud CLI..."
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud CLI não encontrado! Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Success "gcloud CLI encontrado!"

# Verificar autenticação
Write-Log "Verificando autenticação no GCP..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR" -or $authCheck -eq "") {
    Write-Warning "Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Falha na autenticação!"
        exit 1
    }
}
Write-Success "Autenticado como: $authCheck"

# Configurar projeto
Write-Log "Configurando projeto..."
gcloud config set project $PROJECT_ID --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado: $PROJECT_ID"

# Verificar se service account já existe
Write-Log "Verificando se service account já existe..."
$saExists = gcloud iam service-accounts list --filter="email:$SERVICE_ACCOUNT_EMAIL" --format="value(email)" 2>&1
if ($saExists -and $saExists -eq $SERVICE_ACCOUNT_EMAIL) {
    Write-Warning "Service account já existe: $SERVICE_ACCOUNT_EMAIL"
    $createSA = $false
} else {
    Write-Log "Criando service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME `
        --display-name="GitHub Actions Deploy" `
        --description="Service account para deploy automático via GitHub Actions" `
        --project=$PROJECT_ID `
        --quiet 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao criar service account! Pode já existir."
        $createSA = $false
    } else {
        Write-Success "Service account criada: $SERVICE_ACCOUNT_EMAIL"
        $createSA = $true
    }
}

# Atribuir permissões
Write-Log "Atribuindo permissões necessárias..."
$roles = @(
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/cloudbuild.builds.editor",
    "roles/storage.admin"
)

foreach ($role in $roles) {
    Write-Log "  Atribuindo: $role"
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" `
        --role=$role `
        --condition=None `
        --quiet 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "    ✅ $role atribuída"
    } else {
        Write-Warning "    ⚠️  $role pode já estar atribuída ou ocorreu erro"
    }
}

# Criar chave JSON
Write-Log "Criando chave JSON para service account..."
if (Test-Path $KEY_FILE) {
    Write-Warning "Arquivo $KEY_FILE já existe. Removendo..."
    Remove-Item $KEY_FILE -Force
}

gcloud iam service-accounts keys create $KEY_FILE `
    --iam-account=$SERVICE_ACCOUNT_EMAIL `
    --project=$PROJECT_ID 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao criar chave JSON!"
    exit 1
}

if (-not (Test-Path $KEY_FILE)) {
    Write-Error "Arquivo de chave não foi criado!"
    exit 1
}

Write-Success "Chave JSON criada: $KEY_FILE"

# Ler conteúdo do arquivo JSON
Write-Log "Lendo conteúdo da chave JSON..."
$keyContent = Get-Content $KEY_FILE -Raw
if (-not $keyContent) {
    Write-Error "Não foi possível ler o conteúdo da chave JSON!"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ CONFIGURAÇÃO GCP CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Adicione o secret no GitHub:" -ForegroundColor Cyan
Write-Host "   - Acesse: https://github.com/LMONCAO/monpec/settings/secrets/actions" -ForegroundColor White
Write-Host "   - Clique em 'New repository secret'" -ForegroundColor White
Write-Host "   - Nome: GCP_SA_KEY" -ForegroundColor White
Write-Host "   - Valor: Cole o conteúdo completo do arquivo '$KEY_FILE'" -ForegroundColor White
Write-Host ""
Write-Host "2. O conteúdo da chave está salvo em: $KEY_FILE" -ForegroundColor Cyan
Write-Host ""

# Perguntar se quer exibir o conteúdo
$showContent = Read-Host "Deseja exibir o conteúdo da chave JSON agora? (S/N)"
if ($showContent -eq "S" -or $showContent -eq "s") {
    Write-Host ""
    Write-Host "=== CONTEÚDO DA CHAVE JSON ===" -ForegroundColor Yellow
    Write-Host $keyContent
    Write-Host "=== FIM DO CONTEÚDO ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Copie TODO o conteúdo acima e cole no GitHub como valor do secret 'GCP_SA_KEY'" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "3. Após adicionar o secret no GitHub, faça commit e push:" -ForegroundColor Cyan
Write-Host "   git add .github/" -ForegroundColor White
Write-Host "   git commit -m 'Adicionar GitHub Actions para deploy automático'" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor White
Write-Host ""

Write-Host "4. O deploy será executado automaticamente no GitHub Actions!" -ForegroundColor Cyan
Write-Host "   Acompanhe em: https://github.com/LMONCAO/monpec/actions" -ForegroundColor White
Write-Host ""

Write-Warning "⚠️  IMPORTANTE: Mantenha o arquivo '$KEY_FILE' seguro e não o commite no Git!"
Write-Host "   Já adicionado ao .gitignore para evitar commits acidentais." -ForegroundColor Gray
Write-Host ""

# Adicionar ao .gitignore se não estiver lá
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -notmatch "github-actions-key\.json") {
        Add-Content ".gitignore" "`n# GitHub Actions key`ngithub-actions-key.json"
        Write-Success "Arquivo .gitignore atualizado"
    }
} else {
    Set-Content ".gitignore" "# GitHub Actions key`ngithub-actions-key.json"
    Write-Success "Arquivo .gitignore criado"
}

Write-Host "✅ Script concluído!" -ForegroundColor Green
Write-Host ""

