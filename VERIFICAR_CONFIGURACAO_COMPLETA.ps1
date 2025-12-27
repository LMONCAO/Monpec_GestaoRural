# 🔍 VERIFICAÇÃO COMPLETA DA CONFIGURAÇÃO
# Este script verifica TODA a configuração do deploy automático

Write-Host "🔍 VERIFICAÇÃO COMPLETA - DEPLOY AUTOMÁTICO" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Cores
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERRO] $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "[i] $msg" -ForegroundColor Blue }
function Write-Step { param($msg) Write-Host "[*] $msg" -ForegroundColor Magenta }

$allChecks = @()
$passedChecks = 0
$totalChecks = 0

function Add-Check {
    param($name, $status, $message)
    $totalChecks++
    if ($status) {
        $passedChecks++
        Write-Success "[$totalChecks] $name"
        if ($message) { Write-Host "      $message" -ForegroundColor Gray }
    } else {
        Write-Error "[$totalChecks] $name"
        if ($message) { Write-Host "      $message" -ForegroundColor Yellow }
    }
    $script:allChecks += [PSCustomObject]@{Name=$name; Status=$status; Message=$message}
}

Write-Host "📋 VERIFICAÇÕES LOCAIS" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Yellow
Write-Host ""

# 1. Verificar arquivos de workflow
Add-Check "Arquivo .github/workflows/deploy-gcp.yml existe" `
    (Test-Path ".github/workflows/deploy-gcp.yml") `
    "Workflow principal do GitHub Actions"

Add-Check "Arquivo .github/workflows/deploy-gcp-simple.yml existe" `
    (Test-Path ".github/workflows/deploy-gcp-simple.yml") `
    "Workflow simplificado (alternativo)"

# 2. Verificar Dockerfile
Add-Check "Dockerfile.prod existe" `
    (Test-Path "Dockerfile.prod") `
    "Arquivo necessário para build da imagem"

# 3. Verificar Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitRemote = git remote get-url origin 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Check "Repositório Git configurado" $true "Remote: $gitRemote"
    } else {
        Add-Check "Repositório Git configurado" $false "Execute: git remote add origin <url>"
    }
} else {
    Add-Check "Git instalado" $false "Instale o Git"
}

Write-Host ""
Write-Host "📋 VERIFICAÇÕES DE FERRAMENTAS" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow
Write-Host ""

# 4. Verificar GitHub CLI
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghAuth = gh auth status 2>&1
    $isAuthenticated = $LASTEXITCODE -eq 0
    Add-Check "GitHub CLI instalado e autenticado" $isAuthenticated `
        $(if ($isAuthenticated) { "Pronto para usar" } else { "Execute: gh auth login" })
} else {
    Add-Check "GitHub CLI instalado" $false "Instale com: winget install GitHub.cli"
}

# 5. Verificar Google Cloud CLI
if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    $gcloudProject = gcloud config get-value project 2>&1
    $hasProject = $LASTEXITCODE -eq 0 -and $gcloudProject
    Add-Check "Google Cloud CLI instalado e configurado" $hasProject `
        $(if ($hasProject) { "Projeto: $gcloudProject" } else { "Execute: gcloud config set project monpec-sistema-rural" })
} else {
    Add-Check "Google Cloud CLI instalado" $false "Instale em: https://cloud.google.com/sdk/docs/install"
}

Write-Host ""
Write-Host "📋 VERIFICAÇÕES DO GOOGLE CLOUD" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow
Write-Host ""

# 6. Verificar Service Account no GCP
if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    $saExists = gcloud iam service-accounts describe "github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" 2>&1
    Add-Check "Service Account 'github-actions-deploy' existe no GCP" `
        ($LASTEXITCODE -eq 0) `
        $(if ($LASTEXITCODE -ne 0) { "Execute: .\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1" } else { "Service Account configurada" })
} else {
    Add-Check "Service Account configurada" $false "Instale gcloud CLI primeiro"
}

# 7. Verificar arquivo de chave local
$keyFile = "github-actions-deploy-key.json"
$hasKeyFile = Test-Path $keyFile
Add-Check "Arquivo de chave JSON local existe" $hasKeyFile `
    $(if ($hasKeyFile) { "Arquivo: $keyFile" } else { "Será criado ao configurar Service Account" })

Write-Host ""
Write-Host "📋 VERIFICAÇÕES DO GITHUB" -ForegroundColor Yellow
Write-Host "-----------------------" -ForegroundColor Yellow
Write-Host ""

# 8. Verificar secret no GitHub (tentativa)
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        $secrets = gh secret list --repo "LMONCAO/Monpec_GestaoRural" 2>&1
        if ($LASTEXITCODE -eq 0 -and $secrets -match "GCP_SA_KEY") {
            Add-Check "Secret 'GCP_SA_KEY' configurado no GitHub" $true "Secret encontrado"
        } else {
            Add-Check "Secret 'GCP_SA_KEY' configurado no GitHub" $false `
                "Configure em: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions"
        }
    } else {
        Add-Check "Secret 'GCP_SA_KEY' configurado no GitHub" $false `
            "Autentique-se primeiro: gh auth login"
    }
} else {
    Add-Check "Secret 'GCP_SA_KEY' configurado no GitHub" $false `
        "Instale GitHub CLI ou verifique manualmente"
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$percentage = [math]::Round(($passedChecks / $totalChecks) * 100, 1)
Write-Host "✅ Verificações aprovadas: $passedChecks / $totalChecks ($percentage%)" -ForegroundColor $(if ($percentage -eq 100) { "Green" } elseif ($percentage -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($percentage -eq 100) {
    Write-Success "🎉 TUDO CONFIGURADO! Seu deploy automático está pronto!"
    Write-Host ""
    Write-Info "Próximos passos:"
    Write-Host "   1. Faça push para master/main: git push origin master"
    Write-Host "   2. Acompanhe o deploy: https://github.com/LMONCAO/Monpec_GestaoRural/actions"
    Write-Host ""
} elseif ($percentage -ge 70) {
    Write-Warning "⚠️  Quase lá! Algumas configurações estão faltando."
    Write-Host ""
    Write-Info "Verifique os itens marcados com ❌ acima"
    Write-Host ""
} else {
    Write-Error "❌ Várias configurações estão faltando."
    Write-Host ""
    Write-Info "Execute os scripts de configuração:"
    Write-Host "   1. .\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1"
    Write-Host "   2. .\VERIFICAR_SECRET_GITHUB.ps1"
    Write-Host ""
}

Write-Host "🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "   - GitHub Actions: https://github.com/LMONCAO/Monpec_GestaoRural/actions" -ForegroundColor Cyan
Write-Host "   - GitHub Secrets: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "   - Google Cloud Console: https://console.cloud.google.com/run" -ForegroundColor Cyan
Write-Host ""

