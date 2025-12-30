# Script para aplicar migrations na ordem correta
# Resolve o conflito entre migrations 0071 e 0072

Write-Host "🔍 Verificando status das migrations..." -ForegroundColor Cyan

# Verificar status atual
python manage.py showmigrations gestao_rural | Select-String -Pattern "007[0-9]|008[0-2]" -Context 0,0

Write-Host "`n📋 Aplicando migrations na ordem correta..." -ForegroundColor Yellow

# Aplicar migrations sequencialmente até a 0073
Write-Host "`n1️⃣ Aplicando migration 0070..." -ForegroundColor Green
python manage.py migrate gestao_rural 0070

Write-Host "`n2️⃣ Aplicando migration 0071..." -ForegroundColor Green
python manage.py migrate gestao_rural 0071

Write-Host "`n3️⃣ Aplicando migration 0072..." -ForegroundColor Green
python manage.py migrate gestao_rural 0072

Write-Host "`n4️⃣ Aplicando migration 0073..." -ForegroundColor Green
python manage.py migrate gestao_rural 0073

Write-Host "`n5️⃣ Aplicando migration de merge 0074 (resolve conflito)..." -ForegroundColor Yellow
python manage.py migrate gestao_rural 0074

Write-Host "`n6️⃣ Aplicando todas as migrations restantes..." -ForegroundColor Green
python manage.py migrate

Write-Host "`n✅ Migrations aplicadas com sucesso!" -ForegroundColor Green
Write-Host "`n📊 Status final:" -ForegroundColor Cyan
python manage.py showmigrations gestao_rural | Select-String -Pattern "007[0-9]|008[0-2]" -Context 0,0






