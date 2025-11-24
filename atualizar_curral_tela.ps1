# ========================================
# ATUALIZAR TELA CURRAL - FORCAR VERSÃO MAIS RECENTE
# ========================================

Write-Host "ATUALIZANDO TELA CURRAL PARA VERSÃO MAIS RECENTE" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host ""

# Verificar se estamos no diretorio correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: Execute este script na raiz do projeto Django!" -ForegroundColor Red
    exit 1
}

Write-Host "1. Limpando cache do Python..." -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   Cache limpo!" -ForegroundColor Green

Write-Host ""
Write-Host "2. Verificando templates do curral..." -ForegroundColor Cyan
$templates = @(
    "templates\gestao_rural\curral_dashboard_v3.html",
    "templates\gestao_rural\curral_dashboard.html",
    "templates\gestao_rural\curral_painel.html"
)

foreach ($template in $templates) {
    if (Test-Path $template) {
        $info = Get-Item $template
        Write-Host "   $template - Ultima modificacao: $($info.LastWriteTime)" -ForegroundColor Gray
    } else {
        Write-Host "   $template - NAO ENCONTRADO" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "3. Verificando views do curral..." -ForegroundColor Cyan
if (Test-Path "gestao_rural\views_curral.py") {
    $info = Get-Item "gestao_rural\views_curral.py"
    Write-Host "   views_curral.py - Ultima modificacao: $($info.LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "   views_curral.py - NAO ENCONTRADO" -ForegroundColor Red
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "INSTRUCOES PARA VER A VERSÃO MAIS RECENTE:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. LIMPAR CACHE DO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   - Pressione Ctrl+Shift+Delete" -ForegroundColor Cyan
Write-Host "   - Ou pressione Ctrl+F5 para forcar atualizacao" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. USAR A URL CORRETA:" -ForegroundColor Yellow
Write-Host "   URL V3 (MAIS RECENTE):" -ForegroundColor Green
Write-Host "   http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Cyan
Write-Host ""
Write-Host "   URL PAINEL (ALTERNATIVA):" -ForegroundColor Green
Write-Host "   http://localhost:8000/propriedade/2/curral/painel/" -ForegroundColor Cyan
Write-Host ""
Write-Host "   URL ANTIGA (REDIRECIONA):" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/propriedade/2/curral/" -ForegroundColor Gray
Write-Host ""
Write-Host "3. REINICIAR SERVIDOR (se necessario):" -ForegroundColor Yellow
Write-Host "   - Pare o servidor (Ctrl+C)" -ForegroundColor Cyan
Write-Host "   - Execute: python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. VERIFICAR SE ESTA USANDO A VERSÃO CORRETA:" -ForegroundColor Yellow
Write-Host "   - A URL deve terminar com /v3/ para a versao mais recente" -ForegroundColor Cyan
Write-Host "   - Verifique o titulo da pagina (deve dizer 'Curral Inteligente 3.0')" -ForegroundColor Cyan
Write-Host ""

