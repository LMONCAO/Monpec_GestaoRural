# Script PowerShell para organizar o projeto
$ErrorActionPreference = "Continue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ORGANIZAÇÃO DO PROJETO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Criar estrutura de pastas
$folders = @("docs", "temp", "scripts\deploy", "scripts\admin", "scripts\correcoes", 
             "scripts\utilitarios", "scripts\configuracao", "scripts\backup", "deploy")

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Criada pasta: $folder" -ForegroundColor Green
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
$keepInRoot = @("manage.py", "requirements.txt", "Dockerfile", "Dockerfile.prod", 
                ".gitignore", "app.yaml", "build-config.yaml", "cloudbuild-config.yaml",
                "organizar_projeto_completo.py", "organizar_projeto.ps1", "entrypoint.sh")

# 1. Mover arquivos .md
Write-Host "`n1. Movendo arquivos .md..." -ForegroundColor Yellow
Get-ChildItem -Filter "*.md" -File | Where-Object { $keepInRoot -notcontains $_.Name } | ForEach-Object {
    $dest = Join-Path "docs" $_.Name
    if (Test-Path $dest) {
        $counter = 1
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $ext = $_.Extension
        do {
            $dest = Join-Path "docs" "${baseName}_${counter}${ext}"
            $counter++
        } while (Test-Path $dest)
    }
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Host "  ✓ $($_.Name) -> docs/" -ForegroundColor Green
    $stats.md++
}

# 2. Mover scripts .sh, .ps1, .bat
Write-Host "`n2. Movendo scripts..." -ForegroundColor Yellow

# Função para categorizar script
function Get-ScriptCategory {
    param($filename)
    $name = $filename.ToLower()
    
    if ($name -match "deploy|atualizar|aplicar_migracoes|cloud|gcp|google") { return "scripts\deploy" }
    if ($name -match "admin|criar_admin|superuser") { return "scripts\admin" }
    if ($name -match "corrigir|correcao|fix|solucao") { return "scripts\correcoes" }
    if ($name -match "configurar|config|setup") { return "scripts\configuracao" }
    if ($name -match "backup|exportar|importar") { return "scripts\backup" }
    return "scripts"
}

foreach ($ext in @(".sh", ".ps1", ".bat")) {
    Get-ChildItem -Filter "*${ext}" -File | Where-Object { $keepInRoot -notcontains $_.Name } | ForEach-Object {
        $category = Get-ScriptCategory $_.Name
        $dest = Join-Path $category $_.Name
        
        if (Test-Path $dest) {
            $counter = 1
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
            do {
                $dest = Join-Path $category "${baseName}_${counter}${ext}"
                $counter++
            } while (Test-Path $dest)
        }
        
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  ✓ $($_.Name) -> $category/" -ForegroundColor Green
        $stats[$ext.TrimStart('.')]++
    }
}

# 3. Mover scripts Python utilitários
Write-Host "`n3. Movendo scripts Python utilitários..." -ForegroundColor Yellow
$djangoDirs = @("gestao_rural", "sistema_rural", "api", "templates", "static")
Get-ChildItem -Filter "*.py" -File | Where-Object { 
    $keepInRoot -notcontains $_.Name -and 
    $_.Directory.FullName -eq $PWD.Path 
} | ForEach-Object {
    # Verificar se não está em subdiretório Django
    $isDjango = $false
    foreach ($dir in $djangoDirs) {
        if ((Get-Item $_.FullName).FullName -like "*\$dir\*") {
            $isDjango = $true
            break
        }
    }
    
    if (-not $isDjango) {
        $dest = Join-Path "scripts\utilitarios" $_.Name
        if (Test-Path $dest) {
            $counter = 1
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
            $ext = $_.Extension
            do {
                $dest = Join-Path "scripts\utilitarios" "${baseName}_${counter}${ext}"
                $counter++
            } while (Test-Path $dest)
        }
        Move-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  ✓ $($_.Name) -> scripts\utilitarios/" -ForegroundColor Green
        $stats.py++
    }
}

# 4. Mover arquivos .txt de comandos
Write-Host "`n4. Movendo arquivos .txt de comandos..." -ForegroundColor Yellow
$commandKeywords = @("comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES")
Get-ChildItem -Filter "*.txt" -File | Where-Object { 
    $commandKeywords | Where-Object { $_.Name -like "*$_*" }
} | ForEach-Object {
    $dest = Join-Path "deploy" $_.Name
    if (Test-Path $dest) {
        $counter = 1
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $ext = $_.Extension
        do {
            $dest = Join-Path "deploy" "${baseName}_${counter}${ext}"
            $counter++
        } while (Test-Path $dest)
    }
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Host "  ✓ $($_.Name) -> deploy/" -ForegroundColor Green
    $stats.txt++
}

# Resumo
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "RESUMO:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
foreach ($key in $stats.Keys) {
    if ($stats[$key] -gt 0) {
        Write-Host "  $($key.ToUpper()): $($stats[$key]) arquivo(s)" -ForegroundColor White
    }
}
Write-Host "==========================================" -ForegroundColor Cyan
