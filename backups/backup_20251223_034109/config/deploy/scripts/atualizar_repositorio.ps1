# Script para atualizar o repositório do GitHub
# Execute este script no outro computador para sincronizar com as mudanças mais recentes

# Codificação UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZANDO REPOSITÓRIO DO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
$gitPath = $null
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitPath = "git"
} elseif (Test-Path "C:\Program Files\Git\bin\git.exe") {
    $gitPath = "C:\Program Files\Git\bin\git.exe"
} elseif (Test-Path "C:\Program Files (x86)\Git\bin\git.exe") {
    $gitPath = "C:\Program Files (x86)\Git\bin\git.exe"
} else {
    Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Git em: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Verificar se estamos na pasta correta
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Esta não é uma pasta Git!" -ForegroundColor Red
    Write-Host "Navegue até a pasta do projeto Monpec_GestaoRural" -ForegroundColor Yellow
    exit 1
}

# Mostrar status atual
Write-Host "Status atual do repositório:" -ForegroundColor Yellow
& $gitPath status
Write-Host ""

# Buscar mudanças do GitHub
Write-Host "Buscando mudanças do GitHub..." -ForegroundColor Yellow
& $gitPath fetch origin
Write-Host ""

# Verificar se há mudanças para baixar
$statusOutput = & $gitPath status 2>&1 | Out-String
$behind = $statusOutput -match "Your branch is behind"
$upToDate = $statusOutput -match "Your branch is up to date"

if ($behind) {
    Write-Host "Há atualizações disponíveis no GitHub!" -ForegroundColor Green
    Write-Host ""
    
    # Mostrar commits que serão baixados
    Write-Host "Commits que serão baixados:" -ForegroundColor Yellow
    & $gitPath log HEAD..origin/master --oneline
    Write-Host ""
    
    # Perguntar se quer continuar
    $resposta = Read-Host "Deseja atualizar agora? (S/N)"
    if ($resposta -eq "S" -or $resposta -eq "s" -or $resposta -eq "Y" -or $resposta -eq "y") {
        Write-Host ""
        Write-Host "Atualizando arquivos..." -ForegroundColor Yellow
        & $gitPath pull origin master
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  REPOSITÓRIO ATUALIZADO COM SUCESSO!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Últimos 5 commits:" -ForegroundColor Cyan
            & $gitPath log --oneline -5
        } else {
            Write-Host ""
            Write-Host "ERRO ao atualizar! Verifique se há conflitos." -ForegroundColor Red
        }
    } else {
        Write-Host "Atualização cancelada." -ForegroundColor Yellow
    }
} elseif ($upToDate) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  REPOSITÓRIO JÁ ESTÁ ATUALIZADO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Último commit:" -ForegroundColor Cyan
    & $gitPath log --oneline -1
} else {
    Write-Host "Atualizando arquivos..." -ForegroundColor Yellow
    & $gitPath pull origin master
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  REPOSITÓRIO ATUALIZADO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Últimos 5 commits:" -ForegroundColor Cyan
        & $gitPath log --oneline -5
    } else {
        Write-Host ""
        Write-Host "ERRO ao atualizar! Verifique se há conflitos." -ForegroundColor Red
        Write-Host ""
        Write-Host "Status atual:" -ForegroundColor Yellow
        & $gitPath status
    }
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
