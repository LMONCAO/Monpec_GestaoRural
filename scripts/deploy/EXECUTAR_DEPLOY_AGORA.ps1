# 🚀 EXECUTAR DEPLOY AGORA - MONPEC
# Script principal para executar o deploy completo
# Execute: .\EXECUTAR_DEPLOY_AGORA.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 EXECUTANDO DEPLOY - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Executar o script de deploy completo
& ".\DEPLOY_FINAL_COMPLETO.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deploy executado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Configure o admin usando criar_admin_producao.py" -ForegroundColor White
    Write-Host "   2. Teste a landing page e formulário de demonstração" -ForegroundColor White
    Write-Host "   3. Verifique as credenciais do Mercado Pago" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
    Write-Host ""
    exit 1
}
