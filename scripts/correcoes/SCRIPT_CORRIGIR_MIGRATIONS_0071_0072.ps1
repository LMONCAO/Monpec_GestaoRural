# Script para corrigir e reaplicar migrations 0071 e 0072
# IMPORTANTE: Execute em ambiente de desenvolvimento/teste primeiro!

Write-Host "🔧 Script de Correção das Migrations 0071 e 0072" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Verificar status atual
Write-Host "`n📊 Verificando status atual das migrations..." -ForegroundColor Yellow
python manage.py showmigrations gestao_rural | Select-String -Pattern "007[0-4]" -Context 0,0

Write-Host "`n⚠️ ATENÇÃO: Este script vai fazer rollback das migrations 0071-0074" -ForegroundColor Red
Write-Host "   Certifique-se de ter um backup do banco de dados!" -ForegroundColor Red

$confirm = Read-Host "`nDeseja continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit
}

# Verificar se há produtos no banco
Write-Host "`n🔍 Verificando se há produtos no banco..." -ForegroundColor Yellow
$produtos_count = python manage.py shell -c "from gestao_rural.models_compras_financeiro import Produto; print(Produto.objects.count())" 2>&1 | Select-Object -Last 1

if ($produtos_count -match '\d+') {
    $count = [int]$produtos_count
    if ($count -gt 0) {
        Write-Host "⚠️ Existem $count produtos no banco!" -ForegroundColor Red
        Write-Host "   Você precisa decidir se quer mantê-los ou deletá-los." -ForegroundColor Yellow
        $keep = Read-Host "   Manter produtos? (S/N)"
        
        if ($keep -ne "S" -and $keep -ne "s") {
            Write-Host "⚠️ Você precisará deletar os produtos manualmente antes de continuar." -ForegroundColor Red
            exit
        }
    }
}

# Fazer rollback
Write-Host "`n⏪ Fazendo rollback até migration 0070..." -ForegroundColor Yellow
python manage.py migrate gestao_rural 0070

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer rollback!" -ForegroundColor Red
    Write-Host "   Tente fazer manualmente: python manage.py migrate gestao_rural 0070" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Rollback concluído!" -ForegroundColor Green

# Aplicar migrations corrigidas
Write-Host "`n📦 Aplicando migrations corrigidas..." -ForegroundColor Yellow

Write-Host "`n1️⃣ Aplicando migration 0071 (CORRIGIDA)..." -ForegroundColor Green
python manage.py migrate gestao_rural 0071

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao aplicar migration 0071!" -ForegroundColor Red
    exit 1
}

Write-Host "`n2️⃣ Aplicando migration 0072 (CORRIGIDA)..." -ForegroundColor Green
python manage.py migrate gestao_rural 0072

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao aplicar migration 0072!" -ForegroundColor Red
    exit 1
}

Write-Host "`n3️⃣ Aplicando migration 0073..." -ForegroundColor Green
python manage.py migrate gestao_rural 0073

Write-Host "`n4️⃣ Aplicando migration 0074 (merge)..." -ForegroundColor Green
python manage.py migrate gestao_rural 0074

Write-Host "`n5️⃣ Aplicando demais migrations..." -ForegroundColor Green
python manage.py migrate

# Verificar status final
Write-Host "`n✅ Migrations aplicadas com sucesso!" -ForegroundColor Green
Write-Host "`n📊 Status final:" -ForegroundColor Cyan
python manage.py showmigrations gestao_rural | Select-String -Pattern "007[0-4]" -Context 0,0

Write-Host "`n🎉 Processo concluído! Teste fazer login para verificar se o erro 500 foi resolvido." -ForegroundColor Green






