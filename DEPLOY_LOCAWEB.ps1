# 🌐 SCRIPT DE DEPLOY PARA LOCAWEB - MONPEC.COM.BR
# PowerShell script para fazer deploy do sistema na Locaweb

param(
    [string]$IP = "10.1.1.234",
    [string]$Usuario = "ubuntu",
    [string]$ChaveSSH = "@MONPEC.key (1-28)",
    [switch]$ApenasUpload = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🌐 DEPLOY MONPEC PARA LOCAWEB" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Cores
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Blue }

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Error "❌ Arquivo manage.py não encontrado!"
    Write-Error "Execute este script na raiz do projeto Django."
    exit 1
}

# Verificar se SSH está disponível
$sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshAvailable) {
    Write-Error "❌ SSH não encontrado!"
    Write-Error "Instale o OpenSSH Client ou use o Git Bash."
    exit 1
}

# Verificar se SCP está disponível
$scpAvailable = Get-Command scp -ErrorAction SilentlyContinue
if (-not $scpAvailable) {
    Write-Error "❌ SCP não encontrado!"
    Write-Error "Instale o OpenSSH Client ou use o Git Bash."
    exit 1
}

Write-Step "Configurações do Deploy:"
Write-Host "  IP do Servidor: $IP" -ForegroundColor Gray
Write-Host "  Usuário: $Usuario" -ForegroundColor Gray
Write-Host "  Chave SSH: $ChaveSSH" -ForegroundColor Gray
Write-Host ""

# Verificar conexão com servidor
Write-Step "Verificando conexão com servidor..."
$ping = Test-Connection -ComputerName $IP -Count 1 -Quiet
if (-not $ping) {
    Write-Error "❌ Não foi possível conectar ao servidor $IP"
    Write-Info "Verifique se a VM está rodando no painel da Locaweb."
    exit 1
}
Write-Success "✅ Servidor acessível!"

# Preparar arquivos para upload
Write-Step "Preparando arquivos para upload..."

# Criar lista de arquivos a excluir
$excludePatterns = @(
    "*.pyc",
    "__pycache__",
    "*.log",
    ".git",
    "venv",
    "env",
    "db.sqlite3*",
    "*.shm",
    "*.wal",
    ".vscode",
    ".idea",
    "node_modules"
)

# Criar arquivo temporário com lista de exclusões
$excludeFile = [System.IO.Path]::GetTempFileName()
$excludePatterns | Out-File -FilePath $excludeFile -Encoding ASCII

Write-Success "✅ Arquivos preparados!"

# Opção 1: Upload via SCP
if ($ApenasUpload) {
    Write-Step "Fazendo upload dos arquivos..."
    
    # Construir comando SCP
    $scpCommand = "scp"
    if (Test-Path $ChaveSSH) {
        $scpCommand += " -i `"$ChaveSSH`""
    }
    $scpCommand += " -r"
    $scpCommand += " -o StrictHostKeyChecking=no"
    $scpCommand += " ."
    $scpCommand += " $Usuario@${IP}:/tmp/monpec_deploy/"
    
    Write-Info "Executando: $scpCommand"
    
    try {
        Invoke-Expression $scpCommand
        Write-Success "✅ Upload concluído!"
    } catch {
        Write-Error "❌ Erro no upload: $_"
        exit 1
    }
    
    Write-Host ""
    Write-Success "🎉 Upload concluído com sucesso!"
    Write-Host ""
    Write-Info "Próximos passos:"
    Write-Host "1. Conecte-se ao servidor: ssh $Usuario@$IP"
    Write-Host "2. Execute o script de configuração: sudo bash /tmp/monpec_deploy/configurar_locaweb.sh"
    Write-Host ""
    exit 0
}

# Opção 2: Deploy completo via SSH
Write-Step "Iniciando deploy completo..."

# Comando SSH para executar no servidor
$deployScript = @"
cd /tmp
rm -rf monpec_deploy
mkdir -p monpec_deploy
cd monpec_deploy
git clone https://github.com/LMONCAO/Monpec_projetista.git . || echo 'Git não disponível, usando upload'
"@

Write-Step "Conectando ao servidor e executando configuração..."

# Construir comando SSH
$sshCommand = "ssh"
if (Test-Path $ChaveSSH) {
    $sshCommand += " -i `"$ChaveSSH`""
}
$sshCommand += " -o StrictHostKeyChecking=no"
$sshCommand += " $Usuario@${IP}"
$sshCommand += " 'bash -s'"

Write-Info "Executando configuração no servidor..."

# Ler o script de configuração e enviar via SSH
$configScript = Get-Content "configurar_locaweb.sh" -Raw -ErrorAction SilentlyContinue
if ($configScript) {
    try {
        $configScript | & $sshCommand.Split(' ')
        Write-Success "✅ Deploy concluído!"
    } catch {
        Write-Error "❌ Erro no deploy: $_"
        Write-Info "Tente executar manualmente no servidor."
        exit 1
    }
} else {
    Write-Error "❌ Arquivo configurar_locaweb.sh não encontrado!"
    Write-Info "Use a opção -ApenasUpload para fazer upload manual."
    exit 1
}

Write-Host ""
Write-Success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host ""
Write-Info "🌐 Acesse o sistema em:"
Write-Host "   http://$IP" -ForegroundColor Cyan
Write-Host "   https://monpec.com.br (após configurar DNS)" -ForegroundColor Cyan
Write-Host ""
Write-Info "📊 Comandos úteis:"
Write-Host "   Verificar status: ssh $Usuario@$IP 'sudo systemctl status monpec'"
Write-Host "   Ver logs: ssh $Usuario@$IP 'sudo tail -f /var/log/monpec/django.log'"
Write-Host "   Reiniciar: ssh $Usuario@$IP 'sudo systemctl restart monpec'"
Write-Host ""






