# Script de Backup Completo do Sistema MONPEC
# Data: $(Get-Date -Format "yyyy-MM-dd")

$ErrorActionPreference = "Stop"

# Configurações
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath
$BackupDir = Join-Path $ProjectRoot "backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETO DO SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar diretório de backup
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Host "[✓] Diretório de backup criado: $BackupDir" -ForegroundColor Green

# 1. Backup do Banco de Dados
Write-Host ""
Write-Host "[1/6] Fazendo backup do banco de dados..." -ForegroundColor Yellow
$DbBackupDir = "$BackupDir\database"
New-Item -ItemType Directory -Path $DbBackupDir -Force | Out-Null

# SQLite principal
if (Test-Path "$ProjectRoot\db.sqlite3") {
    Copy-Item "$ProjectRoot\db.sqlite3" "$DbBackupDir\db.sqlite3" -Force
    Write-Host "  [✓] db.sqlite3 copiado" -ForegroundColor Green
}

# Bancos de tenant
if (Test-Path "$ProjectRoot\tenants") {
    Copy-Item "$ProjectRoot\tenants\*" "$DbBackupDir\tenants\" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [✓] Bancos de tenant copiados" -ForegroundColor Green
}

# 2. Backup do Código Fonte
Write-Host ""
Write-Host "[2/6] Fazendo backup do código fonte..." -ForegroundColor Yellow
$CodeBackupDir = "$BackupDir\codigo"
New-Item -ItemType Directory -Path $CodeBackupDir -Force | Out-Null

# Diretórios importantes
$DirsToBackup = @(
    "gestao_rural",
    "sistema_rural",
    "templates",
    "static",
    "staticfiles",
    "scripts"
)

foreach ($dir in $DirsToBackup) {
    if (Test-Path "$ProjectRoot\$dir") {
        Copy-Item "$ProjectRoot\$dir" "$CodeBackupDir\$dir" -Recurse -Force -Exclude @("__pycache__", "*.pyc", ".git")
        Write-Host "  [✓] $dir copiado" -ForegroundColor Green
    }
}

# Arquivos importantes na raiz
$FilesToBackup = @(
    "manage.py",
    "requirements.txt",
    "requirements_producao.txt",
    "Dockerfile",
    ".env",
    ".env_producao",
    ".gcloudignore",
    ".gitignore"
)

foreach ($file in $FilesToBackup) {
    if (Test-Path "$ProjectRoot\$file") {
        Copy-Item "$ProjectRoot\$file" "$CodeBackupDir\$file" -Force
        Write-Host "  [✓] $file copiado" -ForegroundColor Green
    }
}

# 3. Backup de Configurações
Write-Host ""
Write-Host "[3/6] Fazendo backup de configurações..." -ForegroundColor Yellow
$ConfigBackupDir = "$BackupDir\config"
New-Item -ItemType Directory -Path $ConfigBackupDir -Force | Out-Null

# Configurações do deploy
if (Test-Path "$ProjectRoot\deploy") {
    Copy-Item "$ProjectRoot\deploy\*" "$ConfigBackupDir\deploy\" -Recurse -Force
    Write-Host "  [✓] Configurações de deploy copiadas" -ForegroundColor Green
}

# 4. Backup de Mídia (opcional - pode ser grande)
Write-Host ""
Write-Host "[4/6] Fazendo backup de arquivos de mídia..." -ForegroundColor Yellow
$MediaBackupDir = "$BackupDir\media"
if (Test-Path "$ProjectRoot\media") {
    New-Item -ItemType Directory -Path $MediaBackupDir -Force | Out-Null
    Copy-Item "$ProjectRoot\media\*" "$MediaBackupDir\" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [✓] Arquivos de mídia copiados" -ForegroundColor Green
} else {
    Write-Host "  [!] Diretório media não encontrado (pode estar vazio)" -ForegroundColor Yellow
}

# 5. Exportar dados do Django (dumpdata)
Write-Host ""
Write-Host "[5/6] Exportando dados do Django..." -ForegroundColor Yellow
Set-Location $ProjectRoot
try {
    python manage.py dumpdata --exclude auth.permission --exclude contenttypes > "$BackupDir\dumpdata.json" 2>&1
    Write-Host "  [✓] Dados exportados para dumpdata.json" -ForegroundColor Green
} catch {
    Write-Host "  [!] Erro ao exportar dados: $_" -ForegroundColor Yellow
}

# 6. Criar arquivo de informações do backup
Write-Host ""
Write-Host "[6/6] Criando arquivo de informações..." -ForegroundColor Yellow
$InfoContent = @"
BACKUP DO SISTEMA MONPEC
========================

Data do Backup: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Sistema: MONPEC - Monitor da Pecuária
Versão: 1.0

Estrutura:
- database/: Bancos de dados (SQLite)
- codigo/: Código fonte do sistema
- config/: Configurações de deploy
- media/: Arquivos de mídia
- dumpdata.json: Exportação completa dos dados Django

Para restaurar:
1. Copiar arquivos de volta para o projeto
2. Executar: python manage.py loaddata dumpdata.json
3. Executar: python manage.py migrate
4. Executar: python manage.py collectstatic

URLs principais documentadas em: BACKUP_COMPLETO.md
"@

$InfoContent | Out-File "$BackupDir\INFO_BACKUP.txt" -Encoding UTF8
Write-Host "  [✓] Arquivo de informações criado" -ForegroundColor Green

# Copiar documentação
if (Test-Path "$ProjectRoot\BACKUP_COMPLETO.md") {
    Copy-Item "$ProjectRoot\BACKUP_COMPLETO.md" "$BackupDir\BACKUP_COMPLETO.md" -Force
}

# Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Localização: $BackupDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Verificar o conteúdo do backup" -ForegroundColor White
Write-Host "2. Fazer upload para Google Cloud Storage (opcional)" -ForegroundColor White
Write-Host "3. Manter backup em local seguro" -ForegroundColor White
Write-Host ""

# Calcular tamanho do backup
$BackupSize = (Get-ChildItem -Path $BackupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Tamanho total do backup: $([math]::Round($BackupSize, 2)) MB" -ForegroundColor Cyan

