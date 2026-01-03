# Script para aplicar a migration de produtos
# Execute este script para criar as tabelas de produtos no banco de dados

Write-Host "🔄 Aplicando Migration de Produtos" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erro: Arquivo manage.py não encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script na raiz do projeto Django" -ForegroundColor Yellow
    exit 1
}

# Verificar se Python está disponível
$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro: Python não encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python ou configure o PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📋 Verificando migrations pendentes..." -ForegroundColor Yellow
& $pythonCmd manage.py showmigrations gestao_rural | Select-String "0071"

Write-Host ""
Write-Host "🗄️ Aplicando migration 0071 (Produtos)..." -ForegroundColor Yellow
& $pythonCmd manage.py migrate gestao_rural 0071_adicionar_produtos_cadastro_fiscal

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migration aplicada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Acesse: /propriedade/{id}/compras/produtos/" -ForegroundColor White
    Write-Host "   2. Cadastre seus produtos" -ForegroundColor White
    Write-Host "   3. Use os produtos ao emitir NF-e" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro ao aplicar migration!" -ForegroundColor Red
    Write-Host "   Verifique os erros acima" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Tentando aplicar todas as migrations pendentes..." -ForegroundColor Cyan
    & $pythonCmd manage.py migrate
}

Write-Host ""
Write-Host "✨ Concluído!" -ForegroundColor Green

