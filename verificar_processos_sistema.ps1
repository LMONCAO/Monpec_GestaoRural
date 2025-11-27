# Script para verificar processos Python e qual settings está sendo usado

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO PROCESSOS DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar processos Python
$processosPython = Get-Process | Where-Object {$_.ProcessName -like "*python*"}

if ($processosPython) {
    Write-Host "[INFO] Processos Python encontrados: $($processosPython.Count)" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($proc in $processosPython) {
        Write-Host "  PID: $($proc.Id) | Processo: $($proc.ProcessName) | Iniciado: $($proc.StartTime)" -ForegroundColor White
    }
} else {
    Write-Host "[INFO] Nenhum processo Python encontrado" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO PORTAS EM USO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar porta 8000
$porta8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($porta8000) {
    $pidPorta8000 = $porta8000 | Select-Object -ExpandProperty OwningProcess -Unique
    Write-Host "[INFO] Porta 8000 está em uso pelo PID: $pidPorta8000" -ForegroundColor Yellow
    
    $procPorta = Get-Process -Id $pidPorta8000 -ErrorAction SilentlyContinue
    if ($procPorta) {
        Write-Host "  Processo: $($procPorta.ProcessName) (PID: $pidPorta8000)" -ForegroundColor White
    }
} else {
    Write-Host "[INFO] Porta 8000 está livre" -ForegroundColor Green
}

# Verificar porta 6000 (se mencionada)
$porta6000 = Get-NetTCPConnection -LocalPort 6000 -ErrorAction SilentlyContinue
if ($porta6000) {
    $pidPorta6000 = $porta6000 | Select-Object -ExpandProperty OwningProcess -Unique
    Write-Host "[INFO] Porta 6000 está em uso pelo PID: $pidPorta6000" -ForegroundColor Yellow
    
    $procPorta = Get-Process -Id $pidPorta6000 -ErrorAction SilentlyContinue
    if ($procPorta) {
        Write-Host "  Processo: $($procPorta.ProcessName) (PID: $pidPorta6000)" -ForegroundColor White
    }
} else {
    Write-Host "[INFO] Porta 6000 está livre" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO SETTINGS EM USO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar qual settings está configurado por padrão
if (Test-Path "manage.py") {
    Write-Host "[INFO] Verificando manage.py..." -ForegroundColor Cyan
    $manageContent = Get-Content "manage.py" -Raw
    if ($manageContent -match "DJANGO_SETTINGS_MODULE.*=.*['""]([^'""]+)['""]") {
        $settingsPadrao = $matches[1]
        Write-Host "  Settings padrão no manage.py: $settingsPadrao" -ForegroundColor White
    }
}

# Verificar variável de ambiente
if ($env:DJANGO_ENV) {
    Write-Host "[INFO] Variável DJANGO_ENV definida: $env:DJANGO_ENV" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Variável DJANGO_ENV não está definida (usando padrão)" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ARQUIVOS DE SETTINGS DISPONÍVEIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "sistema_rural\settings.py") {
    Write-Host "  [OK] sistema_rural.settings (DESENVOLVIMENTO)" -ForegroundColor Green
} else {
    Write-Host "  [ERRO] sistema_rural.settings (NAO ENCONTRADO)" -ForegroundColor Red
}

if (Test-Path "sistema_rural\settings_producao.py") {
    Write-Host "  [OK] sistema_rural.settings_producao (PRODUCAO)" -ForegroundColor Yellow
} else {
    Write-Host "  [INFO] sistema_rural.settings_producao (NAO ENCONTRADO)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RECOMENDAÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para iniciar o sistema corretamente:" -ForegroundColor White
Write-Host "  .\iniciar_sistema_completo.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "O script irá:" -ForegroundColor White
Write-Host "  1. Parar todos os processos Python existentes" -ForegroundColor Gray
Write-Host "  2. Usar sistema_rural.settings (DESENVOLVIMENTO) por padrão" -ForegroundColor Gray
Write-Host "  3. Iniciar na porta 8000" -ForegroundColor Gray
Write-Host ""

