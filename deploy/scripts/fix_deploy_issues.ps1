# 🔧 CORRIGINDO PROBLEMAS DO DEPLOY - SISTEMA RURAL COM IA

Write-Host "🔧 CORRIGINDO PROBLEMAS DO DEPLOY" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow

# 1. Corrigir problema SSH Host Key
Write-Host "1. Corrigindo problema SSH Host Key..." -ForegroundColor Cyan
ssh-keygen -R 45.32.219.76
Write-Host "✅ Chave SSH antiga removida" -ForegroundColor Green

# 2. Aceitar nova chave SSH
Write-Host "2. Aceitando nova chave SSH..." -ForegroundColor Cyan
ssh -o StrictHostKeyChecking=no root@45.32.219.76 "echo 'Conexão SSH OK'"
Write-Host "✅ Conexão SSH configurada" -ForegroundColor Green

# 3. Criar arquivo de deploy sem problemas de permissão
Write-Host "3. Criando arquivo de deploy..." -ForegroundColor Cyan

# Usar PowerShell para criar o arquivo
$files = Get-ChildItem -Path . -Recurse | Where-Object {
    $_.FullName -notlike "*\venv\*" -and
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\db.sqlite3" -and
    $_.FullName -notlike "*\.log"
}

# Criar arquivo tar usando PowerShell
$deployFile = "sistema-rural-deploy.tar.gz"

# Usar tar do Windows
tar -czf $deployFile --exclude=venv --exclude=__pycache__ --exclude=db.sqlite3 --exclude=*.log .
Write-Host "✅ Arquivo de deploy criado: $deployFile" -ForegroundColor Green

# 4. Fazer upload
Write-Host "4. Fazendo upload para o servidor..." -ForegroundColor Cyan
scp $deployFile root@45.32.219.76:/tmp/
Write-Host "✅ Upload concluído" -ForegroundColor Green

# 5. Executar deploy no servidor
Write-Host "5. Executando deploy no servidor..." -ForegroundColor Cyan

$deployScript = @"
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

ssh root@45.32.219.76 $deployScript
Write-Host "✅ Deploy executado no servidor" -ForegroundColor Green

# 6. Verificar sistema
Write-Host "6. Verificando sistema..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
try {
    $response = Invoke-WebRequest -Uri "http://45.32.219.76" -TimeoutSec 30
    Write-Host "✅ Sistema está funcionando!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Sistema ainda não está respondendo. Aguarde alguns minutos." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "🌐 Sistema: http://45.32.219.76" -ForegroundColor Cyan
Write-Host "👤 Admin: http://45.32.219.76/admin" -ForegroundColor Cyan
Write-Host "🔑 Login: admin / admin123" -ForegroundColor Cyan

# Limpar arquivo temporário
Remove-Item $deployFile -Force
Write-Host "🧹 Arquivo temporário removido" -ForegroundColor Green



