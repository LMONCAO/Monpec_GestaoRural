# ========================================
# EXECUTAR SISTEMA MONPEC COMPLETO - AUTOMÁTICO
# ========================================

Write-Host "🚀 EXECUTANDO SISTEMA MONPEC COMPLETO AUTOMATICAMENTE" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Yellow

# 1. EXECUTAR PRIMEIRO SCRIPT
Write-Host "📁 Criando estrutura base..." -ForegroundColor Cyan
& ".\desenvolver_sistema_completo.ps1"

# 2. EXECUTAR SEGUNDO SCRIPT
Write-Host "⚙️ Completando sistema..." -ForegroundColor Cyan
& ".\completar_sistema_automatico.ps1"

# 3. EXECUTAR TERCEIRO SCRIPT
Write-Host "🎨 Criando templates..." -ForegroundColor Cyan
& ".\criar_templates_modernos.ps1"

# 4. EXECUTAR COMANDOS DJANGO
Write-Host "🗄️ Configurando banco de dados..." -ForegroundColor Cyan
Set-Location "monpec_local"

# Fazer migrações
Write-Host "📊 Criando migrações..." -ForegroundColor White
python manage.py makemigrations

Write-Host "🗃️ Aplicando migrações..." -ForegroundColor White
python manage.py migrate

# Criar superusuário automaticamente
Write-Host "👤 Criando superusuário..." -ForegroundColor White
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')" | python manage.py shell

# Coletar arquivos estáticos
Write-Host "📦 Coletando arquivos estáticos..." -ForegroundColor White
python manage.py collectstatic --noinput

# 5. INICIAR SERVIDOR
Write-Host "🌐 Iniciando servidor..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 SISTEMA MONPEC COMPLETO CRIADO E EXECUTADO!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 INFORMAÇÕES DO SISTEMA:" -ForegroundColor Cyan
Write-Host "• URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🔧 FUNCIONALIDADES INCLUÍDAS:" -ForegroundColor Cyan
Write-Host "✅ Landing page moderna" -ForegroundColor Green
Write-Host "✅ Dashboard completo" -ForegroundColor Green
Write-Host "✅ Gestão de proprietários" -ForegroundColor Green
Write-Host "✅ Gestão de propriedades" -ForegroundColor Green
Write-Host "✅ Gestão de projetos" -ForegroundColor Green
Write-Host "✅ Módulos funcionais" -ForegroundColor Green
Write-Host "✅ Relatórios e exportação" -ForegroundColor Green
Write-Host "✅ Design responsivo" -ForegroundColor Green
Write-Host "✅ API endpoints" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor Django
python manage.py runserver


