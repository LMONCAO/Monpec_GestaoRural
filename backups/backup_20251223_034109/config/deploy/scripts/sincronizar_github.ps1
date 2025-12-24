# Script para Sincronizar com GitHub
# Este script ajuda a manter a pasta sincronizada com o GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sincronização com GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitInstalled) {
    Write-Host "[AVISO] Git nao esta instalado ou nao esta no PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Instale o Git: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Use o GitHub Desktop: https://desktop.github.com/" -ForegroundColor White
    Write-Host ""
    Write-Host "Pressione qualquer tecla para continuar com GitHub Desktop..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Verificar se estamos em um repositório Git
if (-not (Test-Path .git)) {
    Write-Host "[ERRO] Esta pasta nao e um repositorio Git!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute este script na pasta do projeto Monpec_GestaoRural" -ForegroundColor Yellow
    exit
}

# Verificar status do repositório
Write-Host "[INFO] Verificando status do repositorio..." -ForegroundColor Cyan
Write-Host ""

$status = git status --porcelain
$branch = git branch --show-current

Write-Host "Branch atual: $branch" -ForegroundColor Green
Write-Host ""

# Verificar se há alterações locais
if ($status) {
    Write-Host "[INFO] Alteracoes detectadas:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    
    $response = Read-Host "Deseja fazer commit dessas alterações? (s/n)"
    if ($response -eq 's' -or $response -eq 'S') {
        $message = Read-Host "Digite a mensagem do commit"
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "Atualização automática - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        
        Write-Host ""
        Write-Host "[INFO] Fazendo commit..." -ForegroundColor Cyan
        git add .
        git commit -m $message
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Commit realizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "[ERRO] Erro ao fazer commit" -ForegroundColor Red
            exit
        }
    }
} else {
    Write-Host "[OK] Nenhuma alteracao pendente" -ForegroundColor Green
    Write-Host ""
}

# Fazer Pull primeiro
Write-Host "[INFO] Fazendo Pull do GitHub..." -ForegroundColor Cyan
git pull origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Pull realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Pode haver conflitos. Verifique manualmente." -ForegroundColor Yellow
}

Write-Host ""

# Fazer Push se houver commits locais
$localCommits = git log origin/$branch..HEAD --oneline 2>$null

if ($localCommits) {
    Write-Host "[INFO] Enviando alteracoes para o GitHub..." -ForegroundColor Cyan
    git push origin $branch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Push realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Erro ao fazer push. Verifique suas credenciais." -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Nenhum commit local para enviar" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sincronização concluída!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

