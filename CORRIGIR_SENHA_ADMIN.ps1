# ========================================
# CORRIGIR SENHA DO ADMIN
# ========================================

Write-Host "🔧 CORRIGINDO SENHA DO ADMIN" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""

# Parar processos Python se estiverem rodando
Write-Host "🛑 Verificando processos Python..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Definir senha forte para admin (atende todos os requisitos)
# Não contém sequências comuns (123, abc, etc)
$NOVA_SENHA = "AdminMonpec2025!@"

Write-Host "🔑 Atualizando senha do usuário admin..." -ForegroundColor Cyan
Write-Host ""

# Atualizar ou criar usuário admin
$codigoPython = @"
from django.contrib.auth.models import User

# Verifica se o usuário admin existe
if User.objects.filter(username='admin').exists():
    usuario = User.objects.get(username='admin')
    usuario.set_password('$NOVA_SENHA')
    usuario.is_superuser = True
    usuario.is_staff = True
    usuario.is_active = True
    if not usuario.email:
        usuario.email = 'admin@monpec.com.br'
    usuario.save()
    print('✅ Senha do usuário admin atualizada com sucesso!')
else:
    # Cria novo usuário admin
    usuario = User.objects.create_superuser(
        username='admin',
        email='admin@monpec.com.br',
        password='$NOVA_SENHA'
    )
    print('✅ Usuário admin criado com sucesso!')

print()
print('=' * 60)
print('CREDENCIAIS DE ACESSO:')
print('=' * 60)
print('Usuário: admin')
print('Senha: $NOVA_SENHA')
print('=' * 60)
"@

python manage.py shell -c $codigoPython

Write-Host ""
Write-Host "✅ SENHA CORRIGIDA!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: $NOVA_SENHA" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ IMPORTANTE:" -ForegroundColor Yellow
Write-Host "A senha '123456' está bloqueada pelo sistema por questões de segurança." -ForegroundColor White
Write-Host "A nova senha atende a todos os requisitos de segurança." -ForegroundColor White
Write-Host ""

