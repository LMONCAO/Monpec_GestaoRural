# 🔧 CONFIGURAR SERVICE ACCOUNT NO GOOGLE CLOUD
# Este script ajuda a criar e configurar a Service Account para GitHub Actions

Write-Host "🔧 CONFIGURAÇÃO DE SERVICE ACCOUNT - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SA_NAME = "github-actions-deploy"
$SA_DISPLAY_NAME = "GitHub Actions Deploy"
$KEY_FILE = "github-actions-deploy-key.json"

# Cores
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }
function Write-Step { param($msg) Write-Host "📌 $msg" -ForegroundColor Magenta }

# 1. Verificar gcloud CLI
Write-Info "1/7 - Verificando Google Cloud CLI..."
if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    $gcloudVersion = gcloud --version | Select-Object -First 1
    Write-Success "Google Cloud CLI instalado: $gcloudVersion"
} else {
    Write-Error "Google Cloud CLI não encontrado!"
    Write-Info "   Instale em: https://cloud.google.com/sdk/docs/install"
    Write-Host ""
    exit 1
}

Write-Host ""

# 2. Verificar autenticação
Write-Info "2/7 - Verificando autenticação..."
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($currentAccount) {
    Write-Success "Autenticado como: $currentAccount"
} else {
    Write-Warning "Não autenticado. Iniciando login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
}

Write-Host ""

# 3. Configurar projeto
Write-Info "3/7 - Configurando projeto..."
$currentProject = gcloud config get-value project 2>&1
if ($currentProject -ne $PROJECT_ID) {
    Write-Warning "Projeto atual: $currentProject"
    Write-Step "Configurando projeto para: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao configurar projeto!"
        Write-Info "   Verifique se o projeto existe e você tem acesso"
        exit 1
    }
    Write-Success "Projeto configurado!"
} else {
    Write-Success "Projeto já configurado: $PROJECT_ID"
}

Write-Host ""

# 4. Verificar se Service Account já existe
Write-Info "4/7 - Verificando Service Account existente..."
$existingSA = gcloud iam service-accounts describe "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Service Account já existe: $SA_NAME"
    Write-Info "   Email: $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    $createNew = Read-Host "   Deseja criar uma nova chave? (S/N)"
    if ($createNew -ne "S" -and $createNew -ne "s") {
        Write-Info "Pulando criação da Service Account..."
        $skipCreate = $true
    }
} else {
    Write-Info "Service Account não existe. Será criada..."
    $skipCreate = $false
}

Write-Host ""

# 5. Criar Service Account (se necessário)
if (-not $skipCreate) {
    Write-Info "5/7 - Criando Service Account..."
    gcloud iam service-accounts create $SA_NAME `
        --display-name=$SA_DISPLAY_NAME `
        --description="Service account para deploy automático via GitHub Actions" `
        --project=$PROJECT_ID 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Service Account criada com sucesso!"
    } else {
        if ($existingSA) {
            Write-Info "Service Account já existe (erro esperado)"
        } else {
            Write-Error "Falha ao criar Service Account!"
            exit 1
        }
    }
} else {
    Write-Info "5/7 - Pulando criação (já existe)"
}

Write-Host ""

# 6. Atribuir permissões
Write-Info "6/7 - Atribuindo permissões..."
$roles = @(
    "roles/run.admin",                    # Cloud Run Admin
    "roles/iam.serviceAccountUser",       # Service Account User
    "roles/cloudbuild.builds.editor",     # Cloud Build Editor
    "roles/storage.admin",                # Storage Admin
    "roles/cloudsql.client",              # Cloud SQL Client
    "roles/serviceusage.serviceUsageAdmin" # Service Usage Admin (para habilitar APIs se necessário)
)

$saEmail = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

foreach ($role in $roles) {
    Write-Step "Atribuindo role: $role"
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$saEmail" `
        --role=$role `
        --condition=None 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Permissão atribuída: $role"
    } else {
        Write-Warning "Aviso ao atribuir: $role (pode já estar atribuída)"
    }
}

Write-Host ""

# 7. Criar chave JSON
Write-Info "7/7 - Criando chave JSON..."
if (Test-Path $KEY_FILE) {
    $overwrite = Read-Host "Arquivo $KEY_FILE já existe. Sobrescrever? (S/N)"
    if ($overwrite -ne "S" -and $overwrite -ne "s") {
        Write-Info "Mantendo arquivo existente"
        Write-Host ""
        Write-Success "✅ Configuração concluída!"
        Write-Host ""
        Write-Info "📄 Arquivo de chave: $KEY_FILE"
        Write-Host ""
        exit 0
    }
}

Write-Step "Gerando chave JSON..."
gcloud iam service-accounts keys create $KEY_FILE `
    --iam-account=$saEmail `
    --project=$PROJECT_ID 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "Chave JSON criada: $KEY_FILE"
    
    # Adicionar ao .gitignore
    if (Test-Path ".gitignore") {
        $gitignoreContent = Get-Content ".gitignore" -Raw
        if ($gitignoreContent -notmatch $KEY_FILE) {
            Add-Content ".gitignore" "`n# GitHub Actions Service Account Key`n$KEY_FILE"
            Write-Success "Arquivo adicionado ao .gitignore"
        }
    }
} else {
    Write-Error "Falha ao criar chave JSON!"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📄 Arquivo de chave criado: $KEY_FILE" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 PRÓXIMO PASSO - Configurar Secret no GitHub:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Abra o arquivo: $KEY_FILE" -ForegroundColor White
Write-Host "   2. Copie TODO o conteúdo (desde { até })" -ForegroundColor White
Write-Host "   3. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "   4. Clique em 'New repository secret'" -ForegroundColor White
Write-Host "   5. Name: GCP_SA_KEY" -ForegroundColor White
Write-Host "   6. Secret: Cole o conteúdo do JSON" -ForegroundColor White
Write-Host "   7. Clique em 'Add secret'" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Red
Write-Host "   - NÃO faça commit do arquivo $KEY_FILE" -ForegroundColor Yellow
Write-Host "   - Mantenha o arquivo em local seguro" -ForegroundColor Yellow
Write-Host "   - O arquivo já foi adicionado ao .gitignore" -ForegroundColor Green
Write-Host ""

