# ============================================================================
# EXECUTAR DEPLOY AGORA - GOOGLE CLOUD
# ============================================================================
# Este script deve ser executado DENTRO da pasta do projeto
# ============================================================================

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script dentro da pasta do projeto Django" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Exemplo:" -ForegroundColor Cyan
    Write-Host "  cd 'C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural'" -ForegroundColor Gray
    Write-Host "  .\EXECUTAR_DEPLOY_AGORA.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO DEPLOY NO GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Executar o script principal
& ".\DEPLOY_GOOGLE_CLOUD_COMPLETO_AUTOMATICO.ps1"
