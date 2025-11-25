# Script para iniciar servidor de desenvolvimento local
# MONPEC - Sistema de Gestão Rural

Write-Host "🚀 Iniciando Servidor Local - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para pasta do projeto
$projectPath = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
Set-Location $projectPath

# Verificar se ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Execute primeiro:" -ForegroundColor Yellow
    Write-Host "   .\configurar_ambiente_local.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Ativar ambiente virtual
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Erro ao ativar ambiente virtual." -ForegroundColor Yellow
    Write-Host "   Tente executar manualmente:" -ForegroundColor Yellow
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   python manage.py runserver" -ForegroundColor White
    exit 1
}

Write-Host "✅ Ambiente virtual ativado!" -ForegroundColor Green
Write-Host ""

# Verificar se manage.py existe
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Arquivo manage.py não encontrado!" -ForegroundColor Red
    Write-Host "   Certifique-se de estar na pasta correta do projeto." -ForegroundColor Yellow
    exit 1
}

# Iniciar servidor
Write-Host "🌐 Iniciando servidor Django..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servidor iniciando..." -ForegroundColor Cyan
Write-Host "  Acesse: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver

















