# ========================================
# SETUP VERSÃO DE DEMONSTRAÇÃO - MONPEC
# ========================================

Write-Host ""
Write-Host "🎯 CONFIGURANDO VERSÃO DE DEMONSTRAÇÃO" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""

# 1. Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ ERRO: Arquivo manage.py não encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script no diretório raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# 0. BACKUP AUTOMÁTICO ANTES DE CONFIGURAR DEMO
Write-Host "🔒 Fazendo backup automático do sistema..." -ForegroundColor Cyan
Write-Host "   (Isso garante que seus dados estão seguros)" -ForegroundColor Yellow

if (Test-Path ".\backup_antes_demo.ps1") {
    & ".\backup_antes_demo.ps1"
    Write-Host ""
    Write-Host "✅ Backup concluído! Continuando com setup da demo..." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠️  Script de backup não encontrado, mas continuando..." -ForegroundColor Yellow
    Write-Host "   Recomendado: Execute .\backup_antes_demo.ps1 manualmente antes" -ForegroundColor Yellow
    Write-Host ""
    $continuar = Read-Host "   Continuar mesmo assim? (S/N)"
    if ($continuar -ne "S" -and $continuar -ne "s") {
        Write-Host "   Setup cancelado pelo usuário." -ForegroundColor Yellow
        exit 0
    }
    Write-Host ""
}

# 2. Parar processos Python existentes
Write-Host "🛑 Parando processos Python existentes..." -ForegroundColor Cyan
$processosPython = Get-Process python -ErrorAction SilentlyContinue
if ($processosPython) {
    Write-Host "   ⚠️  Processos Python detectados. Parando..." -ForegroundColor Yellow
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Processos parados" -ForegroundColor Green
} else {
    Write-Host "   ✅ Nenhum processo Python rodando" -ForegroundColor Green
}

# 3. Executar migrações
Write-Host ""
Write-Host "📦 Executando migrações do banco de dados..." -ForegroundColor Cyan
python manage.py makemigrations
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Aviso: Algumas migrações podem já estar aplicadas" -ForegroundColor Yellow
}

python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO ao executar migrações!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Migrações executadas com sucesso!" -ForegroundColor Green

# 4. Criar usuário demo (SEGURANÇA: Usa get_or_create, não sobrescreve dados)
Write-Host ""
Write-Host "👤 Criando usuário de demonstração..." -ForegroundColor Cyan
Write-Host "   ℹ️  Se o usuário 'demo' já existir, apenas atualizará a senha" -ForegroundColor Yellow
python manage.py shell -c @"
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_superuser('demo', 'demo@monpec.com.br', 'demo123')
    user.first_name = 'Usuário'
    user.last_name = 'Demonstração'
    user.save()
    print('✅ Usuário demo criado com sucesso!')
    print('   Username: demo')
    print('   Senha: demo123')
else:
    print('ℹ️ Usuário demo já existe')
    user = User.objects.get(username='demo')
    user.set_password('demo123')
    user.save()
    print('✅ Senha do usuário demo atualizada!')
"@

# 5. Popular dados de demonstração (SEGURANÇA: Usa get_or_create, não sobrescreve)
Write-Host ""
Write-Host "📊 Populando dados de demonstração..." -ForegroundColor Cyan
Write-Host "   ℹ️  Os dados serão ADICIONADOS, não substituirão dados existentes!" -ForegroundColor Yellow
Write-Host "   ℹ️  O script usa get_or_create, então é seguro executar múltiplas vezes" -ForegroundColor Yellow
if (Test-Path "populate_test_data.py") {
    python populate_test_data.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dados de demonstração criados com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Aviso: Alguns dados podem já existir (isso é normal)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Arquivo populate_test_data.py não encontrado" -ForegroundColor Yellow
    Write-Host "   Pulando população de dados..." -ForegroundColor Yellow
}

# 6. Mensagem final
Write-Host ""
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "✅ VERSÃO DE DEMONSTRAÇÃO CONFIGURADA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 CREDENCIAIS DE ACESSO:" -ForegroundColor Cyan
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host "   Usuário: demo" -ForegroundColor White
Write-Host "   Senha: demo123" -ForegroundColor White
Write-Host ""
Write-Host "📊 DADOS DE DEMONSTRAÇÃO:" -ForegroundColor Cyan
Write-Host "   • Produtor: João Silva" -ForegroundColor White
Write-Host "   • Propriedade: Fazenda São José" -ForegroundColor White
Write-Host "   • Localização: Ribeirão Preto - SP" -ForegroundColor White
Write-Host "   • Área: 500 hectares" -ForegroundColor White
Write-Host ""
Write-Host "🚀 PARA INICIAR O SERVIDOR:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 PARA ACESSO REMOTO (rede local):" -ForegroundColor Cyan
Write-Host "   python manage.py runserver 0.0.0.0:8000" -ForegroundColor Yellow
Write-Host "   Depois acesse: http://[SEU_IP]:8000" -ForegroundColor White
Write-Host ""
Write-Host "💡 DICA: Para resetar os dados de demo, execute:" -ForegroundColor Cyan
Write-Host "   python manage.py flush --no-input" -ForegroundColor Yellow
Write-Host "   Depois execute este script novamente." -ForegroundColor White
Write-Host ""
Write-Host "🔒 SEGURANÇA:" -ForegroundColor Cyan
Write-Host "   • Seus dados originais estão seguros no backup" -ForegroundColor White
Write-Host "   • Os dados de demo foram ADICIONADOS, não substituídos" -ForegroundColor White
Write-Host "   • Para restaurar: Use o backup em .\backups\backup_antes_demo_*" -ForegroundColor White
Write-Host ""

# 7. Perguntar se deseja iniciar o servidor
$iniciar = Read-Host "Deseja iniciar o servidor agora? (S/N)"
if ($iniciar -eq "S" -or $iniciar -eq "s" -or $iniciar -eq "Y" -or $iniciar -eq "y") {
    Write-Host ""
    Write-Host "🚀 Iniciando servidor Django..." -ForegroundColor Green
    Write-Host "   Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    python manage.py runserver
}

