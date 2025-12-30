# 🔐 VERIFICAR CONFIGURAÇÃO DO SECRET NO GITHUB
# Este script ajuda a verificar se o secret GCP_SA_KEY está configurado

Write-Host "🔐 VERIFICAÇÃO DO SECRET - GITHUB ACTIONS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$REPO_OWNER = "LMONCAO"
$REPO_NAME = "Monpec_GestaoRural"
$SECRET_NAME = "GCP_SA_KEY"

# Cores
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }

# 1. Verificar GitHub CLI
Write-Info "1/4 - Verificando GitHub CLI..."
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Success "GitHub CLI instalado"
} else {
    Write-Warning "GitHub CLI não encontrado"
    Write-Info "   Instale com: winget install GitHub.cli"
    Write-Host ""
    Write-Info "   OU verifique manualmente em:"
    Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# 2. Verificar autenticação
Write-Info "2/4 - Verificando autenticação..."
try {
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Autenticado no GitHub"
    } else {
        Write-Error "Não autenticado"
        Write-Info "   Execute: gh auth login"
        Write-Host ""
        exit 1
    }
} catch {
    Write-Error "Erro ao verificar autenticação"
    Write-Host ""
    exit 1
}

Write-Host ""

# 3. Tentar listar secrets (pode não funcionar se não tiver permissão)
Write-Info "3/4 - Verificando secrets configurados..."
Write-Warning "   Nota: GitHub não permite listar valores de secrets, apenas nomes"
Write-Host ""

try {
    # Tentar verificar via API (requer token com permissão)
    $secrets = gh secret list --repo "$REPO_OWNER/$REPO_NAME" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $secrets
        Write-Host ""
        
        if ($secrets -match $SECRET_NAME) {
            Write-Success "Secret '$SECRET_NAME' encontrado!"
        } else {
            Write-Error "Secret '$SECRET_NAME' NÃO encontrado!"
            Write-Host ""
            Write-Info "📝 Como configurar:"
            Write-Host "   1. Acesse: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
            Write-Host "   2. Clique em 'New repository secret'"
            Write-Host "   3. Name: $SECRET_NAME"
            Write-Host "   4. Value: Cole o conteúdo completo do arquivo JSON da Service Account"
            Write-Host "   5. Clique em 'Add secret'"
        }
    } else {
        Write-Warning "Não foi possível listar secrets automaticamente"
        Write-Info "   Verifique manualmente em:"
        Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "Erro ao verificar secrets"
    Write-Info "   Verifique manualmente em:"
    Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Yellow
}

Write-Host ""

# 4. Verificar se há arquivo de chave local
Write-Info "4/4 - Verificando arquivos de chave local..."
$keyFiles = @(
    "github-actions-deploy-key.json",
    "gcp-service-account-key.json",
    "*.json"
)

$foundKey = $false
foreach ($pattern in $keyFiles) {
    $files = Get-ChildItem -Path . -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        foreach ($file in $files) {
            if ($file.Name -notmatch "package|node_modules") {
                Write-Warning "Arquivo de chave encontrado: $($file.Name)"
                Write-Info "   ⚠️  ATENÇÃO: Não faça commit deste arquivo!"
                $foundKey = $true
            }
        }
    }
}

if (-not $foundKey) {
    Write-Info "Nenhum arquivo de chave JSON encontrado localmente"
    Write-Info "   Isso é normal se você já configurou o secret no GitHub"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Link direto para secrets:" -ForegroundColor Yellow
Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ O secret deve se chamar exatamente: $SECRET_NAME" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Se o secret não estiver configurado:" -ForegroundColor Yellow
Write-Host "   1. Crie a Service Account no GCP (veja CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1)"
Write-Host "   2. Baixe a chave JSON"
Write-Host "   3. Adicione como secret no GitHub com o nome: $SECRET_NAME"
Write-Host ""








