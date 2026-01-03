# Script para executar collectstatic e reiniciar servicos no servidor de producao
# Servidor: monpec.com.br (10.1.1.234)

param(
    [string]$IP = "10.1.1.234",
    [string]$Usuario = "ubuntu",
    [string]$ChaveSSH = ""
)

$ErrorActionPreference = "Stop"

Write-Host "Executando collectstatic e reiniciando servicos" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Step { Write-Host ">> $args" -ForegroundColor Blue }

Write-Step "Verificando conexao com servidor..."
$ping = Test-Connection -ComputerName $IP -Count 1 -Quiet
if (-not $ping) {
    Write-Error "Nao foi possivel conectar ao servidor $IP"
    Write-Info "Verifique se a VM esta rodando."
    exit 1
}
Write-Success "Servidor acessivel!"

$sshCommand = "ssh"
if ($ChaveSSH -and (Test-Path $ChaveSSH)) {
    $sshCommand += " -i `"$ChaveSSH`""
}
$sshCommand += " -o StrictHostKeyChecking=no"
$sshCommand += " $Usuario@${IP}"

$serverScript = @'
cd /var/www/monpec.com.br || cd ~/Monpec_GestaoRural || exit 1

echo "Executando collectstatic..."
python3 manage.py collectstatic --noinput --clear --settings=sistema_rural.settings_producao

if [ $? -eq 0 ]; then
    echo "collectstatic executado com sucesso!"
    
    echo ""
    echo "Reiniciando servicos..."
    
    if sudo systemctl list-units --type=service | grep -q gunicorn; then
        echo "Reiniciando gunicorn..."
        sudo systemctl restart gunicorn
    fi
    
    if sudo systemctl list-units --type=service | grep -q nginx; then
        echo "Reiniciando nginx..."
        sudo systemctl restart nginx
    fi
    
    if sudo systemctl list-units --type=service | grep -q monpec; then
        echo "Reiniciando servico monpec..."
        sudo systemctl restart monpec
    fi
    
    echo ""
    echo "Servicos reiniciados!"
    echo ""
    echo "Verificando se as imagens foram coletadas:"
    ls -lh /var/www/monpec.com.br/static/site/*.jpeg 2>/dev/null || echo "Imagens nao encontradas em /var/www/monpec.com.br/static/site/"
    ls -lh staticfiles/site/*.jpeg 2>/dev/null || echo "Imagens nao encontradas em staticfiles/site/"
    
else
    echo "Erro ao executar collectstatic!"
    exit 1
fi
'@

Write-Step "Conectando ao servidor e executando comandos..."
Write-Info "IP: $IP"
Write-Info "Usuario: $Usuario"
Write-Host ""

try {
    $serverScript | & $sshCommand.Split(' ')
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Success "Comandos executados com sucesso no servidor!"
        Write-Host ""
        Write-Info "Verifique o site em:"
        Write-Host "   https://monpec.com.br" -ForegroundColor Cyan
        Write-Host ""
        Write-Info "Teste as imagens diretamente:"
        Write-Host "   https://monpec.com.br/static/site/foto1.jpeg" -ForegroundColor Cyan
        Write-Host "   https://monpec.com.br/static/site/foto2.jpeg" -ForegroundColor Cyan
    } else {
        Write-Error "Erro ao executar comandos no servidor!"
        Write-Info "Tente executar manualmente via SSH:"
        Write-Host "   ssh $Usuario@$IP" -ForegroundColor Yellow
    }
} catch {
    Write-Error "Erro na conexao SSH: $_"
    Write-Info ""
    Write-Info "Execute manualmente no servidor:"
    Write-Host "   ssh $Usuario@$IP" -ForegroundColor Yellow
    Write-Host "   cd /var/www/monpec.com.br" -ForegroundColor Yellow
    Write-Host "   python3 manage.py collectstatic --noinput --clear --settings=sistema_rural.settings_producao" -ForegroundColor Yellow
    Write-Host "   sudo systemctl restart gunicorn" -ForegroundColor Yellow
    Write-Host "   sudo systemctl restart nginx" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

