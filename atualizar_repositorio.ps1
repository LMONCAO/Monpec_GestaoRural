# Script para atualizar o repositório do GitHub
# Execute este script no outro computador para sincronizar com as mudanças mais recentes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZANDO REPOSITÓRIO DO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos na pasta correta
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Esta não é uma pasta Git!" -ForegroundColor Red
    Write-Host "Navegue até a pasta do projeto Monpec_GestaoRural" -ForegroundColor Yellow
    exit 1
}

# Mostrar status atual
Write-Host "Status atual do repositório:" -ForegroundColor Yellow
git status
Write-Host ""

# Buscar mudanças do GitHub
Write-Host "Buscando mudanças do GitHub..." -ForegroundColor Yellow
git fetch origin
Write-Host ""

# Verificar se há mudanças para baixar
$status = git status
if ($status -match "Your branch is behind") {
    Write-Host "Há atualizações disponíveis no GitHub!" -ForegroundColor Green
    Write-Host ""
    
    # Mostrar commits que serão baixados
    Write-Host "Commits que serão baixados:" -ForegroundColor Yellow
    git log HEAD..origin/master --oneline
    Write-Host ""
    
    # Perguntar se quer continuar
    $resposta = Read-Host "Deseja atualizar agora? (S/N)"
    if ($resposta -eq "S" -or $resposta -eq "s" -or $resposta -eq "Y" -or $resposta -eq "y") {
        Write-Host ""
        Write-Host "Atualizando arquivos..." -ForegroundColor Yellow
        git pull origin master
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  REPOSITÓRIO ATUALIZADO COM SUCESSO!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Últimos 5 commits:" -ForegroundColor Cyan
            git log --oneline -5
        } else {
            Write-Host ""
            Write-Host "ERRO ao atualizar! Verifique se há conflitos." -ForegroundColor Red
        }
    } else {
        Write-Host "Atualização cancelada." -ForegroundColor Yellow
    }
} elseif ($status -match "Your branch is up to date") {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  REPOSITÓRIO JÁ ESTÁ ATUALIZADO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Último commit:" -ForegroundColor Cyan
    git log --oneline -1
} else {
    Write-Host "Atualizando arquivos..." -ForegroundColor Yellow
    git pull origin master
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  REPOSITÓRIO ATUALIZADO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Últimos 5 commits:" -ForegroundColor Cyan
        git log --oneline -5
    } else {
        Write-Host ""
        Write-Host "ERRO ao atualizar! Verifique se há conflitos." -ForegroundColor Red
        Write-Host ""
        Write-Host "Status atual:" -ForegroundColor Yellow
        git status
    }
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

