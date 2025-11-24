# Script para reiniciar o sistema completamente
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REINICIANDO SISTEMA COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Parar TODOS os processos Python
Write-Host "[1/5] Parando todos os processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "python"} | ForEach-Object {
    try {
        Stop-Process -Id $_.Id -Force -ErrorAction Stop
        Write-Host "  ✓ Processo $($_.Id) parado" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Processo $($_.Id) não pôde ser parado (pode estar protegido)" -ForegroundColor Yellow
    }
}
Start-Sleep -Seconds 5

# 2. Parar processos na porta 8000
Write-Host "`n[2/5] Parando processos na porta 8000..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $pids) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
        Write-Host "  ✓ Processo $pid parado" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Processo $pid não pôde ser parado" -ForegroundColor Yellow
    }
}
Start-Sleep -Seconds 3

# 3. Limpar cache
Write-Host "`n[3/5] Limpando cache do Python..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Cache limpo" -ForegroundColor Green

# 4. Verificar configuração
Write-Host "`n[4/5] Verificando configuração..." -ForegroundColor Yellow
python manage.py check | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Django check passou" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Django check encontrou problemas" -ForegroundColor Yellow
}

# Testar URL
$urlTest = python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); import django; django.setup(); from django.urls import reverse; print(reverse('curral_dashboard_v3', args=[2]))" 2>&1
if ($urlTest -match "/propriedade/2/curral/v3/") {
    Write-Host "  ✓ URL V3 está funcionando: $urlTest" -ForegroundColor Green
} else {
    Write-Host "  ❌ ERRO: URL V3 não está funcionando!" -ForegroundColor Red
    Write-Host "  Saída: $urlTest" -ForegroundColor Yellow
    exit 1
}

# 5. Verificar se porta está livre
Write-Host "`n[5/5] Verificando porta 8000..." -ForegroundColor Yellow
$portaEmUso = netstat -ano | findstr :8000 | findstr LISTENING
if ($portaEmUso) {
    Write-Host "  ⚠ AVISO: Ainda há processos na porta 8000!" -ForegroundColor Red
    Write-Host "  Você precisa fechar manualmente ou usar outra porta" -ForegroundColor Yellow
    Write-Host "`nProcessos encontrados:" -ForegroundColor Yellow
    $portaEmUso | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    Write-Host "`nTente fechar todas as janelas do PowerShell e executar novamente." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  ✓ Porta 8000 está livre" -ForegroundColor Green
}

# Iniciar servidor
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  INICIANDO SERVIDOR DJANGO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Sistema reiniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acesse:" -ForegroundColor Cyan
Write-Host "http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Dica: Limpe o cache do navegador (Ctrl+F5) se necessário" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000

