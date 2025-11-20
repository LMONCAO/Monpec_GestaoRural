# Script de Backup Completo do Sistema Monpec
# Cria backup de código fonte, banco de dados, arquivos estáticos e configurações

Write-Host "=== BACKUP COMPLETO DO SISTEMA MONPEC ===" -ForegroundColor Green
Write-Host ""

# Obter data e hora para nome do backup
$dataBackup = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$nomeBackup = "backup_monpec_$dataBackup"
$pastaBackup = ".\backups\$nomeBackup"

Write-Host "Criando pasta de backup: $pastaBackup" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $pastaBackup | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\codigo_fonte" | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\banco_dados" | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\estaticos" | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\configuracoes" | Out-Null

Write-Host ""
Write-Host "1. Copiando código fonte..." -ForegroundColor Cyan

# Código fonte - Django apps
Copy-Item -Path ".\gestao_rural" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force
Copy-Item -Path ".\monpec_clean" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\monpec_local" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\monpec_projetista_clean" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\sistema_rural" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\api" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force -ErrorAction SilentlyContinue

# Templates
Copy-Item -Path ".\templates" -Destination "$pastaBackup\codigo_fonte\" -Recurse -Force

# Arquivos Python na raiz
Get-ChildItem -Path "." -Filter "*.py" -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$pastaBackup\codigo_fonte\" -Force
}

# Arquivos de configuração do Django
Copy-Item -Path ".\manage.py" -Destination "$pastaBackup\codigo_fonte\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\settings.py" -Destination "$pastaBackup\codigo_fonte\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\urls.py" -Destination "$pastaBackup\codigo_fonte\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\wsgi.py" -Destination "$pastaBackup\codigo_fonte\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\requirements.txt" -Destination "$pastaBackup\codigo_fonte\" -Force -ErrorAction SilentlyContinue

Write-Host "   ✓ Código fonte copiado" -ForegroundColor Green

Write-Host ""
Write-Host "2. Copiando banco de dados..." -ForegroundColor Cyan

# Banco de dados SQLite
Copy-Item -Path ".\db.sqlite3" -Destination "$pastaBackup\banco_dados\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\db.sqlite3-shm" -Destination "$pastaBackup\banco_dados\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\db.sqlite3-wal" -Destination "$pastaBackup\banco_dados\" -Force -ErrorAction SilentlyContinue

Write-Host "   ✓ Banco de dados copiado" -ForegroundColor Green

Write-Host ""
Write-Host "3. Copiando arquivos estáticos..." -ForegroundColor Cyan

# Arquivos estáticos
if (Test-Path ".\static") {
    Copy-Item -Path ".\static" -Destination "$pastaBackup\estaticos\" -Recurse -Force
    Write-Host "   ✓ Arquivos estáticos copiados" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Pasta static não encontrada" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4. Copiando configurações..." -ForegroundColor Cyan

# Arquivos de configuração
Copy-Item -Path ".\vercel.json" -Destination "$pastaBackup\configuracoes\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\requirements*.txt" -Destination "$pastaBackup\configuracoes\" -Force -ErrorAction SilentlyContinue

Write-Host "   ✓ Configurações copiadas" -ForegroundColor Green

Write-Host ""
Write-Host "5. Criando arquivo de informações do backup..." -ForegroundColor Cyan

# Criar arquivo de informações
$infoBackup = @"
=== INFORMAÇÕES DO BACKUP ===
Data/Hora: $dataBackup
Nome: $nomeBackup

=== CONTEÚDO ===
- Código fonte completo (apps Django, templates, arquivos Python)
- Banco de dados SQLite
- Arquivos estáticos
- Configurações

=== RESTAURAÇÃO ===
Para restaurar este backup:
1. Copie os arquivos de volta para o diretório original
2. Execute: python manage.py migrate
3. Execute: python manage.py collectstatic

=== NOTAS ===
Este backup foi criado automaticamente antes de uma revisão completa do sistema.
"@

$infoBackup | Out-File -FilePath "$pastaBackup\INFO_BACKUP.txt" -Encoding UTF8

Write-Host "   ✓ Arquivo de informações criado" -ForegroundColor Green

Write-Host ""
Write-Host "=== BACKUP CONCLUÍDO COM SUCESSO ===" -ForegroundColor Green
Write-Host "Localização: $pastaBackup" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tamanho do backup:" -ForegroundColor Yellow
Get-ChildItem -Path $pastaBackup -Recurse | Measure-Object -Property Length -Sum | ForEach-Object {
    $tamanhoMB = [math]::Round($_.Sum / 1MB, 2)
    Write-Host "   $tamanhoMB MB" -ForegroundColor White
}
Write-Host ""

















