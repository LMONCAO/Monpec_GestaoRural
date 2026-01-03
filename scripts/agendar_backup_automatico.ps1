# Script para agendar backup automático diário no Windows
# Configura Tarefa Agendada do Windows para fazer backup automático todos os dias

Write-Host "📅 Configurando backup automático diário no Windows..." -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos na raiz do projeto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erro: Execute este script na raiz do projeto Django" -ForegroundColor Red
    exit 1
}

# Obter caminho absoluto do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackupScript = Join-Path $ScriptDir "backup_automatico_integrado.ps1"

# Verificar se Python está no PATH
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "❌ Erro: Python não encontrado no PATH" -ForegroundColor Red
    exit 1
}

# Nome da tarefa
$TaskName = "MonPEC_Backup_Automatico"

# Verificar se tarefa já existe
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "⚠️  Tarefa já existe. Removendo versão anterior..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Criar ação (executar script PowerShell)
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`" completo true"

# Criar trigger (diariamente às 02:00)
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00"

# Criar configurações
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Criar principal (executar mesmo quando usuário não estiver logado)
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

# Registrar tarefa
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Backup automático diário do sistema MonPEC - Backup completo comprimido às 02:00" | Out-Null

Write-Host "✅ Backup automático configurado!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Detalhes:" -ForegroundColor Cyan
Write-Host "   - Nome da Tarefa: $TaskName"
Write-Host "   - Horário: Todos os dias às 02:00"
Write-Host "   - Tipo: Backup completo comprimido"
Write-Host "   - Retenção: 7 dias"
Write-Host ""
Write-Host "Para verificar:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "Para remover:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
Write-Host ""
Write-Host "Para executar manualmente:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName $TaskName"








