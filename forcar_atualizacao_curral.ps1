# ========================================
# FORCAR ATUALIZACAO DA TELA CURRAL
# ========================================

Write-Host "FORCANDO ATUALIZACAO DA TELA CURRAL" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""

# Limpar cache do Python
Write-Host "1. Limpando cache do Python..." -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   Cache Python limpo!" -ForegroundColor Green

# Verificar template
Write-Host ""
Write-Host "2. Verificando template v3..." -ForegroundColor Cyan
$template = Get-Item "templates\gestao_rural\curral_dashboard_v3.html" -ErrorAction SilentlyContinue
if ($template) {
    Write-Host "   Template encontrado!" -ForegroundColor Green
    Write-Host "   Ultima modificacao: $($template.LastWriteTime)" -ForegroundColor Gray
    Write-Host "   Tamanho: $([math]::Round($template.Length/1KB, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "   ERRO: Template nao encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "SOLUCAO PARA VER A VERSÃO MAIS RECENTE:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "OPCAO 1 - FORCAR ATUALIZACAO NO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   Pressione Ctrl+F5 (ou Cmd+Shift+R no Mac)" -ForegroundColor Cyan
Write-Host "   Isso força o navegador a recarregar tudo" -ForegroundColor Gray
Write-Host ""
Write-Host "OPCAO 2 - LIMPAR CACHE DO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   1. Pressione Ctrl+Shift+Delete" -ForegroundColor Cyan
Write-Host "   2. Selecione 'Imagens e arquivos em cache'" -ForegroundColor Cyan
Write-Host "   3. Clique em 'Limpar dados'" -ForegroundColor Cyan
Write-Host "   4. Recarregue a pagina" -ForegroundColor Cyan
Write-Host ""
Write-Host "OPCAO 3 - USAR URL DIRETA V3:" -ForegroundColor Yellow
Write-Host "   Acesse diretamente:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Green
Write-Host "   (Substitua '2' pelo ID da sua propriedade)" -ForegroundColor Gray
Write-Host ""
Write-Host "OPCAO 4 - REINICIAR SERVIDOR:" -ForegroundColor Yellow
Write-Host "   1. Pare o servidor (Ctrl+C no terminal)" -ForegroundColor Cyan
Write-Host "   2. Execute: python manage.py runserver" -ForegroundColor Cyan
Write-Host "   3. Acesse a URL v3 novamente" -ForegroundColor Cyan
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "VERIFICACAO:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Apos seguir os passos acima, verifique:" -ForegroundColor Yellow
Write-Host "   - O titulo da pagina deve dizer 'Curral Inteligente 3.0'" -ForegroundColor Cyan
Write-Host "   - A URL deve terminar com /v3/" -ForegroundColor Cyan
Write-Host "   - Nao deve haver erros no console (F12)" -ForegroundColor Cyan
Write-Host ""

