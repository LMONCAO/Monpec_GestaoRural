# ========================================
# INSTALAR SERVIDOR PERMANENTE MONPEC DESENVOLVIMENTO
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALAR SERVIDOR PERMANENTE MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está executando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERRO] Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    pause
    exit
}

# Obter diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $projectDir "INICIAR_SISTEMA_CORRETO.bat"

if (-not (Test-Path $batFile)) {
    # Tentar arquivo alternativo
    $batFileAlt = Join-Path $projectDir "MONPEC DESENVOLVIMENTO.bat"
    if (Test-Path $batFileAlt) {
        $batFile = $batFileAlt
        Write-Host "[INFO] Usando arquivo alternativo: MONPEC DESENVOLVIMENTO.bat" -ForegroundColor Yellow
    } else {
        Write-Host "[ERRO] Arquivo 'INICIAR_SISTEMA_CORRETO.bat' ou 'MONPEC DESENVOLVIMENTO.bat' nao encontrado!" -ForegroundColor Red
        Write-Host "Certifique-se de que um dos arquivos existe em: $projectDir" -ForegroundColor Yellow
        pause
        exit
    }
}

Write-Host "[INFO] Diretorio do projeto: $projectDir" -ForegroundColor Green
Write-Host "[INFO] Arquivo BAT: $batFile" -ForegroundColor Green
Write-Host ""

# Parar tarefa existente se houver
$existingTask = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "[INFO] Parando tarefa existente..." -ForegroundColor Yellow
    Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
    Disable-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
    try {
        Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false -ErrorAction Stop
        Write-Host "[OK] Tarefa antiga removida" -ForegroundColor Green
    } catch {
        Write-Host "[AVISO] Nao foi possivel remover a tarefa automaticamente" -ForegroundColor Yellow
        Write-Host "[INFO] Execute manualmente como Administrador:" -ForegroundColor Yellow
        Write-Host "      schtasks /Delete /TN `"MONPEC_Servidor_Django`" /F" -ForegroundColor Gray
    }
    Start-Sleep -Seconds 2
}

# Parar processos Python
Write-Host "[INFO] Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Processos parados" -ForegroundColor Green
Write-Host ""

# Criar ação da tarefa
$action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $projectDir

# Criar trigger (iniciar quando o usuário fizer login)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Criar configurações da tarefa
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Criar principal (executar como usuário atual)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Registrar a tarefa
Write-Host "[INFO] Criando tarefa agendada..." -ForegroundColor Yellow
try {
    Register-ScheduledTask `
        -TaskName "MONPEC_Servidor_Django" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Servidor Django MONPEC - Desenvolvimento - Inicia automaticamente no login" `
        -Force | Out-Null
    
    Write-Host "[OK] Tarefa agendada criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    # Iniciar a tarefa agora
    Write-Host "[INFO] Iniciando servidor agora..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName "MONPEC_Servidor_Django"
    Start-Sleep -Seconds 3
    
    # Verificar se está rodando
    $taskInfo = Get-ScheduledTaskInfo -TaskName "MONPEC_Servidor_Django"
    if ($taskInfo.State -eq 'Running') {
        Write-Host "[OK] Servidor iniciado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Tarefa criada, mas nao esta rodando ainda" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[ERRO] Falha ao criar tarefa agendada: $_" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "O servidor MONPEC sera iniciado automaticamente:" -ForegroundColor White
Write-Host "  - Quando voce fizer login no Windows" -ForegroundColor Gray
Write-Host "  - Se o servidor parar, ele tentara reiniciar automaticamente" -ForegroundColor Gray
Write-Host ""
Write-Host "Configuracao:" -ForegroundColor White
Write-Host "  - Settings: sistema_rural.settings (DESENVOLVIMENTO)" -ForegroundColor Gray
Write-Host "  - URL: http://127.0.0.1:8000/" -ForegroundColor Gray
Write-Host ""
Write-Host "Para gerenciar a tarefa:" -ForegroundColor White
Write-Host "  - Abra o Agendador de Tarefas do Windows" -ForegroundColor Gray
Write-Host "  - Procure por: MONPEC_Servidor_Django" -ForegroundColor Gray
Write-Host ""
Write-Host "Para remover a tarefa permanente:" -ForegroundColor White
Write-Host "  - Execute: REMOVER_SERVIDOR_PERMANENTE_MONPEC.ps1" -ForegroundColor Gray
Write-Host ""

pause

