# ========================================
# FORÇAR REINÍCIO COMPLETO DO SERVIDOR
# ========================================

Write-Host "🔄 FORÇANDO REINÍCIO COMPLETO" -ForegroundColor Red
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""

# Parar TODOS os processos Python
Write-Host "🛑 Parando TODOS os processos Python..." -ForegroundColor Cyan
$processos = Get-Process python -ErrorAction SilentlyContinue
if ($processos) {
    foreach ($proc in $processos) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
            Write-Host "  [OK] Processo $($proc.Id) parado" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Nao foi possivel parar processo $($proc.Id)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  [INFO] Nenhum processo Python encontrado" -ForegroundColor Gray
}

Start-Sleep -Seconds 3

# Limpar cache Python completamente
Write-Host ""
Write-Host "🧹 Limpando cache Python completamente..." -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  [OK] Cache limpo!" -ForegroundColor Green

# Verificar sintaxe do arquivo de URLs
Write-Host ""
Write-Host "🔍 Verificando sintaxe do arquivo de URLs..." -ForegroundColor Cyan
python311\python.exe -m py_compile gestao_rural/urls.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Sintaxe correta!" -ForegroundColor Green
} else {
    Write-Host "  [ERRO] Erro de sintaxe encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se a URL está definida
Write-Host ""
Write-Host "🔍 Verificando se a URL curral/v3 esta definida..." -ForegroundColor Cyan
$urlEncontrada = Select-String -Path "gestao_rural\urls.py" -Pattern "curral/v3" -Quiet
if ($urlEncontrada) {
    Write-Host "  [OK] URL encontrada no arquivo!" -ForegroundColor Green
} else {
    Write-Host "  [ERRO] URL NAO encontrada no arquivo!" -ForegroundColor Red
    exit 1
}

# Verificar view
Write-Host ""
Write-Host "🔍 Verificando se a view existe..." -ForegroundColor Cyan
python311\python.exe verificar_url_curral_v3.py

Write-Host ""
Write-Host "🚀 Iniciando servidor Django..." -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Acesse: http://localhost:8000/propriedade/1/curral/v3/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python311\python.exe manage.py runserver


