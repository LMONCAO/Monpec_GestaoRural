# Script para puxar (pull) atualizações do GitHub
# Repositório: https://github.com/LMONCAO/Monpec_GestaoRural

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SINCRONIZANDO COM GITHUB" -ForegroundColor Cyan
Write-Host "  Puxando atualizações..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

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

# Procurar Git do GitHub Desktop
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
        return $false
    }
    return $true
}

# Verificar se estamos em um repositório Git
Write-Host "`nVerificando se é um repositório Git..." -ForegroundColor Cyan
$isGitRepo = Test-Path ".git"
if (-not $isGitRepo) {
    Write-Host "ERRO: Este diretório não é um repositório Git!" -ForegroundColor Red
    Write-Host "Inicializando repositório..." -ForegroundColor Yellow
    Invoke-Git @("init")
    Write-Host "Configurando remote..." -ForegroundColor Yellow
    Invoke-Git @("remote", "add", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git")
    Write-Host "Fazendo clone inicial..." -ForegroundColor Yellow
    Write-Host "AVISO: Como não é um repositório, você pode precisar fazer clone manualmente." -ForegroundColor Yellow
    exit 1
}

# Verificar remote configurado
Write-Host "`nVerificando remote configurado..." -ForegroundColor Cyan
$remoteOutput = Invoke-Git @("remote", "-v") -NoExit
$hasOrigin = $remoteOutput -match "origin"

# Configurar ou atualizar remote
if (-not $hasOrigin) {
    Write-Host "`nConfigurando remote 'origin'..." -ForegroundColor Cyan
    Invoke-Git @("remote", "add", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git") -NoExit
} else {
    Write-Host "`nVerificando remote 'origin'..." -ForegroundColor Cyan
    # Verificar se a URL está correta
    $currentRemoteUrl = Invoke-Git @("remote", "get-url", "origin") -NoExit
    if ($currentRemoteUrl -notmatch "Monpec_GestaoRural") {
        Write-Host "Atualizando URL do remote..." -ForegroundColor Yellow
        Invoke-Git @("remote", "set-url", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git") -NoExit
    }
}

# Verificar remote
Write-Host "`nRemote configurado:" -ForegroundColor Cyan
Invoke-Git @("remote", "-v")

# Detectar branch atual
Write-Host "`nDetectando branch atual..." -ForegroundColor Cyan
$currentBranchOutput = Invoke-Git @("branch", "--show-current") -NoExit
$currentBranch = $null

# Processar output do git branch --show-current
if ($currentBranchOutput) {
    $branchLine = $currentBranchOutput | Where-Object { $_ -match '\S' } | Select-Object -First 1
    if ($branchLine) {
        $currentBranch = $branchLine.ToString().Trim()
    }
}

# Se não conseguir detectar, tentar outras formas
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    $branchOutput = Invoke-Git @("branch") -NoExit
    if ($branchOutput) {
        $branchLine = $branchOutput | Where-Object { $_ -match '^\*' } | Select-Object -First 1
        if ($branchLine) {
            $currentBranch = ($branchLine.ToString() -replace '^\*\s+', '').Trim()
        }
    }
}

# Fallback para main ou master
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    $allBranches = Invoke-Git @("branch", "-a") -NoExit
    if ($allBranches) {
        if ($allBranches -match "main") {
            $currentBranch = "main"
        } elseif ($allBranches -match "master") {
            $currentBranch = "master"
        } else {
            $currentBranch = "main"
        }
    } else {
        $currentBranch = "master"
    }
    Write-Host "Usando branch: $currentBranch" -ForegroundColor Yellow
} else {
    Write-Host "Branch atual: $currentBranch" -ForegroundColor Green
}

# Verificar status antes do pull
Write-Host "`nVerificando status do repositório..." -ForegroundColor Cyan
$statusOutput = Invoke-Git @("status") -NoExit

# Verificar se há alterações locais não commitadas
$hasUncommittedChanges = $statusOutput -match "modified:|deleted:|new file:"
if ($hasUncommittedChanges) {
    Write-Host "`nAVISO: Há alterações locais não commitadas!" -ForegroundColor Yellow
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Fazer stash (guardar temporariamente) das alterações" -ForegroundColor Cyan
    Write-Host "2. Fazer commit das alterações antes do pull" -ForegroundColor Cyan
    Write-Host "3. Descartar alterações locais (CUIDADO!)" -ForegroundColor Red
    
    $choice = Read-Host "`nEscolha uma opção (1/2/3) ou 'c' para cancelar"
    
    if ($choice -eq "1") {
        Write-Host "Fazendo stash das alterações..." -ForegroundColor Cyan
        Invoke-Git @("stash", "save", "Alterações locais antes do pull - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    } elseif ($choice -eq "2") {
        Write-Host "Adicionando arquivos..." -ForegroundColor Cyan
        Invoke-Git @("add", ".")
        $commitMessage = Read-Host "Digite a mensagem do commit (ou pressione Enter para usar mensagem padrão)"
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "Alterações locais antes do pull - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        Invoke-Git @("commit", "-m", $commitMessage)
    } elseif ($choice -eq "3") {
        $confirm = Read-Host "Tem certeza que deseja descartar TODAS as alterações locais? (sim/não)"
        if ($confirm -eq "sim" -or $confirm -eq "s") {
            Write-Host "Descartando alterações locais..." -ForegroundColor Red
            Invoke-Git @("reset", "--hard", "HEAD")
            Invoke-Git @("clean", "-fd")
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "Operação cancelada." -ForegroundColor Yellow
        exit 0
    }
}

# Buscar atualizações do remote
Write-Host "`nBuscando atualizações do GitHub..." -ForegroundColor Cyan
$fetchResult = Invoke-Git @("fetch", "origin") -NoExit
if (-not $fetchResult) {
    Write-Host "AVISO: Erro ao buscar atualizações. Continuando mesmo assim..." -ForegroundColor Yellow
}

# Verificar se há atualizações
Write-Host "`nVerificando se há atualizações disponíveis..." -ForegroundColor Cyan
$localCommit = Invoke-Git @("rev-parse", "HEAD") -NoExit
$remoteCommitOutput = Invoke-Git @("rev-parse", "origin/$currentBranch") -NoExit

# Processar commits
$localCommitHash = $null
$remoteCommitHash = $null

if ($localCommit) {
    $localCommitHash = ($localCommit | Where-Object { $_ -match '\S' } | Select-Object -First 1).ToString().Trim()
}

if ($remoteCommitOutput) {
    $remoteCommitHash = ($remoteCommitOutput | Where-Object { $_ -match '\S' } | Select-Object -First 1).ToString().Trim()
}

if ($localCommitHash -and $remoteCommitHash -and $localCommitHash -eq $remoteCommitHash) {
    Write-Host "`nRepositório já está atualizado!" -ForegroundColor Green
} else {
    Write-Host "`nHá atualizações disponíveis. Fazendo pull..." -ForegroundColor Cyan
    
    # Fazer pull
    $pullResult = Invoke-Git @("pull", "origin", $currentBranch) -NoExit
    if ($pullResult) {
        Write-Host "`n=== Atualização concluída com sucesso! ===" -ForegroundColor Green
    } else {
        Write-Host "`nAVISO: Pode ter havido conflitos durante o pull." -ForegroundColor Yellow
        Write-Host "Verifique os arquivos e resolva os conflitos manualmente." -ForegroundColor Yellow
    }
}

# Se havia stash, perguntar se deseja restaurar
$stashList = Invoke-Git @("stash", "list") -NoExit
if ($stashList -and $stashList -match "stash@") {
    Write-Host "`nHá alterações guardadas (stash)." -ForegroundColor Cyan
    $restoreStash = Read-Host "Deseja restaurar as alterações guardadas? (s/n)"
    if ($restoreStash -eq "s" -or $restoreStash -eq "sim") {
        Write-Host "Restaurando alterações..." -ForegroundColor Cyan
        Invoke-Git @("stash", "pop") -NoExit
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  SINCRONIZAÇÃO CONCLUÍDA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Repositório: https://github.com/LMONCAO/Monpec_GestaoRural" -ForegroundColor Cyan

