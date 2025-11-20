# === CORREÇÃO ERRO 502 VIA SSH - VERSÃO SIMPLES ===
Write-Host "🔥 CORREÇÃO DO ERRO 502 - MONPEC" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Yellow

$servidor = "191.252.225.106"
$chaveSSH = "C:\Users\lmonc\Downloads\monpecprojetista.key"

Write-Host "🚀 Tentando executar correção via SSH..." -ForegroundColor Cyan

# Comandos individuais
$cmd1 = "pkill -9 python"
$cmd2 = "cd /var/www/monpec.com.br"
$cmd3 = "cp gestao_rural/urls.py gestao_rural/urls.py.backup.backup"

Write-Host "📋 Executando comandos básicos..." -ForegroundColor Yellow

try {
    if (Test-Path $chaveSSH) {
        Write-Host "✅ Usando chave SSH encontrada" -ForegroundColor Green
        
        # Parar processos
        Write-Host "1. Parando processos Python..."
        & ssh -i $chaveSSH -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$servidor $cmd1
        
        # Fazer backup
        Write-Host "2. Fazendo backup..."
        & ssh -i $chaveSSH -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$servidor "$cmd2 && $cmd3"
        
        # Usar o script bash já criado
        Write-Host "3. Enviando script de correção..."
        & scp -i $chaveSSH -o StrictHostKeyChecking=no "corrigir_502_servidor.sh" root@${servidor}:/tmp/
        
        Write-Host "4. Executando correção completa..."
        & ssh -i $chaveSSH -o ConnectTimeout=30 -o StrictHostKeyChecking=no root@$servidor "chmod +x /tmp/corrigir_502_servidor.sh && bash /tmp/corrigir_502_servidor.sh"
        
    } else {
        Write-Host "⚠️  Tentando sem chave SSH..." -ForegroundColor Yellow
        
        # Parar processos
        Write-Host "1. Parando processos Python..."
        & ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no monpec@$servidor $cmd1
        
        # Fazer backup
        Write-Host "2. Fazendo backup..."
        & ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no monpec@$servidor "$cmd2 && $cmd3"
        
        # Usar o script bash já criado
        Write-Host "3. Enviando script de correção..."
        & scp -o StrictHostKeyChecking=no "corrigir_502_servidor.sh" monpec@${servidor}:/tmp/
        
        Write-Host "4. Executando correção completa..."
        & ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no monpec@$servidor "chmod +x /tmp/corrigir_502_servidor.sh && bash /tmp/corrigir_502_servidor.sh"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "" 
        Write-Host "✅ CORREÇÃO EXECUTADA!" -ForegroundColor Green
        Write-Host "🌐 Teste: http://191.252.225.106" -ForegroundColor Cyan
        Write-Host "🔑 Login: admin / 123456" -ForegroundColor White
    } else {
        Write-Host "❌ Erro durante execução (código: $LASTEXITCODE)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erro de conexão: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste final
Write-Host ""
Write-Host "🔍 TESTE FINAL..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://191.252.225.106" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ SISTEMA FUNCIONANDO! (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Sistema ainda não está respondendo" -ForegroundColor Red
    Write-Host "💡 Execute os comandos manualmente no Console Web da Locaweb" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Yellow
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

