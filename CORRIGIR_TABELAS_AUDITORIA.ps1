# ========================================
# CORRIGIR TABELAS DE AUDITORIA
# ========================================

Write-Host "🔧 CORRIGINDO TABELAS DE AUDITORIA" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""

# Parar processos Python se estiverem rodando
Write-Host "🛑 Verificando processos Python..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "📊 Criando tabelas de auditoria..." -ForegroundColor Cyan
Write-Host ""

# Executar script Python
python311\python.exe criar_tabelas_auditoria.py

Write-Host ""
Write-Host "✅ TABELAS CORRIGIDAS!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 TABELAS CRIADAS:" -ForegroundColor Cyan
Write-Host "• gestao_rural_verificacaoemail" -ForegroundColor White
Write-Host "• gestao_rural_sessaosegura" -ForegroundColor White
Write-Host "• gestao_rural_logauditoria" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Agora voce pode fazer login normalmente!" -ForegroundColor Green
Write-Host ""


