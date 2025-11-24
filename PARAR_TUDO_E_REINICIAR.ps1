# Script para PARAR TUDO e reiniciar servidor limpo
Write-Host "========================================" -ForegroundColor Red
Write-Host "  PARANDO TODOS OS PROCESSOS PYTHON" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Parar TODOS os processos Python de forma agressiva
Write-Host "Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "python"} | ForEach-Object {
    Write-Host "Parando processo: $($_.Id) - $($_.ProcessName)" -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 3

# Parar processos na porta 8000
Write-Host "`nParando processos na porta 8000..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $pids) {
    Write-Host "Parando processo $pid na porta 8000..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 3

# Verificar se está tudo parado
Write-Host "`nVerificando processos restantes..." -ForegroundColor Cyan
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -match "python"}
$portProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "AVISO: Ainda há processos Python rodando!" -ForegroundColor Red
    $pythonProcesses | ForEach-Object { Write-Host "  - PID: $($_.Id) - $($_.ProcessName)" -ForegroundColor Yellow }
} else {
    Write-Host "✅ Todos os processos Python foram parados!" -ForegroundColor Green
}

if ($portProcesses) {
    Write-Host "AVISO: Ainda há processos na porta 8000!" -ForegroundColor Red
} else {
    Write-Host "✅ Porta 8000 está livre!" -ForegroundColor Green
}

# Limpar cache
Write-Host "`nLimpando cache do Python..." -ForegroundColor Cyan
Get-ChildItem -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "✅ Cache limpo!" -ForegroundColor Green

# Iniciar servidor
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  INICIANDO SERVIDOR LIMPO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000

