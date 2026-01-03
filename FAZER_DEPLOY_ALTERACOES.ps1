# Script para fazer deploy das alterações de login automático demo
# Execute este script para fazer commit e push das alterações

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY ALTERAÇÕES - LOGIN AUTOMÁTICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "gestao_rural\views.py")) {
    Write-Host "ERRO: Execute este script do diretório raiz do projeto!" -ForegroundColor Red
    exit 1
}

# Verificar se Git está instalado
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Git não está instalado!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Git encontrado" -ForegroundColor Green
Write-Host ""

# Verificar status do repositório
Write-Host "Verificando status do repositório..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Problema ao verificar status do Git" -ForegroundColor Red
    exit 1
}

# Verificar se há remote configurado
Write-Host "Verificando repositório remoto..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠ ATENÇÃO: Nenhum repositório remoto configurado!" -ForegroundColor Yellow
    Write-Host ""
    $repoUrl = Read-Host "Digite a URL do repositório GitHub (ex: https://github.com/usuario/repo.git)"
    
    if ($repoUrl) {
        Write-Host "Configurando remote 'origin'..." -ForegroundColor Yellow
        git remote add origin $repoUrl
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Remote configurado" -ForegroundColor Green
        } else {
            Write-Host "ERRO: Não foi possível configurar o remote" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "ERRO: URL do repositório é obrigatória!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Remote encontrado: $remoteUrl" -ForegroundColor Green
}

Write-Host ""

# Verificar se há alterações para commitar
$modifiedFiles = @(
    "gestao_rural\views.py",
    "templates\site\landing_page.html"
)

$filesToAdd = @()
foreach ($file in $modifiedFiles) {
    if (Test-Path $file) {
        $filesToAdd += $file
    }
}

if ($filesToAdd.Count -eq 0) {
    Write-Host "ERRO: Arquivos modificados não encontrados!" -ForegroundColor Red
    exit 1
}

Write-Host "Arquivos que serão adicionados:" -ForegroundColor Yellow
foreach ($file in $filesToAdd) {
    Write-Host "  - $file" -ForegroundColor Cyan
}
Write-Host ""

# Perguntar confirmação
$confirm = Read-Host "Deseja continuar com o commit e push? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Adicionando arquivos ao Git..." -ForegroundColor Yellow
foreach ($file in $filesToAdd) {
    git add $file
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Erro ao adicionar $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Fazendo commit..." -ForegroundColor Yellow
$commitMessage = "Fix: Login automático após criar usuário demo - redireciona para demo_loading"

git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Commit realizado com sucesso" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao fazer commit" -ForegroundColor Red
    Write-Host "Tentando continuar mesmo assim..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificando branch atual..." -ForegroundColor Yellow
$currentBranch = git branch --show-current

if (-not $currentBranch) {
    # Se não há branch, criar master/main
    Write-Host "Criando branch master..." -ForegroundColor Yellow
    git checkout -b master
    $currentBranch = "master"
}

Write-Host "Branch atual: $currentBranch" -ForegroundColor Cyan
Write-Host ""

# Verificar se há upstream configurado
$upstream = git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>&1

Write-Host "Fazendo push para o repositório remoto..." -ForegroundColor Yellow

if ($LASTEXITCODE -eq 0 -and $upstream) {
    Write-Host "Usando upstream: $upstream" -ForegroundColor Cyan
    git push
} else {
    Write-Host "Configurando upstream e fazendo push..." -ForegroundColor Yellow
    git push -u origin $currentBranch
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ DEPLOY INICIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "O GitHub Actions irá fazer o deploy automaticamente." -ForegroundColor Cyan
    Write-Host "Acompanhe o progresso em:" -ForegroundColor Cyan
    Write-Host "https://github.com/[usuario]/[repo]/actions" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alterações realizadas:" -ForegroundColor Cyan
    Write-Host "  - Login automático após criar usuário demo" -ForegroundColor White
    Write-Host "  - Redirecionamento direto para demo_loading" -ForegroundColor White
    Write-Host "  - Adicionado credentials: 'same-origin' no fetch" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERRO: Falha ao fazer push" -ForegroundColor Red
    Write-Host "Verifique se você tem permissões no repositório remoto." -ForegroundColor Yellow
    exit 1
}

