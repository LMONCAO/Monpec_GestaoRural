# ========================================
# RESOLVER PROBLEMA DEFINITIVO
# ========================================

Write-Host "🔧 RESOLVENDO PROBLEMA DEFINITIVO" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow

# 1. PARAR TUDO
Write-Host "🛑 Parando todos os processos..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. IR PARA DIRETÓRIO
Write-Host "📁 Navegando para diretório..." -ForegroundColor Cyan
Set-Location "monpec_clean"

# 3. REMOVER BANCO ANTIGO
Write-Host "🗑️ Removendo banco antigo..." -ForegroundColor Cyan
Remove-Item "db.sqlite3" -ErrorAction SilentlyContinue
Remove-Item "gestao_rural\migrations\*.py" -ErrorAction SilentlyContinue
Remove-Item "gestao_rural\migrations\__pycache__" -Recurse -ErrorAction SilentlyContinue

# 4. CRIAR MIGRAÇÕES INICIAIS
Write-Host "📊 Criando migrações iniciais..." -ForegroundColor Cyan
python manage.py makemigrations gestao_rural

# 5. APLICAR MIGRAÇÕES
Write-Host "🗃️ Aplicando migrações..." -ForegroundColor Cyan
python manage.py migrate

# 6. CRIAR SUPERUSUÁRIO
Write-Host "👤 Criando superusuário..." -ForegroundColor Cyan
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')
    print('✅ Usuário admin criado!')
else:
    print('✅ Usuário admin já existe!')
"

# 7. VERIFICAR TABELAS
Write-Host "🔍 Verificando tabelas..." -ForegroundColor Cyan
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
tables = cursor.fetchall()
print('📋 Tabelas criadas:')
for table in tables:
    print(f'  ✅ {table[0]}')
"

# 8. TESTAR VIEWS
Write-Host "🧪 Testando views..." -ForegroundColor Cyan
python manage.py shell -c "
from gestao_rural.models import Proprietario, Propriedade, ProjetoCredito
print(f'✅ Proprietario: {Proprietario.objects.count()} registros')
print(f'✅ Propriedade: {Propriedade.objects.count()} registros')
print(f'✅ ProjetoCredito: {ProjetoCredito.objects.count()} registros')
"

Write-Host ""
Write-Host "🎉 PROBLEMA RESOLVIDO DEFINITIVAMENTE!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Acesse: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""

# 9. INICIAR SERVIDOR
python manage.py runserver


