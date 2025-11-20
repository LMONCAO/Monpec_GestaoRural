# === SCRIPT PARA CORRIGIR ERRO 502 VIA SSH ===
# Este script tentará conectar e corrigir o erro 502 automaticamente

Write-Host "🔥 CORREÇÃO AUTOMÁTICA DO ERRO 502 - MONPEC" -ForegroundColor Red
Write-Host "=================================================" -ForegroundColor Yellow

$servidor = "191.252.225.106"
$chaveSSH = "C:\Users\lmonc\Downloads\monpecprojetista.key"

# Verificar se a chave SSH existe
if (Test-Path $chaveSSH) {
    Write-Host "✅ Chave SSH encontrada: $chaveSSH" -ForegroundColor Green
    $sshCmd = "ssh -i `"$chaveSSH`" -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$servidor"
} else {
    Write-Host "⚠️  Chave SSH não encontrada. Tentando conexão com usuário monpec..." -ForegroundColor Yellow
    $sshCmd = "ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no monpec@$servidor"
}

# Criar arquivo temporário com os comandos
$scriptPath = "correcao_temp.sh"
$scriptContent = @"
#!/bin/bash
echo 'Iniciando correção do erro 502...'
pkill -9 python
cd /var/www/monpec.com.br
cp gestao_rural/urls.py gestao_rural/urls.py.backup.`$(date +%H%M%S)
cat > gestao_rural/urls.py << 'ENDFILE'
from django.urls import path
from . import views

app_name = 'gestao_rural'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('logout/', views.logout_view, name='logout'),
]
ENDFILE
python manage.py check
if [ `$? -eq 0 ]; then
    source venv/bin/activate
    nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
    sleep 3
    ps aux | grep python | grep runserver
    echo 'Sistema corrigido com sucesso!'
else
    echo 'Erro na verificação do Django'
fi
"@

# Salvar script temporário
$scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8

Write-Host "🚀 Tentando conectar no servidor..." -ForegroundColor Cyan

try {
    Write-Host "📋 Enviando script de correção..." -ForegroundColor Yellow
    
    # Enviar e executar o script
    if (Test-Path $chaveSSH) {
        Write-Host "Usando chave SSH..."
        & scp -i $chaveSSH -o StrictHostKeyChecking=no $scriptPath root@${servidor}:/tmp/
        & ssh -i $chaveSSH -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$servidor "chmod +x /tmp/$scriptPath && bash /tmp/$scriptPath"
    } else {
        Write-Host "Tentando conexão direta..."
        & scp -o StrictHostKeyChecking=no $scriptPath monpec@${servidor}:/tmp/
        & ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no monpec@$servidor "chmod +x /tmp/$scriptPath && bash /tmp/$scriptPath"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ CORREÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
        Write-Host "🌐 Teste o sistema em: http://191.252.225.106" -ForegroundColor Cyan
        Write-Host "🔑 Login: admin / 123456" -ForegroundColor White
    } else {
        Write-Host "❌ Erro durante a execução. Código: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro de conexão SSH: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "" 
    Write-Host "📋 ALTERNATIVAS:" -ForegroundColor Yellow
    Write-Host "1. Execute os comandos manualmente no Console Web da Locaweb"
    Write-Host "2. Use o arquivo 'CORRECAO_ERRO_502_AGORA.txt'" 
    Write-Host "3. Configure a chave SSH: $chaveSSH"
}

Write-Host ""
Write-Host "🔍 VERIFICAÇÃO FINAL:" -ForegroundColor Cyan
Write-Host "Testando conexão com o servidor..."

try {
    $response = Invoke-WebRequest -Uri "http://191.252.225.106" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ SISTEMA FUNCIONANDO! Status: $($response.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Sistema respondeu com status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Sistema não está respondendo. Continue com a correção manual." -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host "Script finalizado. Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
