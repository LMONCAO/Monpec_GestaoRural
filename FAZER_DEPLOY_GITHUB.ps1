# 🚀 SCRIPT PARA FAZER DEPLOY VIA GITHUB ACTIONS
# Este script automatiza o processo de deploy usando GitHub Actions

Write-Host "🚀 DEPLOY VIA GITHUB ACTIONS" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Cores
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }
function Write-Step { param($msg) Write-Host "📌 $msg" -ForegroundColor Magenta }

$REPO_OWNER = "LMONCAO"
$REPO_NAME = "Monpec_GestaoRural"
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

# ============================================
# PASSO 1: Verificar se é repositório Git
# ============================================
Write-Step "1/6 - Verificando repositório Git..."

if (-not (Test-Path ".git")) {
    Write-Warning "Repositório Git não inicializado"
    Write-Info "Inicializando repositório Git..."
    
    $initRepo = Read-Host "Deseja inicializar o repositório Git agora? (S/N)"
    if ($initRepo -eq "S" -or $initRepo -eq "s") {
        git init
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Erro ao inicializar repositório Git"
            exit 1
        }
        Write-Success "Repositório Git inicializado"
        
        $remoteUrl = Read-Host "Digite a URL do repositório GitHub (ex: https://github.com/LMONCAO/Monpec_GestaoRural.git)"
        if ($remoteUrl) {
            git remote add origin $remoteUrl
            Write-Success "Remote adicionado: $remoteUrl"
        }
    } else {
        Write-Error "É necessário ter um repositório Git configurado"
        exit 1
    }
} else {
    Write-Success "Repositório Git encontrado"
    
    # Verificar remote
    $remote = git remote get-url origin 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Remote: $remote"
    } else {
        Write-Warning "Remote não configurado"
        $remoteUrl = Read-Host "Digite a URL do repositório GitHub"
        if ($remoteUrl) {
            git remote add origin $remoteUrl
            Write-Success "Remote adicionado"
        }
    }
}

Write-Host ""

# ============================================
# PASSO 2: Verificar arquivos necessários
# ============================================
Write-Step "2/6 - Verificando arquivos necessários..."

$requiredFiles = @(
    ".github/workflows/deploy-gcp.yml",
    "Dockerfile.prod"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "Arquivo encontrado: $file"
    } else {
        Write-Error "Arquivo não encontrado: $file"
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Error "Alguns arquivos necessários estão faltando. Verifique e tente novamente."
    exit 1
}

Write-Host ""

# ============================================
# PASSO 3: Verificar Service Account
# ============================================
Write-Step "3/6 - Verificando Service Account no GCP..."

if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    $saExists = gcloud iam service-accounts describe "github-actions-deploy@$PROJECT_ID.iam.gserviceaccount.com" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Service Account encontrada"
    } else {
        Write-Warning "Service Account não encontrada"
        Write-Info "Execute: .\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1"
        Write-Host ""
        $continue = Read-Host "Deseja continuar mesmo assim? (S/N)"
        if ($continue -ne "S" -and $continue -ne "s") {
            exit 1
        }
    }
} else {
    Write-Warning "gcloud CLI não encontrado. Pule esta verificação."
}

Write-Host ""

# ============================================
# PASSO 4: Verificar Secret no GitHub
# ============================================
Write-Step "4/6 - Verificando Secret no GitHub..."

if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        $secrets = gh secret list --repo "$REPO_OWNER/$REPO_NAME" 2>&1
        if ($LASTEXITCODE -eq 0 -and $secrets -match "GCP_SA_KEY") {
            Write-Success "Secret 'GCP_SA_KEY' encontrado no GitHub"
        } else {
            Write-Warning "Secret 'GCP_SA_KEY' não encontrado"
            Write-Info "Configure em: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
            Write-Host ""
            
            # Verificar se há arquivo de chave local
            if (Test-Path "github-actions-deploy-key.json") {
                Write-Info "Arquivo de chave encontrado localmente"
                $addSecret = Read-Host "Deseja adicionar o secret agora? (S/N)"
                if ($addSecret -eq "S" -or $addSecret -eq "s") {
                    $keyContent = Get-Content "github-actions-deploy-key.json" -Raw
                    gh secret set GCP_SA_KEY --repo "$REPO_OWNER/$REPO_NAME" --body $keyContent
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Secret adicionado com sucesso!"
                    } else {
                        Write-Error "Erro ao adicionar secret"
                    }
                }
            }
            
            $continue = Read-Host "Deseja continuar mesmo assim? (S/N)"
            if ($continue -ne "S" -and $continue -ne "s") {
                exit 1
            }
        }
    } else {
        Write-Warning "GitHub CLI não autenticado"
        Write-Info "Execute: gh auth login"
        Write-Host ""
        Write-Info "Ou configure manualmente em: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
    }
} else {
    Write-Warning "GitHub CLI não encontrado"
    Write-Info "Verifique manualmente em: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
}

Write-Host ""

# ============================================
# PASSO 5: Preparar commit
# ============================================
Write-Step "5/6 - Preparando commit..."

# Verificar status
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Info "Arquivos modificados detectados:"
    Write-Host $gitStatus -ForegroundColor Gray
    Write-Host ""
    
    $addFiles = Read-Host "Deseja adicionar todos os arquivos? (S/N)"
    if ($addFiles -eq "S" -or $addFiles -eq "s") {
        git add .
        Write-Success "Arquivos adicionados"
    } else {
        Write-Info "Adicione os arquivos manualmente com: git add <arquivo>"
    }
    
    $commitMessage = Read-Host "Digite a mensagem do commit (ou pressione Enter para usar padrão)"
    if (-not $commitMessage) {
        $commitMessage = "Deploy automático via GitHub Actions"
    }
    
    git commit -m $commitMessage
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Commit criado com sucesso"
    } else {
        Write-Warning "Nenhum commit necessário ou erro ao criar commit"
    }
} else {
    Write-Info "Nenhuma alteração para commitar"
}

Write-Host ""

# ============================================
# PASSO 6: Fazer push e disparar deploy
# ============================================
Write-Step "6/6 - Fazendo push para GitHub..."

# Verificar branch atual
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    Write-Info "Criando branch 'main'..."
    git checkout -b main
    $currentBranch = "main"
}

Write-Info "Branch atual: $currentBranch"

# Verificar se precisa fazer push
$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse "origin/$currentBranch" 2>&1

if ($LASTEXITCODE -ne 0 -or $localCommit -ne $remoteCommit) {
    Write-Info "Fazendo push para origin/$currentBranch..."
    
    $doPush = Read-Host "Deseja fazer push agora? (S/N)"
    if ($doPush -eq "S" -or $doPush -eq "s") {
        git push -u origin $currentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Push realizado com sucesso!"
            Write-Host ""
            Write-Success "🚀 Deploy iniciado automaticamente!"
            Write-Info "Acompanhe o progresso em:"
            Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Cyan
        } else {
            Write-Error "Erro ao fazer push"
            Write-Info "Verifique suas credenciais Git e tente novamente"
        }
    } else {
        Write-Info "Push cancelado. Execute manualmente:"
        Write-Host "   git push -u origin $currentBranch" -ForegroundColor Yellow
    }
} else {
    Write-Info "Repositório já está atualizado"
    Write-Info "Para disparar deploy manualmente, acesse:"
    Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Ou faça uma pequena alteração e faça push novamente"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "   - GitHub Actions: https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Cyan
Write-Host "   - GitHub Secrets: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "   - Cloud Run: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Success "✅ Processo concluído!"

