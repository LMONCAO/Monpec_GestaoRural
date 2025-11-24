# Script para verificar arquivos e atualizar o sistema
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICAÇÃO E ATUALIZAÇÃO DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar Git
$gitPath = $null
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
} else {
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
    } catch {
        Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
        exit 1
    }
}

# 1. Verificar status do repositório
Write-Host "[1/4] Verificando status do repositório..." -ForegroundColor Cyan
& $gitPath status --short | ForEach-Object {
    if ($_ -match "^M ") {
        Write-Host "  [MODIFICADO] $($_.Substring(2))" -ForegroundColor Yellow
    } elseif ($_ -match "^A ") {
        Write-Host "  [ADICIONADO] $($_.Substring(2))" -ForegroundColor Green
    } elseif ($_ -match "^D ") {
        Write-Host "  [DELETADO] $($_.Substring(2))" -ForegroundColor Red
    } elseif ($_ -match "^\\?\\? ") {
        Write-Host "  [NOVO] $($_.Substring(3))" -ForegroundColor Cyan
    }
}

# Contar arquivos
$modifiedCount = (& $gitPath diff --name-only).Count
$untrackedCount = (& $gitPath ls-files --others --exclude-standard).Count

Write-Host ""
Write-Host "Resumo:" -ForegroundColor Cyan
Write-Host "  Arquivos modificados: $modifiedCount" -ForegroundColor Yellow
Write-Host "  Arquivos não rastreados: $untrackedCount" -ForegroundColor Cyan
Write-Host ""

# 2. Verificar se há atualizações no GitHub
Write-Host "[2/4] Verificando atualizações no GitHub..." -ForegroundColor Cyan
& $gitPath fetch origin | Out-Null

$localCommit = (& $gitPath rev-parse HEAD).Trim()
$remoteCommit = (& $gitPath rev-parse origin/master).Trim()

if ($localCommit -eq $remoteCommit) {
    Write-Host "  [OK] Repositório já está atualizado com o GitHub!" -ForegroundColor Green
} else {
    Write-Host "  [ATUALIZAÇÕES DISPONÍVEIS] Há novas alterações no GitHub!" -ForegroundColor Yellow
    Write-Host "  Execute 'git pull' para atualizar." -ForegroundColor Yellow
}
Write-Host ""

# 3. Verificar Python e Django
Write-Host "[3/4] Verificando ambiente Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERRO] Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se manage.py existe
if (-not (Test-Path "manage.py")) {
    Write-Host "  [ERRO] manage.py não encontrado!" -ForegroundColor Red
    Write-Host "  Execute este script na raiz do projeto Django." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Projeto Django encontrado" -ForegroundColor Green
Write-Host ""

# 4. Aplicar atualizações do sistema
Write-Host "[4/4] Aplicando atualizações do sistema..." -ForegroundColor Cyan
Write-Host ""

# Verificar se há ambiente virtual e usar o Python correto
$pythonCmd = "python"
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "  Usando Python do ambiente virtual (venv)..." -ForegroundColor Gray
    $pythonCmd = ".\venv\Scripts\python.exe"
} elseif (Test-Path "env\Scripts\python.exe") {
    Write-Host "  Usando Python do ambiente virtual (env)..." -ForegroundColor Gray
    $pythonCmd = ".\env\Scripts\python.exe"
}

# Executar migrações
Write-Host "  [1/2] Executando migrações do banco de dados..." -ForegroundColor Cyan
$migrateOutput = & $pythonCmd manage.py migrate 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Migrações aplicadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] Pode ter havido erros nas migrações." -ForegroundColor Yellow
    Write-Host $migrateOutput -ForegroundColor Gray
}

# Coletar arquivos estáticos
Write-Host "  [2/2] Coletando arquivos estáticos..." -ForegroundColor Cyan
$collectstaticOutput = & $pythonCmd manage.py collectstatic --noinput 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Arquivos estáticos coletados!" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] Pode ter havido erros ao coletar estáticos." -ForegroundColor Yellow
    Write-Host $collectstaticOutput -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  VERIFICAÇÃO E ATUALIZAÇÃO CONCLUÍDAS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Se houver alterações locais, considere fazer commit" -ForegroundColor White
Write-Host "  2. Execute '.\rodar_localhost.ps1' para iniciar o servidor" -ForegroundColor White
Write-Host "  3. Ou execute 'python manage.py runserver' manualmente" -ForegroundColor White
Write-Host ""

