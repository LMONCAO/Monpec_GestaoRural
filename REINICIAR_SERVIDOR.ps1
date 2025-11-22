# ========================================
# REINICIAR SERVIDOR DJANGO
# ========================================

Write-Host "🔄 REINICIANDO SERVIDOR DJANGO" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Yellow
Write-Host ""

# Parar processos Python
Write-Host "🛑 Parando processos Python..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Limpar cache Python
Write-Host "🧹 Limpando cache Python..." -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Verificar URL
Write-Host "🔍 Verificando URL curral/v3..." -ForegroundColor Cyan
python311\python.exe verificar_url_curral_v3.py

Write-Host ""
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8000/propriedade/1/curral/v3/" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python311\python.exe manage.py runserver


