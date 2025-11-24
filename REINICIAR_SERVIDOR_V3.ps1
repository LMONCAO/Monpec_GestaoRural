# Script para reiniciar servidor e garantir que URL V3 funcione
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REINICIANDO SERVIDOR PARA V3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Parar TODOS os processos Python
Write-Host "Parando todos os processos Python..." -ForegroundColor Yellow
taskkill /F /IM python.exe /T 2>$null
taskkill /F /IM pythonw.exe /T 2>$null
Start-Sleep -Seconds 3

# Verificar se a porta está livre
Write-Host "Verificando porta 8000..." -ForegroundColor Cyan
$portaEmUso = netstat -ano | findstr :8000 | findstr LISTENING
if ($portaEmUso) {
    Write-Host "AVISO: Ainda há processos na porta 8000!" -ForegroundColor Red
    $portaEmUso | ForEach-Object {
        $parts = $_ -split '\s+'
        $pid = $parts[-1]
        Write-Host "Parando processo $pid..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# Limpar cache do Python
Write-Host "Limpando cache do Python..." -ForegroundColor Cyan
Get-ChildItem -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Cache limpo!" -ForegroundColor Green

# Verificar se a URL está configurada
Write-Host "`nVerificando configuração da URL V3..." -ForegroundColor Cyan
$urlV3 = Select-String -Path "sistema_rural\urls.py" -Pattern "curral/v3" -Quiet
if ($urlV3) {
    Write-Host "✅ URL V3 encontrada em sistema_rural/urls.py" -ForegroundColor Green
} else {
    Write-Host "❌ ERRO: URL V3 não encontrada!" -ForegroundColor Red
    exit 1
}

# Testar URL com Django
Write-Host "`nTestando URL com Django..." -ForegroundColor Cyan
try {
    $teste = python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); import django; django.setup(); from django.urls import reverse; print(reverse('curral_dashboard_v3', args=[2]))" 2>&1
    if ($teste -match "/propriedade/2/curral/v3/") {
        Write-Host "✅ URL V3 está funcionando: $teste" -ForegroundColor Green
    } else {
        Write-Host "❌ ERRO: URL não está funcionando" -ForegroundColor Red
        Write-Host "Saída: $teste" -ForegroundColor Yellow
    }
} catch {
    Write-Host "AVISO: Não foi possível testar a URL" -ForegroundColor Yellow
}

# Iniciar servidor
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  INICIANDO SERVIDOR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000

