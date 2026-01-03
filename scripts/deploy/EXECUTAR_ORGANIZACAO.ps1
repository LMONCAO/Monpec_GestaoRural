# Script para organizar arquivos do projeto
# Execute este script no diretório raiz do projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ORGANIZAÇÃO DO PROJETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$root = Get-Location
Write-Host "Diretório: $root" -ForegroundColor Yellow

# Verificar se estamos no diretório correto
if (-not (Test-Path "manage.py") -and -not (Test-Path "sistema_rural")) {
    Write-Host "ERRO: Execute este script na raiz do projeto Django!" -ForegroundColor Red
    exit 1
}

# Criar estrutura de pastas
$folders = @(
    "docs",
    "temp",
    "scripts\deploy",
    "scripts\admin",
    "scripts\correcoes",
    "scripts\utilitarios",
    "scripts\configuracao",
    "scripts\backup",
    "deploy"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "✓ Criada: $folder" -ForegroundColor Green
    }
}

$stats = @{
    md = 0
    sh = 0
    ps1 = 0
    bat = 0
    py = 0
    txt = 0
}

# Arquivos que devem permanecer na raiz
$keepInRoot = @(
    "manage.py",
    "requirements.txt",
    "Dockerfile",
    "Dockerfile.prod",
    ".gitignore",
    "app.yaml",
    "build-config.yaml",
    "cloudbuild-config.yaml",
    "entrypoint.sh",
    "EXECUTAR_ORGANIZACAO.ps1",
    "_organizar_agora.py",
    "organizar_projeto_completo.py",
    "organizar_projeto.ps1"
)

function Get-ScriptCategory {
    param($name)
    $n = $name.ToLower()
    
    if ($n -match "deploy|atualizar|aplicar_migracoes|cloud|gcp|google") { return "scripts\deploy" }
    if ($n -match "admin|criar_admin|superuser") { return "scripts\admin" }
    if ($n -match "corrigir|correcao|fix|solucao") { return "scripts\correcoes" }
    if ($n -match "configurar|config|setup") { return "scripts\configuracao" }
    if ($n -match "backup|exportar|importar") { return "scripts\backup" }
    return "scripts\deploy"
}

# 1. Mover .md
Write-Host "`n1. Movendo arquivos .md..." -ForegroundColor Yellow
Get-ChildItem -Path $root -Filter "*.md" -File | Where-Object { $keepInRoot -notcontains $_.Name } | ForEach-Object {
    $dest = Join-Path "docs" $_.Name
    if (Test-Path $dest) {
        $counter = 1
        $base = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $ext = $_.Extension
        while (Test-Path $dest) {
            $dest = Join-Path "docs" "${base}_${counter}${ext}"
            $counter++
        }
    }
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Host "  ✓ $($_.Name) -> docs/" -ForegroundColor Gray
    $stats.md++
}

# 2. Mover scripts
Write-Host "`n2. Movendo scripts..." -ForegroundColor Yellow
foreach ($ext in @(".sh", ".ps1", ".bat")) {
    Get-ChildItem -Path $root -Filter "*${ext}" -File | Where-Object { $keepInRoot -notcontains $_.Name } | ForEach-Object {
        $category = Get-ScriptCategory $_.Name
        $dest = Join-Path $category $_.Name
        
        if (Test-Path $dest) {
            $counter = 1
            $base = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
            while (Test-Path $dest) {
                $dest = Join-Path $category "${base}_${counter}${ext}"
                $counter++
            }
        }
        
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  ✓ $($_.Name) -> $category/" -ForegroundColor Gray
        $stats[$ext.TrimStart('.')]++
    }
}

# 3. Mover .py utilitários
Write-Host "`n3. Movendo scripts Python utilitários..." -ForegroundColor Yellow
$djangoDirs = @("gestao_rural", "sistema_rural", "api", "templates", "static")
Get-ChildItem -Path $root -Filter "*.py" -File | Where-Object { 
    $keepInRoot -notcontains $_.Name -and
    $_.Directory.FullName -eq $root.FullName
} | ForEach-Object {
    # Verificar se não está em subdiretório
    $relPath = $_.FullName.Replace($root.FullName + "\", "")
    $isDjango = $false
    foreach ($dir in $djangoDirs) {
        if ($relPath -like "$dir\*" -or $relPath -eq $dir) {
            $isDjango = $true
            break
        }
    }
    
    if (-not $isDjango) {
        $dest = Join-Path "scripts\utilitarios" $_.Name
        if (Test-Path $dest) {
            $counter = 1
            $base = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
            $ext = $_.Extension
            while (Test-Path $dest) {
                $dest = Join-Path "scripts\utilitarios" "${base}_${counter}${ext}"
                $counter++
            }
        }
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  ✓ $($_.Name) -> scripts\utilitarios/" -ForegroundColor Gray
        $stats.py++
    }
}

# 4. Mover .txt de comandos
Write-Host "`n4. Movendo arquivos .txt de comandos..." -ForegroundColor Yellow
$keywords = @("comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES")
Get-ChildItem -Path $root -Filter "*.txt" -File | Where-Object {
    $keywords | Where-Object { $_.Name -like "*$_*" }
} | ForEach-Object {
    $dest = Join-Path "deploy" $_.Name
    if (Test-Path $dest) {
        $counter = 1
        $base = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $ext = $_.Extension
        while (Test-Path $dest) {
            $dest = Join-Path "deploy" "${base}_${counter}${ext}"
            $counter++
        }
    }
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Host "  ✓ $($_.Name) -> deploy/" -ForegroundColor Gray
    $stats.txt++
}

# Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$total = 0
foreach ($key in $stats.Keys) {
    if ($stats[$key] -gt 0) {
        Write-Host "  $($key.ToUpper()): $($stats[$key]) arquivo(s)" -ForegroundColor White
        $total += $stats[$key]
    }
}
Write-Host "  TOTAL: $total arquivo(s) movidos" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n✅ Organização concluída!" -ForegroundColor Green
Write-Host "Consulte docs/ORGANIZACAO_PROJETO.md para mais informações." -ForegroundColor Yellow

