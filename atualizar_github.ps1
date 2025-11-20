# Script para atualizar o repositório no GitHub
# Repositório: https://github.com/LMONCAO/Monpec_GestaoRural

Write-Host "=== Atualizando repositório no GitHub ===" -ForegroundColor Cyan

# Verificar se Git está disponível
$gitPath = $null
$possiblePaths = @(
    "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles\GitHub Desktop\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles (x86)\GitHub Desktop\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe",
    "$env:ProgramFiles (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
)

# Procurar Git do GitHub Desktop (pode ter versão no caminho)
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
    Write-Host "Git do GitHub Desktop encontrado!" -ForegroundColor Green
}

# Procurar nos caminhos padrão
if (-not $gitPath) {
    foreach ($path in $possiblePaths) {
        $expandedPaths = @()
        if ($path -like "*`**") {
            # Expandir wildcards
            $expandedPaths = Get-ChildItem (Split-Path $path -Parent) -ErrorAction SilentlyContinue | Where-Object { $_.FullName -like $path } | Select-Object -ExpandProperty FullName
        } else {
            $expandedPaths = @($path)
        }
        
        foreach ($expandedPath in $expandedPaths) {
            if (Test-Path $expandedPath) {
                $gitPath = $expandedPath
                break
            }
        }
        if ($gitPath) { break }
    }
}

# Tentar encontrar git no PATH
if (-not $gitPath) {
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
    } catch {
        Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
        Write-Host "Por favor, instale o Git ou adicione-o ao PATH." -ForegroundColor Yellow
        Write-Host "Download: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Git encontrado em: $gitPath" -ForegroundColor Green

# Função para executar comandos Git
function Invoke-Git {
    param([string[]]$Arguments, [switch]$NoExit)
    $output = & $gitPath $Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($exitCode -ne 0 -and -not $NoExit) {
        Write-Host "ERRO ao executar: git $($Arguments -join ' ')" -ForegroundColor Red
        exit 1
    }
    return $output
}

# Verificar se estamos em um repositório Git
Write-Host "`nVerificando se é um repositório Git..." -ForegroundColor Cyan
$isGitRepo = Test-Path ".git"
if (-not $isGitRepo) {
    Write-Host "ERRO: Este diretório não é um repositório Git!" -ForegroundColor Red
    Write-Host "Execute 'git init' primeiro ou navegue até um repositório Git." -ForegroundColor Yellow
    exit 1
}

# Verificar status
Write-Host "`nVerificando status do repositório..." -ForegroundColor Cyan
Invoke-Git @("status")

# Verificar se há remote configurado
Write-Host "`nVerificando remote configurado..." -ForegroundColor Cyan
$remoteOutput = Invoke-Git @("remote", "-v") -NoExit
$hasOrigin = $remoteOutput -match "origin"

# Configurar ou atualizar remote
if (-not $hasOrigin) {
    Write-Host "`nConfigurando remote 'origin'..." -ForegroundColor Cyan
    Invoke-Git @("remote", "add", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git")
} else {
    Write-Host "`nAtualizando remote 'origin' para Monpec_GestaoRural..." -ForegroundColor Cyan
    Invoke-Git @("remote", "set-url", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git")
}

# Verificar remote atualizado
Write-Host "`nRemote configurado:" -ForegroundColor Cyan
Invoke-Git @("remote", "-v")

# Detectar branch atual
Write-Host "`nDetectando branch atual..." -ForegroundColor Cyan
$currentBranchOutput = Invoke-Git @("branch", "--show-current")
$currentBranch = ($currentBranchOutput | Where-Object { $_ -match '\S' } | Select-Object -First 1).Trim()

# Se não conseguir detectar, tentar outras formas
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    $branchOutput = Invoke-Git @("branch")
    $currentBranch = ($branchOutput | Where-Object { $_ -match '^\*' } | ForEach-Object { $_ -replace '^\*\s+', '' }).Trim()
}

# Fallback para master ou main
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    $allBranches = Invoke-Git @("branch", "-a")
    if ($allBranches -match "main") {
        $currentBranch = "main"
    } else {
        $currentBranch = "master"
    }
    Write-Host "Usando branch: $currentBranch" -ForegroundColor Yellow
} else {
    Write-Host "Branch atual: $currentBranch" -ForegroundColor Green
}

# Adicionar todos os arquivos
Write-Host "`nAdicionando arquivos ao staging..." -ForegroundColor Cyan
Invoke-Git @("add", ".")

# Verificar o que será commitado
Write-Host "`nArquivos prontos para commit:" -ForegroundColor Cyan
Invoke-Git @("status", "--short")

# Fazer commit (se houver alterações)
$statusOutput = Invoke-Git @("status", "--porcelain") -NoExit
$hasChanges = $statusOutput -and ($statusOutput | Where-Object { $_ -match '\S' })

if ($hasChanges) {
    Write-Host "`nFazendo commit das alterações..." -ForegroundColor Cyan
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Atualização do projeto Monpec Gestão Rural - $timestamp"
    Invoke-Git @("commit", "-m", $commitMessage)
} else {
    Write-Host "`nNenhuma alteração para commitar." -ForegroundColor Yellow
}

# Fazer push para o GitHub
Write-Host "`nEnviando alterações para o GitHub..." -ForegroundColor Cyan
Write-Host "Branch: $currentBranch" -ForegroundColor Gray
Write-Host "Isso pode solicitar suas credenciais do GitHub." -ForegroundColor Yellow

try {
    Invoke-Git @("push", "-u", "origin", $currentBranch)
    Write-Host "`n=== Atualização concluída com sucesso! ===" -ForegroundColor Green
} catch {
    Write-Host "`nAVISO: Pode ser necessário fazer o push manualmente." -ForegroundColor Yellow
    Write-Host "Execute: git push -u origin $currentBranch" -ForegroundColor Yellow
}

Write-Host "Repositório: https://github.com/LMONCAO/Monpec_GestaoRural" -ForegroundColor Cyan


