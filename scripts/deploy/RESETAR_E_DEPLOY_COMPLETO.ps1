# 🔥 RESETAR E DEPLOY COMPLETO - GOOGLE CLOUD
# Este script faz reset completo e depois faz deploy limpo

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔥 RESETAR E DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script vai:" -ForegroundColor Yellow
Write-Host "1. Resetar completamente o Google Cloud (excluir tudo)"
Write-Host "2. Fazer deploy limpo do zero"
Write-Host ""
Write-Host "⚠️  ATENÇÃO: Isso vai excluir TODOS os recursos e dados!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Digite 'SIM' para continuar (qualquer outra coisa cancela)"
if ($confirm -ne "SIM") {
    Write-Host "Operação cancelada pelo usuário." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ETAPA 1: RESETAR GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Executar script de reset
if (Test-Path "RESETAR_GOOGLE_CLOUD.ps1") {
    Write-Host "Executando script de reset..." -ForegroundColor Cyan
    & ".\RESETAR_GOOGLE_CLOUD.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro no reset. Verifique os logs acima." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Script RESETAR_GOOGLE_CLOUD.ps1 não encontrado!" -ForegroundColor Red
    Write-Host "Execute manualmente primeiro." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ RESET CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$continue = Read-Host "Deseja fazer o deploy agora? (S/N)"
if ($continue -ne "S" -and $continue -ne "s") {
    Write-Host "Deploy cancelado. Execute quando estiver pronto:" -ForegroundColor Yellow
    Write-Host "   .\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ETAPA 2: DEPLOY COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Executar script de deploy
if (Test-Path "DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1") {
    Write-Host "Executando deploy completo..." -ForegroundColor Cyan
    & ".\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Script DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1 não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 PROCESSO COMPLETO FINALIZADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""






