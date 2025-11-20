# Script PowerShell para enviar arquivos para o servidor Locaweb
Write-Host "🚀 ENVIANDO ARQUIVOS PARA O SERVIDOR LOCAWEB" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Definir variáveis
$SSH_KEY = "C:\Users\lmonc\.ssh\monpec_locaweb_key"
$SERVER = "root@191.252.225.106"
$REMOTE_DIR = "/var/www/monpec.com.br"

# Função para executar comando SSH
function Invoke-SSHCommand {
    param($Command)
    ssh -i $SSH_KEY $SERVER $Command
}

# Função para enviar arquivo via SCP
function Send-File {
    param($LocalPath, $RemotePath)
    Write-Host "📤 Enviando: $LocalPath" -ForegroundColor Yellow
    scp -i $SSH_KEY $LocalPath "$SERVER`:$RemotePath"
}

# Função para enviar diretório via SCP
function Send-Directory {
    param($LocalPath, $RemotePath)
    Write-Host "📤 Enviando diretório: $LocalPath" -ForegroundColor Yellow
    scp -i $SSH_KEY -r $LocalPath "$SERVER`:$RemotePath"
}

Write-Host "1️⃣ Verificando conexão SSH..." -ForegroundColor Cyan
try {
    $result = Invoke-SSHCommand "echo 'Conexão SSH OK'"
    Write-Host "✅ Conexão SSH funcionando!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro na conexão SSH: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "2️⃣ Criando diretório no servidor..." -ForegroundColor Cyan
Invoke-SSHCommand "mkdir -p $REMOTE_DIR"

Write-Host "3️⃣ Enviando arquivos essenciais..." -ForegroundColor Cyan

# Enviar manage.py
Send-File "manage.py" "$REMOTE_DIR/"

# Enviar requirements.txt
Send-File "requirements.txt" "$REMOTE_DIR/"

# Enviar diretórios
Send-Directory "gestao_rural" "$REMOTE_DIR/"
Send-Directory "sistema_rural" "$REMOTE_DIR/"
Send-Directory "templates" "$REMOTE_DIR/"

# Enviar script de finalização
Send-File "finalizar_instalacao.sh" "/root/"

Write-Host "4️⃣ Verificando arquivos no servidor..." -ForegroundColor Cyan
$files = Invoke-SSHCommand "cd $REMOTE_DIR && ls -la"
Write-Host "Arquivos no servidor:" -ForegroundColor White
Write-Host $files -ForegroundColor White

Write-Host "5️⃣ Executando instalação..." -ForegroundColor Cyan
Invoke-SSHCommand "chmod +x /root/finalizar_instalacao.sh"
Invoke-SSHCommand "/root/finalizar_instalacao.sh"

Write-Host "6️⃣ Testando aplicação..." -ForegroundColor Cyan
Invoke-SSHCommand "cd $REMOTE_DIR && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao && python manage.py runserver 0.0.0.0:8000 &"

Write-Host "✅ INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "🌐 Acesse: http://191.252.225.106:8000" -ForegroundColor Yellow
Write-Host "👤 Login: admin / 123456" -ForegroundColor Yellow

