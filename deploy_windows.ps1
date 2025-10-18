# 🚀 SCRIPT DE DEPLOY PARA WINDOWS - SISTEMA RURAL COM IA
# Servidor: 45.32.219.76

Write-Host "🚀 INICIANDO DEPLOY DO SISTEMA RURAL COM IA" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 1. Corrigir problema SSH Host Key
Write-Host "🔑 Corrigindo problema SSH Host Key..." -ForegroundColor Yellow
try {
    ssh-keygen -R 45.32.219.76
    Write-Host "✅ Chave SSH antiga removida" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Aviso: Erro ao remover chave SSH antiga" -ForegroundColor Yellow
}

# 2. Testar conexão SSH
Write-Host "🔌 Testando conexão SSH..." -ForegroundColor Yellow
try {
    ssh -o StrictHostKeyChecking=no root@45.32.219.76 "echo 'Conexão SSH OK'"
    Write-Host "✅ Conexão SSH funcionando" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro na conexão SSH. Verifique se o servidor está online." -ForegroundColor Red
    exit 1
}

# 3. Criar arquivo tar sem problemas de permissão
Write-Host "📦 Criando arquivo de deploy..." -ForegroundColor Yellow

# Criar lista de arquivos para incluir
$filesToInclude = @(
    "manage.py",
    "requirements.txt",
    "gestao_rural",
    "sistema_rural",
    "templates",
    "static",
    "*.py",
    "*.md",
    "*.sh",
    "*.ps1",
    "*.env*"
)

# Criar arquivo de deploy
$deployFile = "sistema-rural-deploy.tar.gz"

try {
    # Usar tar do Windows 10/11
    tar -czf $deployFile --exclude=venv --exclude=__pycache__ --exclude=db.sqlite3 --exclude=*.log .
    Write-Host "✅ Arquivo de deploy criado: $deployFile" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao criar arquivo de deploy" -ForegroundColor Red
    exit 1
}

# 4. Fazer upload para o servidor
Write-Host "📤 Fazendo upload para o servidor..." -ForegroundColor Yellow
try {
    scp $deployFile root@45.32.219.76:/tmp/
    Write-Host "✅ Upload concluído" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro no upload" -ForegroundColor Red
    exit 1
}

# 5. Executar deploy no servidor
Write-Host "🚀 Executando deploy no servidor..." -ForegroundColor Yellow

$deployCommands = @"
# Extrair arquivos
cd /tmp
tar -xzf sistema-rural-deploy.tar.gz -C /home/django/sistema-rural/

# Configurar permissões
chown -R django:django /home/django/sistema-rural

# Executar deploy
cd /home/django/sistema-rural
chmod +x deploy_automatico.sh
./deploy_automatico.sh
"@

try {
    ssh root@45.32.219.76 $deployCommands
    Write-Host "✅ Deploy executado no servidor" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro no deploy do servidor" -ForegroundColor Red
    exit 1
}

# 6. Verificar se o sistema está funcionando
Write-Host "🔍 Verificando se o sistema está funcionando..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://45.32.219.76" -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Sistema está funcionando!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Sistema respondeu com código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Sistema não está respondendo ainda. Aguarde alguns minutos." -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "🌐 Sistema: http://45.32.219.76" -ForegroundColor Cyan
Write-Host "👤 Admin: http://45.32.219.76/admin" -ForegroundColor Cyan
Write-Host "🔑 Login: admin / admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Comandos úteis:" -ForegroundColor Yellow
Write-Host "• Ver logs: ssh root@45.32.219.76 'journalctl -u sistema-rural -f'" -ForegroundColor White
Write-Host "• Reiniciar: ssh root@45.32.219.76 'systemctl restart sistema-rural'" -ForegroundColor White
Write-Host "• Status: ssh root@45.32.219.76 'systemctl status sistema-rural'" -ForegroundColor White

# Limpar arquivo temporário
Remove-Item $deployFile -Force
Write-Host "🧹 Arquivo temporário removido" -ForegroundColor Green



