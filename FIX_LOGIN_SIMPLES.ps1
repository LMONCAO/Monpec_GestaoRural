# ========================================
# FIX LOGIN SIMPLES
# ========================================

Write-Host "🔧 CORRIGINDO LOGIN SIMPLES" -ForegroundColor Green

# Parar processos Python
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Ir para diretório
Set-Location "monpec_clean"

# Criar superusuário
Write-Host "👤 Criando usuário admin..." -ForegroundColor Cyan
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Usuário já existe')"

Write-Host "✅ Usuário criado!" -ForegroundColor Green
Write-Host "🔑 Login: admin" -ForegroundColor White
Write-Host "🔑 Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Green

# Iniciar servidor
python manage.py runserver


