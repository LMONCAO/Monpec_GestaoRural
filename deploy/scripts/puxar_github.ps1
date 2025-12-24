# ========================================
# PUXAR ARQUIVOS DO GITHUB
# ========================================

Write-Host "PUXANDO ARQUIVOS DO GITHUB" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Yellow
Write-Host ""

# Procurar Git em locais comuns
$gitPath = $null
$possiblePaths = @(
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe",
    "$env:ProgramFiles (x86)\Git\cmd\git.exe",
    "$env:ProgramFiles (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
)

# Procurar Git do GitHub Desktop
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
    Write-Host "Git do GitHub Desktop encontrado!" -ForegroundColor Green
}

# Procurar nos caminhos padrao
if (-not $gitPath) {
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $gitPath = $path
            Write-Host "Git encontrado em: $gitPath" -ForegroundColor Green
            break
        }
    }
}

# Tentar encontrar git no PATH
if (-not $gitPath) {
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
        Write-Host "Git encontrado no PATH: $gitPath" -ForegroundColor Green
    } catch {
        Write-Host "ERRO: Git nao encontrado!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Por favor, instale o Git:" -ForegroundColor Yellow
        Write-Host "1. Download: https://git-scm.com/download/win" -ForegroundColor Cyan
        Write-Host "2. Ou use GitHub Desktop: https://desktop.github.com/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Ou use o GitHub Desktop para fazer pull manualmente." -ForegroundColor Yellow
        exit 1
    }
}

# Verificar se estamos em um repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "AVISO: Este diretorio nao e um repositorio Git" -ForegroundColor Yellow
    Write-Host "   Diretorio atual: $(Get-Location)" -ForegroundColor Gray
    exit 1
}

# Configurar estrategia de merge (merge strategy)
Write-Host ""
Write-Host "Configurando estrategia de merge..." -ForegroundColor Cyan
& $gitPath config pull.rebase false

# Verificar status atual
Write-Host ""
Write-Host "Verificando status do repositorio..." -ForegroundColor Cyan
& $gitPath status --short

# Verificar branch atual
Write-Host ""
Write-Host "Detectando branch atual..." -ForegroundColor Cyan
$currentBranch = & $gitPath branch --show-current
if (-not $currentBranch) {
    $branchOutput = & $gitPath branch
    $currentBranch = ($branchOutput | Where-Object { $_ -match '^\*' } | ForEach-Object { $_ -replace '^\*\s+', '' }).Trim()
}

if (-not $currentBranch) {
    $currentBranch = "master"
    Write-Host "Usando branch: $currentBranch" -ForegroundColor Yellow
} else {
    Write-Host "Branch atual: $currentBranch" -ForegroundColor Green
}

# Fazer fetch
Write-Host ""
Write-Host "Buscando atualizacoes do GitHub..." -ForegroundColor Cyan
& $gitPath fetch origin

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao buscar atualizacoes!" -ForegroundColor Red
    exit 1
}

# Verificar se ha atualizacoes
Write-Host ""
Write-Host "Verificando se ha atualizacoes disponiveis..." -ForegroundColor Cyan
$localCommit = & $gitPath rev-parse HEAD
$remoteCommit = & $gitPath rev-parse origin/$currentBranch 2>&1

if ($remoteCommit -match "fatal") {
    Write-Host "AVISO: Branch remoto nao encontrado. Tentando 'main'..." -ForegroundColor Yellow
    $remoteCommit = & $gitPath rev-parse origin/main 2>&1
    if (-not ($remoteCommit -match "fatal")) {
        $currentBranch = "main"
    }
}

if ($localCommit -eq $remoteCommit) {
    Write-Host "Nenhuma atualizacao disponivel. Repositorio ja esta atualizado!" -ForegroundColor Green
    exit 0
}

# Fazer pull com merge
Write-Host ""
Write-Host "Puxando atualizacoes do GitHub..." -ForegroundColor Cyan
Write-Host "Branch: $currentBranch" -ForegroundColor Gray
Write-Host "Estrategia: merge (padrao)" -ForegroundColor Gray
Write-Host ""

& $gitPath pull origin $currentBranch --no-rebase

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "AVISO: Pode haver conflitos ou mudancas locais nao commitadas." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Status atual:" -ForegroundColor Cyan
    & $gitPath status
    Write-Host ""
    Write-Host "Se houver conflitos, resolva-os manualmente e depois faca commit." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "ARQUIVOS PUXADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Status atual do repositorio:" -ForegroundColor Cyan
& $gitPath status --short
Write-Host ""
