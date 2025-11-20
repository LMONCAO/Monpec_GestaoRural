# ========================================
# INSTALAR SERVIDOR PERMANENTE MONPEC
# ========================================
# Este script configura o servidor Django para iniciar
# automaticamente com o Windows e manter rodando sempre.
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALAR SERVIDOR PERMANENTE MONPEC" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERRO] Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "MONPEC_Servidor_Django"
$scriptPath = Join-Path $scriptDir "SERVIDOR_PERMANENTE.ps1"

Write-Host "[1/4] Preparando script do servidor..." -ForegroundColor Yellow

# Criar script do servidor permanente se não existir
if (-not (Test-Path $scriptPath)) {
    Write-Host "[ERRO] Arquivo SERVIDOR_PERMANENTE.ps1 nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[2/4] Removendo tarefa existente (se houver)..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "[OK] Tarefa antiga removida" -ForegroundColor Green
}

Write-Host "[3/4] Criando tarefa agendada..." -ForegroundColor Yellow

# Criar ação - executar PowerShell oculto
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""

# Criar trigger - iniciar quando o usuário fizer login
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Criar trigger adicional - iniciar quando o sistema iniciar
$trigger2 = New-ScheduledTaskTrigger -AtStartup

# Configurações da tarefa
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -RunOnlyIfNetworkAvailable:$false

# Criar principal - executar quando o usuário atual fizer login
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Registrar tarefa
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($trigger, $trigger2) -Settings $settings -Principal $principal -Description "Servidor Django MONPEC - Inicia automaticamente e mantem rodando" | Out-Null

Write-Host "[OK] Tarefa agendada criada com sucesso!" -ForegroundColor Green

Write-Host "[4/4] Iniciando servidor agora..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 3

# Verificar se está rodando
$porta = netstat -ano | Select-String ":8000"
if ($porta) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SERVIDOR INSTALADO E RODANDO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "O servidor agora:" -ForegroundColor Cyan
    Write-Host "  [OK] Inicia automaticamente com o Windows" -ForegroundColor Green
    Write-Host "  [OK] Reinicia automaticamente se cair" -ForegroundColor Green
    Write-Host "  [OK] Mantem rodando mesmo fechando o terminal" -ForegroundColor Green
    Write-Host ""
    Write-Host "Porta 8000 esta ativa!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para remover o servico permanente:" -ForegroundColor Yellow
    Write-Host "  Execute: REMOVER_SERVIDOR_PERMANENTE.ps1" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[AVISO] Servidor pode nao ter iniciado ainda." -ForegroundColor Yellow
    Write-Host "Aguarde alguns segundos e verifique:" -ForegroundColor Yellow
    Write-Host "  http://localhost:8000" -ForegroundColor Cyan
}

Write-Host ""
pause
