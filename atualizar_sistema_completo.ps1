# Script para atualizar o sistema completo do GitHub
# Inclui templates, arquivos estáticos e todo o código

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZAÇÃO COMPLETA DO SISTEMA" -ForegroundColor Cyan
Write-Host "  Puxando todas as atualizações..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar Git
$gitPath = $null
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
    Write-Host "Git encontrado: $gitPath" -ForegroundColor Green
} else {
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
    } catch {
        Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
        exit 1
    }
}

# Função para executar Git
function Invoke-Git {
    param([string[]]$Arguments)
    & $gitPath $Arguments 2>&1 | ForEach-Object { Write-Host $_ }
    return $LASTEXITCODE -eq 0
}

# Verificar se é repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Não é um repositório Git!" -ForegroundColor Red
    exit 1
}

# Verificar branch atual
$currentBranch = Invoke-Git @("branch", "--show-current")
if (-not $currentBranch) {
    $branchOutput = Invoke-Git @("branch")
    $currentBranch = ($branchOutput | Where-Object { $_ -match '^\*' } | ForEach-Object { $_ -replace '^\*\s+', '' }).Trim()
}
if (-not $currentBranch) {
    $currentBranch = "master"
}

Write-Host "Branch atual: $currentBranch" -ForegroundColor Cyan
Write-Host ""

# Verificar status
Write-Host "Verificando status do repositório..." -ForegroundColor Cyan
$statusOutput = Invoke-Git @("status", "--porcelain")
$hasChanges = $statusOutput -and ($statusOutput | Where-Object { $_ -match '\S' })

if ($hasChanges) {
    Write-Host "`nAVISO: Há alterações locais não commitadas!" -ForegroundColor Yellow
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Fazer stash (guardar temporariamente)" -ForegroundColor Cyan
    Write-Host "2. Fazer commit das alterações" -ForegroundColor Cyan
    Write-Host "3. Descartar alterações (CUIDADO!)" -ForegroundColor Red
    Write-Host "4. Cancelar" -ForegroundColor Yellow
    
    $choice = Read-Host "`nEscolha (1/2/3/4)"
    
    if ($choice -eq "1") {
        Write-Host "Fazendo stash..." -ForegroundColor Cyan
        Invoke-Git @("stash", "push", "-m", "Stash antes de atualizar - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    } elseif ($choice -eq "2") {
        Write-Host "Adicionando arquivos..." -ForegroundColor Cyan
        Invoke-Git @("add", ".")
        $commitMessage = Read-Host "Mensagem do commit (ou Enter para padrão)"
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "Alterações locais - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        Invoke-Git @("commit", "-m", $commitMessage)
    } elseif ($choice -eq "3") {
        $confirm = Read-Host "Tem certeza? (sim/não)"
        if ($confirm -eq "sim" -or $confirm -eq "s") {
            Write-Host "Descartando alterações..." -ForegroundColor Red
            Invoke-Git @("reset", "--hard", "HEAD")
            Invoke-Git @("clean", "-fd")
        } else {
            Write-Host "Cancelado." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "Cancelado." -ForegroundColor Yellow
        exit 0
    }
}

# Buscar atualizações
Write-Host "`nBuscando atualizações do GitHub..." -ForegroundColor Cyan
Invoke-Git @("fetch", "origin") | Out-Null

# Verificar se há atualizações
Write-Host "Verificando atualizações disponíveis..." -ForegroundColor Cyan
$localCommit = (Invoke-Git @("rev-parse", "HEAD") | Select-Object -First 1).Trim()
$remoteCommit = (Invoke-Git @("rev-parse", "origin/$currentBranch") | Select-Object -First 1).Trim()

if ($localCommit -eq $remoteCommit) {
    Write-Host "`nRepositório já está atualizado!" -ForegroundColor Green
} else {
    Write-Host "`nHá atualizações disponíveis!" -ForegroundColor Cyan
    Write-Host "Commit local:  $localCommit" -ForegroundColor Gray
    Write-Host "Commit remoto: $remoteCommit" -ForegroundColor Gray
    Write-Host ""
    
    # Mostrar arquivos que serão atualizados
    Write-Host "Arquivos que serão atualizados:" -ForegroundColor Cyan
    $changedFiles = Invoke-Git @("diff", "--name-only", "HEAD", "origin/$currentBranch")
    $changedFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    
    # Contar templates
    $templateFiles = $changedFiles | Where-Object { $_ -match "templates/" }
    if ($templateFiles) {
        Write-Host "`nTemplates que serão atualizados: $($templateFiles.Count)" -ForegroundColor Yellow
    }
    
    Write-Host "`nFazendo pull..." -ForegroundColor Cyan
    if (Invoke-Git @("pull", "origin", $currentBranch)) {
        Write-Host "`n=== Atualização concluída com sucesso! ===" -ForegroundColor Green
        
        # Verificar templates atualizados
        if ($templateFiles) {
            Write-Host "`nTemplates atualizados:" -ForegroundColor Cyan
            $templateFiles | ForEach-Object { Write-Host "  [OK] $_" -ForegroundColor Green }
        }
    } else {
        Write-Host "`nAVISO: Pode ter havido conflitos!" -ForegroundColor Yellow
        Write-Host "Verifique os arquivos manualmente." -ForegroundColor Yellow
    }
}

# Verificar se há stash para restaurar
$stashList = Invoke-Git @("stash", "list")
if ($stashList -and $stashList -match "stash@") {
    Write-Host "`nHá alterações guardadas (stash)." -ForegroundColor Cyan
    $restoreStash = Read-Host "Deseja restaurar? (s/n)"
    if ($restoreStash -eq "s" -or $restoreStash -eq "sim") {
        Write-Host "Restaurando alterações..." -ForegroundColor Cyan
        Invoke-Git @("stash", "pop") | Out-Null
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ATUALIZAÇÃO CONCLUÍDA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Execute as migrações: python manage.py migrate" -ForegroundColor White
Write-Host "2. Colete arquivos estáticos: python manage.py collectstatic" -ForegroundColor White
Write-Host "3. Reinicie o servidor se estiver rodando" -ForegroundColor White

