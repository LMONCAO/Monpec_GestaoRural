# Script de Otimizacao Completa - Versao Simplificada
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OTIMIZACAO COMPLETA DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se e admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# 1. Parar processos desnecessarios
Write-Host "[1/6] Parando processos desnecessarios..." -ForegroundColor Green
$procs = @("Teams", "Skype", "Discord", "Spotify", "Steam", "OneDrive", "Dropbox")
foreach ($p in $procs) {
    Get-Process -Name $p -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
Write-Host "[OK] Processos parados" -ForegroundColor Gray

# 2. Configurar plano de energia
Write-Host "[2/6] Configurando plano de energia..." -ForegroundColor Green
try {
    powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e 2>$null
    powercfg /change monitor-timeout-ac 0
    powercfg /change disk-timeout-ac 0
    Write-Host "[OK] Plano de energia configurado" -ForegroundColor Gray
} catch {
    Write-Host "[AVISO] Algumas configuracoes podem precisar de admin" -ForegroundColor Yellow
}

# 3. Limpar cache
Write-Host "[3/6] Limpando cache..." -ForegroundColor Green
try {
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Cursor\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Cursor\CachedData\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Cache limpo" -ForegroundColor Gray
} catch {
    Write-Host "[AVISO] Alguns arquivos podem estar em uso" -ForegroundColor Yellow
}

# 4. Otimizar prioridades
Write-Host "[4/6] Otimizando prioridades de processo..." -ForegroundColor Green
try {
    $c = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
    foreach ($p in $c) { $p.PriorityClass = "High" }
    $py = Get-Process -Name "python*" -ErrorAction SilentlyContinue
    foreach ($p in $py) { $p.PriorityClass = "AboveNormal" }
    Write-Host "[OK] Prioridades otimizadas" -ForegroundColor Gray
} catch {
    Write-Host "[AVISO] Erro ao ajustar prioridades" -ForegroundColor Yellow
}

# 5. Verificar memoria
Write-Host "[5/6] Verificando memoria..." -ForegroundColor Green
try {
    $ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    Write-Host "[INFO] RAM: $([math]::Round($ram, 2)) GB" -ForegroundColor Gray
    if ($ram -lt 8) {
        Write-Host "[ATENCAO] RAM abaixo do recomendado (8GB)" -ForegroundColor Red
    }
} catch {
    Write-Host "[AVISO] Nao foi possivel verificar memoria" -ForegroundColor Yellow
}

# 6. Verificar disco
Write-Host "[6/6] Verificando disco..." -ForegroundColor Green
try {
    $d = Get-PSDrive C
    $free = [math]::Round($d.Free / 1GB, 2)
    $total = [math]::Round(($d.Free + $d.Used) / 1GB, 2)
    $percent = [math]::Round(($d.Free / ($d.Free + $d.Used)) * 100, 1)
    Write-Host "[INFO] Disco C: $free GB livres de $total GB ($percent%)" -ForegroundColor Gray
    if ($percent -lt 10) {
        Write-Host "[ATENCAO] Pouco espaco livre!" -ForegroundColor Red
    }
} catch {
    Write-Host "[AVISO] Erro ao verificar disco" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OTIMIZACAO CONCLUIDA!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Recomendacoes:" -ForegroundColor Yellow
Write-Host "  1. Feche aplicacoes que nao esta usando" -ForegroundColor White
Write-Host "  2. Desabilite extensoes desnecessarias no Cursor" -ForegroundColor White
Write-Host "  3. Use .cursorignore para ignorar arquivos grandes" -ForegroundColor White
Write-Host "  4. Reinicie o computador se possivel" -ForegroundColor White
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")




























