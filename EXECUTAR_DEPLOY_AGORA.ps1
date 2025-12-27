# 🚀 EXECUTAR DEPLOY AGORA
# Script simplificado para fazer deploy via GitHub

Write-Host "🚀 DEPLOY VIA GITHUB ACTIONS" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório do projeto
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath
Write-Host "📁 Diretório: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Verificar se é repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "⚠️  Repositório Git não encontrado. Inicializando..." -ForegroundColor Yellow
    git init
    Write-Host ""
}

# Verificar remote
$remote = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Remote não configurado." -ForegroundColor Yellow
    Write-Host "Configure com: git remote add origin https://github.com/LMONCAO/Monpec_GestaoRural.git" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✅ Remote configurado: $remote" -ForegroundColor Green
    Write-Host ""
}

# Verificar arquivos necessários
Write-Host "📋 Verificando arquivos necessários..." -ForegroundColor Cyan
$files = @(
    ".github\workflows\deploy-gcp.yml",
    "Dockerfile.prod"
)

$allOk = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (não encontrado)" -ForegroundColor Red
        $allOk = $false
    }
}
Write-Host ""

if (-not $allOk) {
    Write-Host "❌ Alguns arquivos estão faltando. Verifique e tente novamente." -ForegroundColor Red
    exit 1
}

# Verificar status do Git
Write-Host "📊 Status do repositório:" -ForegroundColor Cyan
git status --short
Write-Host ""

# Adicionar arquivos
$addFiles = Read-Host "Deseja adicionar todos os arquivos modificados? (S/N)"
if ($addFiles -eq "S" -or $addFiles -eq "s") {
    git add .
    Write-Host "✅ Arquivos adicionados" -ForegroundColor Green
    Write-Host ""
}

# Fazer commit
$hasChanges = git diff --cached --quiet
if (-not $hasChanges) {
    $commitMsg = Read-Host "Digite a mensagem do commit (ou Enter para padrão)"
    if (-not $commitMsg) {
        $commitMsg = "Deploy automático via GitHub Actions - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    
    git commit -m $commitMsg
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Commit criado" -ForegroundColor Green
        Write-Host ""
    }
}

# Verificar branch
$branch = git branch --show-current
if (-not $branch) {
    Write-Host "📌 Criando branch 'main'..." -ForegroundColor Yellow
    git checkout -b main
    $branch = "main"
}

Write-Host "🌿 Branch atual: $branch" -ForegroundColor Cyan
Write-Host ""

# Fazer push
$doPush = Read-Host "Deseja fazer push para GitHub agora? (S/N)"
if ($doPush -eq "S" -or $doPush -eq "s") {
    Write-Host "📤 Fazendo push para origin/$branch..." -ForegroundColor Cyan
    
    # Tentar push
    git push -u origin $branch 2>&1 | ForEach-Object {
        if ($_ -match "error|fatal") {
            Write-Host $_ -ForegroundColor Red
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Deploy iniciado automaticamente!" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📊 Acompanhe o progresso:" -ForegroundColor Yellow
        Write-Host "   https://github.com/LMONCAO/Monpec_GestaoRural/actions" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Possíveis soluções:" -ForegroundColor Yellow
        Write-Host "   1. Verifique se o remote está configurado corretamente" -ForegroundColor Gray
        Write-Host "   2. Verifique suas credenciais Git" -ForegroundColor Gray
        Write-Host "   3. Execute manualmente: git push -u origin $branch" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "ℹ️  Push cancelado. Execute manualmente quando estiver pronto:" -ForegroundColor Yellow
    Write-Host "   git push -u origin $branch" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔗 Links úteis:" -ForegroundColor Yellow
Write-Host "   - GitHub Actions: https://github.com/LMONCAO/Monpec_GestaoRural/actions" -ForegroundColor Cyan
Write-Host "   - GitHub Secrets: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "   - Cloud Run: https://console.cloud.google.com/run/detail/us-central1/monpec" -ForegroundColor Cyan
Write-Host ""
