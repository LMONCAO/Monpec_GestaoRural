# Script PowerShell para iniciar o sistema
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SISTEMA MONPEC - GESTAO RURAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Garantir execução a partir da raiz do projeto
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Determinar interpretador Python
$pythonPortable = Join-Path $scriptDir "python311\python.exe"
if (Test-Path $pythonPortable) {
    $pythonCmd = $pythonPortable
    Write-Host "   Usando Python portátil localizado em python311\python.exe" -ForegroundColor Green
} else {
    $pythonCmd = "python"
}

# Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "   $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: Python nao encontrado!" -ForegroundColor Red
    Write-Host "   Verifique se o Python está instalado ou se a pasta python311 existe." -ForegroundColor Red
    exit 1
}

# Verificar Django
Write-Host "[2/4] Verificando Django..." -ForegroundColor Yellow
try {
    & $pythonCmd -c "import django; print(f'Django {django.get_version()} OK')" 2>&1 |
        ForEach-Object { Write-Host "   $_" -ForegroundColor Green }
} catch {
    Write-Host "   AVISO: Verificando dependencias..." -ForegroundColor Yellow
}

# Verificar sistema
Write-Host "[3/4] Verificando sistema Django..." -ForegroundColor Yellow
& $pythonCmd manage.py check 2>&1 | ForEach-Object {
    if ($_ -match "System check identified") {
        Write-Host "   $_" -ForegroundColor Green
    } elseif ($_ -match "error|ERROR|Error") {
        Write-Host "   $_" -ForegroundColor Red
    } else {
        Write-Host "   $_" -ForegroundColor Gray
    }
}

# Iniciar servidor
Write-Host "[4/4] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servidor iniciando na porta 8000" -ForegroundColor Green
Write-Host "Acesse: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor em background e mostrar output
$job = Start-Job -ScriptBlock {
    param($projectDir, $pythonPath)
    Set-Location $projectDir
    & $pythonPath manage.py runserver 2>&1
} -ArgumentList $scriptDir, $pythonCmd

# Aguardar um pouco e verificar se iniciou
Start-Sleep -Seconds 3

# Verificar se o servidor está rodando
$porta = netstat -ano | Select-String ":8000"
if ($porta) {
    Write-Host "Servidor iniciado com sucesso!" -ForegroundColor Green
    Write-Host "Porta 8000 está ativa." -ForegroundColor Green
    Write-Host ""
    Write-Host "Mantendo processo em execucao..." -ForegroundColor Yellow
    Receive-Job -Job $job -Wait
} else {
    Write-Host "AVISO: Servidor pode nao ter iniciado corretamente." -ForegroundColor Yellow
    Write-Host "Verificando erros..." -ForegroundColor Yellow
    Receive-Job -Job $job
    Stop-Job -Job $job
    Remove-Job -Job $job
}
