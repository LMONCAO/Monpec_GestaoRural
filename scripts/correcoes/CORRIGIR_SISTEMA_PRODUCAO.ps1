# Script para corrigir e diagnosticar problemas no servidor de produção
# Execute este script no servidor para identificar e corrigir problemas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORREÇÃO DO SISTEMA MONPEC - PRODUÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# 2. Executar diagnóstico
Write-Host "Executando diagnóstico..." -ForegroundColor Yellow
python diagnosticar_erro_producao.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORREÇÕES AUTOMÁTICAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 3. Verificar e aplicar migrações
Write-Host "Verificando migrações..." -ForegroundColor Yellow
python manage.py showmigrations --settings=sistema_rural.settings_producao | Select-String "\[ \]"

$applyMigrations = Read-Host "Aplicar migrações pendentes? (S/N)"
if ($applyMigrations -eq "S" -or $applyMigrations -eq "s") {
    Write-Host "Aplicando migrações..." -ForegroundColor Yellow
    python manage.py migrate --settings=sistema_rural.settings_producao
}

# 4. Coletar arquivos estáticos
Write-Host ""
Write-Host "Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput

# 5. Verificar configurações
Write-Host ""
Write-Host "Verificando configurações..." -ForegroundColor Yellow
python manage.py check --settings=sistema_rural.settings_producao --deploy

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "CORREÇÕES CONCLUÍDAS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Verifique os logs em logs/django.log ou /var/log/monpec/django.log"
Write-Host "2. Reinicie o servidor web (Apache/Nginx) ou o serviço Django"
Write-Host "3. Teste o acesso em http://monpec.com.br"
Write-Host ""
















