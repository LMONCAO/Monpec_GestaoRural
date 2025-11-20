# ========================================
# CORRIGIR PROBLEMA DO BANCO DE DADOS
# ========================================

Write-Host "🗄️ CORRIGINDO PROBLEMA DO BANCO DE DADOS" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Yellow

# 1. PARAR SERVIDOR
Write-Host "🛑 Parando servidor..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. IR PARA DIRETÓRIO
Write-Host "📁 Navegando para diretório..." -ForegroundColor Cyan
Set-Location "monpec_clean"

# 3. CRIAR MIGRAÇÕES
Write-Host "📊 Criando migrações..." -ForegroundColor Cyan
python manage.py makemigrations

# 4. APLICAR MIGRAÇÕES
Write-Host "🗃️ Aplicando migrações..." -ForegroundColor Cyan
python manage.py migrate

# 5. CRIAR SUPERUSUÁRIO
Write-Host "👤 Criando superusuário..." -ForegroundColor Cyan
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')
    print('✅ Usuário admin criado com sucesso!')
else:
    print('✅ Usuário admin já existe!')
"

# 6. VERIFICAR TABELAS
Write-Host "🔍 Verificando tabelas criadas..." -ForegroundColor Cyan
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
tables = cursor.fetchall()
print('📋 Tabelas criadas:')
for table in tables:
    print(f'  - {table[0]}')
"

Write-Host ""
Write-Host "🎉 PROBLEMA RESOLVIDO!" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Acesse: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""

# 7. INICIAR SERVIDOR
python manage.py runserver


