# Script de Restauração do Backup - Curral Dashboard
# Uso: .\RESTAURAR_BACKUP.ps1 [DATA_BACKUP]
# Exemplo: .\RESTAURAR_BACKUP.ps1 20251120_132137

param(
    [string]$dataBackup = ""
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupBase = Join-Path $scriptPath "backup_curral_refactor"

if ($dataBackup -eq "") {
    # Usar o backup mais recente
    $backupDir = Get-ChildItem -Path $backupBase -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $backupDir) {
        Write-Host "❌ Nenhum backup encontrado!" -ForegroundColor Red
        exit 1
    }
    $backupDir = $backupDir.FullName
} else {
    $backupDir = Join-Path $backupBase $dataBackup
    if (-not (Test-Path $backupDir)) {
        Write-Host "❌ Backup não encontrado: $backupDir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🔄 Restaurando backup de: $backupDir" -ForegroundColor Yellow

# Verificar se os arquivos de backup existem
$arquivos = @(
    "curral_dashboard_v2.html",
    "views_curral.py",
    "curral_dashboard_v2_simulacao_novo.js"
)

foreach ($arquivo in $arquivos) {
    $caminhoBackup = Join-Path $backupDir $arquivo
    if (-not (Test-Path $caminhoBackup)) {
        Write-Host "⚠️ Arquivo não encontrado no backup: $arquivo" -ForegroundColor Yellow
        continue
    }
}

# Restaurar template principal
$templateSrc = Join-Path $backupDir "curral_dashboard_v2.html"
$templateDest = "templates\gestao_rural\curral_dashboard_v2.html"
if (Test-Path $templateSrc) {
    Copy-Item -Path $templateSrc -Destination $templateDest -Force
    Write-Host "✅ Restaurado: $templateDest" -ForegroundColor Green
} else {
    Write-Host "⚠️ Template não encontrado no backup" -ForegroundColor Yellow
}

# Restaurar views
$viewsSrc = Join-Path $backupDir "views_curral.py"
$viewsDest = "gestao_rural\views_curral.py"
if (Test-Path $viewsSrc) {
    Copy-Item -Path $viewsSrc -Destination $viewsDest -Force
    Write-Host "✅ Restaurado: $viewsDest" -ForegroundColor Green
} else {
    Write-Host "⚠️ Views não encontradas no backup" -ForegroundColor Yellow
}

# Restaurar JavaScript
$jsSrc = Join-Path $backupDir "curral_dashboard_v2_simulacao_novo.js"
$jsDest = "static\gestao_rural\curral_dashboard_v2_simulacao_novo.js"
if (Test-Path $jsSrc) {
    Copy-Item -Path $jsSrc -Destination $jsDest -Force
    Write-Host "✅ Restaurado: $jsDest" -ForegroundColor Green
} else {
    Write-Host "⚠️ JavaScript não encontrado no backup" -ForegroundColor Yellow
}

# Restaurar CSS
$cssBackupDir = Join-Path $backupDir "css"
if (Test-Path $cssBackupDir) {
    $cssFiles = Get-ChildItem -Path $cssBackupDir -Filter "*.css"
    foreach ($css in $cssFiles) {
        $cssDest = "static\gestao_rural\css\$($css.Name)"
        Copy-Item -Path $css.FullName -Destination $cssDest -Force
        Write-Host "✅ Restaurado: $cssDest" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Restauração concluída!" -ForegroundColor Green
Write-Host "💡 Reinicie o servidor Django para aplicar as mudanças" -ForegroundColor Cyan
