# Script para Sincronizar com GitHub
# MONPEC - Sistema de Gestão Rural

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sincronização com GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Função para encontrar Git
function Find-Git {
    $possiblePaths = @(
        "$env:ProgramFiles\Git\cmd\git.exe",
        "$env:ProgramFiles\Git\bin\git.exe",
        "$env:ProgramFiles (x86)\Git\cmd\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    )
    
    # Procurar Git do GitHub Desktop
    $githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($githubDesktopGit) {
        return $githubDesktopGit.FullName
    }
    
    # Procurar nos caminhos padrão
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # Tentar no PATH
    try {
        return (Get-Command git -ErrorAction Stop).Source
    } catch {
        return $null
    }
}

# Encontrar Git
$gitPath = Find-Git

if (-not $gitPath) {
    Write-Host "[ERRO] Git não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Instale o Git: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Use o GitHub Desktop: https://desktop.github.com/" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "[OK] Git encontrado: $gitPath" -ForegroundColor Green
Write-Host ""

# Função para executar Git
function Invoke-Git {
    param([string[]]$Arguments)
    & $gitPath $Arguments
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    return $true
}

# Verificar se é repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "[ERRO] Esta pasta não é um repositório Git!" -ForegroundColor Red
    Write-Host ""
    $init = Read-Host "Deseja inicializar um repositório Git? (s/n)"
    if ($init -eq 's' -or $init -eq 'S') {
        Invoke-Git @("init")
        Write-Host "[OK] Repositório inicializado!" -ForegroundColor Green
    } else {
        exit 1
    }
}

# Verificar status
Write-Host "[INFO] Verificando status do repositório..." -ForegroundColor Cyan
$statusOutput = & $gitPath status --porcelain
$branchOutput = & $gitPath branch --show-current
$branch = ($branchOutput | Out-String).Trim()

if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
    Write-Host "[INFO] Usando branch: $branch" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Branch atual: $branch" -ForegroundColor Green
}

Write-Host ""

# Verificar remote
$remoteOutput = Invoke-Git @("remote", "-v") | Out-String
$hasOrigin = $remoteOutput -match "origin"

if (-not $hasOrigin) {
    Write-Host "[INFO] Configurando remote 'origin'..." -ForegroundColor Cyan
    $repoUrl = Read-Host "Digite a URL do repositório GitHub (ou pressione Enter para usar padrão)"
    if ([string]::IsNullOrWhiteSpace($repoUrl)) {
        $repoUrl = "https://github.com/LMONCAO/Monpec_GestaoRural.git"
    }
    Invoke-Git @("remote", "add", "origin", $repoUrl)
    Write-Host "[OK] Remote configurado!" -ForegroundColor Green
} else {
    Write-Host "[OK] Remote já configurado" -ForegroundColor Green
}

Write-Host ""

# Verificar alterações
if ($statusOutput -and ($statusOutput | Where-Object { $_.Trim() -ne '' })) {
    Write-Host "[INFO] Alterações detectadas:" -ForegroundColor Yellow
    Invoke-Git @("status", "--short")
    Write-Host ""
    
    $response = Read-Host "Deseja fazer commit dessas alterações? (s/n)"
    if ($response -eq 's' -or $response -eq 'S') {
        $message = Read-Host "Digite a mensagem do commit (ou pressione Enter para usar padrão)"
        if ([string]::IsNullOrWhiteSpace($message)) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $message = "Atualização automática - $timestamp"
        }
        
        Write-Host ""
        Write-Host "[INFO] Adicionando arquivos..." -ForegroundColor Cyan
        Invoke-Git @("add", ".")
        
        Write-Host "[INFO] Fazendo commit..." -ForegroundColor Cyan
        if (Invoke-Git @("commit", "-m", $message)) {
            Write-Host "[OK] Commit realizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "[ERRO] Erro ao fazer commit" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "[OK] Nenhuma alteração pendente" -ForegroundColor Green
}

Write-Host ""

# Fazer Pull primeiro
Write-Host "[INFO] Fazendo Pull do GitHub..." -ForegroundColor Cyan
Invoke-Git @("pull", "origin", $branch, "--no-rebase") | Out-Null

Write-Host ""

# Verificar se há commits locais para enviar
$localCommitsOutput = & $gitPath log "origin/$branch..HEAD" --oneline 2>$null
$localCommits = ($localCommitsOutput | Out-String).Trim()

if ($localCommits -and $localCommits -ne '') {
    Write-Host "[INFO] Enviando alterações para o GitHub..." -ForegroundColor Cyan
    Write-Host "Branch: $branch" -ForegroundColor Gray
    Write-Host ""
    
    if (Invoke-Git @("push", "-u", "origin", $branch)) {
        Write-Host ""
        Write-Host "[OK] Push realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[AVISO] Erro ao fazer push." -ForegroundColor Yellow
        Write-Host "Pode ser necessário:" -ForegroundColor Yellow
        Write-Host "1. Verificar suas credenciais do GitHub" -ForegroundColor White
        Write-Host "2. Executar manualmente: git push -u origin $branch" -ForegroundColor White
    }
} else {
    Write-Host "[INFO] Nenhum commit local para enviar" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sincronização concluída!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

