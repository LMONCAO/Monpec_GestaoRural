# ========================================
# OTIMIZAÇÃO RÁPIDA DO CURSOR
# Execute quando o Cursor estiver travando
# ========================================

Write-Host "Otimizando Cursor..." -ForegroundColor Cyan

# 1. Aumentar prioridade do Cursor
$cursorProcs = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursorProcs) {
    foreach ($proc in $cursorProcs) {
        try {
            $proc.PriorityClass = "High"
            Write-Host "✓ Prioridade do Cursor aumentada (PID: $($proc.Id))" -ForegroundColor Green
        } catch {
            Write-Host "⚠ Não foi possível alterar prioridade" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⚠ Cursor não está rodando" -ForegroundColor Yellow
}

# 2. Limpar cache do Cursor
$cachePaths = @(
    "$env:APPDATA\Cursor\Cache",
    "$env:APPDATA\Cursor\CachedData",
    "$env:APPDATA\Cursor\Code Cache",
    "$env:APPDATA\Cursor\GPUCache"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        try {
            Remove-Item "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "✓ Cache limpo: $path" -ForegroundColor Green
        } catch {
            # Ignorar erros (arquivos em uso)
        }
    }
}

# 3. Parar processos Python desnecessários (mantém apenas o servidor Django se estiver rodando)
$pythonProcs = Get-Process -Name "python*" -ErrorAction SilentlyContinue
$djangoRunning = $false
foreach ($proc in $pythonProcs) {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
    if ($cmdLine -like "*runserver*" -or $cmdLine -like "*manage.py*") {
        $djangoRunning = $true
        $proc.PriorityClass = "AboveNormal"
        Write-Host "✓ Servidor Django mantido (PID: $($proc.Id))" -ForegroundColor Green
    } else {
        Write-Host "⚠ Processo Python não relacionado encontrado (PID: $($proc.Id))" -ForegroundColor Yellow
    }
}

# 4. Liberar memória
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host ""
Write-Host "✓ Otimização concluída!" -ForegroundColor Green
Write-Host "Se o Cursor ainda estiver lento, tente reiniciá-lo." -ForegroundColor Yellow










