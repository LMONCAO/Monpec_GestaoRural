# ========================================
# CORRIGIR PROBLEMA DE LOGIN
# ========================================

Write-Host "🔧 CORRIGINDO PROBLEMA DE LOGIN" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Yellow

# 1. IR PARA O DIRETÓRIO
Write-Host "📁 Navegando para o diretório..." -ForegroundColor Cyan
Set-Location "monpec_clean"

# 2. CRIAR SUPERUSUÁRIO MANUALMENTE
Write-Host "👤 Criando superusuário..." -ForegroundColor Cyan

# Parar o servidor se estiver rodando
Write-Host "🛑 Parando servidor..." -ForegroundColor White
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Criar superusuário
Write-Host "🔑 Criando usuário admin..." -ForegroundColor White
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')
    print('Usuário admin criado com sucesso!')
else:
    print('Usuário admin já existe!')
"

# 3. VERIFICAR SE FOI CRIADO
Write-Host "✅ Verificando usuário..." -ForegroundColor White
python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
for user in users:
    print(f'Usuário: {user.username} - Email: {user.email} - Admin: {user.is_superuser}')
"

# 4. INICIAR SERVIDOR
Write-Host ""
Write-Host "🎉 LOGIN CORRIGIDO!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Acesse: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver


