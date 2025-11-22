# Script para abrir a página promocional no navegador para captura de tela
# Abra este arquivo HTML no navegador e capture a tela manualmente

$htmlFile = Join-Path $PSScriptRoot "templates\gestao_rural\promo_whatsapp.html"

if (Test-Path $htmlFile) {
    Write-Host "🚀 Abrindo página promocional no navegador..." -ForegroundColor Green
    Write-Host "📸 Use a ferramenta de captura de tela para salvar a imagem" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Dicas:" -ForegroundColor Cyan
    Write-Host "   1. Ajuste o zoom do navegador (Ctrl + Scroll)" -ForegroundColor White
    Write-Host "   2. Use a ferramenta de captura do Windows (Win + Shift + S)" -ForegroundColor White
    Write-Host "   3. Capture apenas o card promocional" -ForegroundColor White
    Write-Host "   4. Salve como PNG para melhor qualidade" -ForegroundColor White
    Write-Host ""
    
    Start-Process $htmlFile
    
    Write-Host "✅ Página aberta! Capture a tela quando estiver pronto." -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo não encontrado: $htmlFile" -ForegroundColor Red
    Write-Host "   Certifique-se de que o arquivo existe no caminho correto." -ForegroundColor Yellow
}


