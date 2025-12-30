# 🔍 VERIFICAR STATUS DO DEPLOY - GITHUB ACTIONS
# Este script verifica o status do deploy no GitHub Actions

Write-Host "🔍 VERIFICAÇÃO DO STATUS - GITHUB ACTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$REPO_OWNER = "LMONCAO"
$REPO_NAME = "Monpec_GestaoRural"
$GITHUB_API = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME"

# Cores
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }

# 1. Verificar se gh CLI está instalado
Write-Info "1/5 - Verificando GitHub CLI..."
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghVersion = gh --version | Select-Object -First 1
    Write-Success "GitHub CLI instalado: $ghVersion"
} else {
    Write-Warning "GitHub CLI não encontrado. Instalando informações básicas..."
    Write-Info "   Para instalar: winget install GitHub.cli"
}

Write-Host ""

# 2. Verificar autenticação GitHub
Write-Info "2/5 - Verificando autenticação GitHub..."
try {
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Autenticado no GitHub"
    } else {
        Write-Warning "Não autenticado. Execute: gh auth login"
    }
} catch {
    Write-Warning "Não foi possível verificar autenticação"
}

Write-Host ""

# 3. Verificar workflows recentes
Write-Info "3/5 - Verificando workflows recentes..."
Write-Host "   Acesse: https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Cyan
Write-Host ""

try {
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        Write-Info "Buscando últimas execuções de workflow..."
        $workflows = gh run list --repo "$REPO_OWNER/$REPO_NAME" --limit 5 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host $workflows
        } else {
            Write-Warning "Não foi possível listar workflows. Verifique manualmente no GitHub."
        }
    } else {
        Write-Info "Abra no navegador para ver os workflows:"
        Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "Erro ao verificar workflows"
}

Write-Host ""

# 4. Verificar se os workflows estão configurados
Write-Info "4/5 - Verificando arquivos de workflow..."
$workflowFiles = @(
    ".github/workflows/deploy-gcp.yml",
    ".github/workflows/deploy-gcp-simple.yml"
)

foreach ($file in $workflowFiles) {
    if (Test-Path $file) {
        Write-Success "Encontrado: $file"
    } else {
        Write-Error "Não encontrado: $file"
    }
}

Write-Host ""

# 5. Verificar Dockerfile
Write-Info "5/5 - Verificando Dockerfile de produção..."
if (Test-Path "Dockerfile.prod") {
    Write-Success "Dockerfile.prod encontrado"
} else {
    Write-Error "Dockerfile.prod não encontrado!"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "   - Actions: https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Cyan
Write-Host "   - Secrets: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "   - Workflows: https://github.com/$REPO_OWNER/$REPO_NAME/tree/master/.github/workflows" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Verifique se o secret GCP_SA_KEY está configurado"
Write-Host "   2. Acesse a aba Actions no GitHub para ver execuções"
Write-Host "   3. Se houver erros, verifique os logs do workflow"
Write-Host ""








