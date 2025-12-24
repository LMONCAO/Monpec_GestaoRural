# Script para corrigir requirements_producao.txt antes do deploy
# Remove dependências problemáticas que não existem no PyPI

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 CORRIGINDO REQUIREMENTS_PRODUCAO.TXT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$requirementsFile = "requirements_producao.txt"

if (Test-Path $requirementsFile) {
    Write-Host "📋 Lendo arquivo: $requirementsFile" -ForegroundColor Yellow
    
    # Ler conteúdo do arquivo
    $content = Get-Content $requirementsFile -Raw
    
    # Remover linhas problemáticas
    $linesToRemove = @(
        "django-logging",
        "django-logging==",
        "django-logging==0.1.0"
    )
    
    $modified = $false
    $newContent = $content
    
    foreach ($line in $linesToRemove) {
        if ($newContent -match $line) {
            Write-Host "⚠️  Removendo dependência problemática: $line" -ForegroundColor Yellow
            # Remover linha completa (com quebra de linha)
            $newContent = $newContent -replace "(?m)^.*$line.*$\r?\n", ""
            $modified = $true
        }
    }
    
    # Remover linhas duplicadas (stripe aparece duas vezes)
    $lines = $newContent -split "`n" | Where-Object { $_.Trim() -ne "" }
    $uniqueLines = @()
    $seen = @{}
    
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        # Ignorar comentários e linhas vazias
        if ($trimmed -match "^#|^$") {
            $uniqueLines += $line
        } elseif ($trimmed -match "^([^=#]+)") {
            $packageName = $matches[1].Trim()
            if (-not $seen.ContainsKey($packageName)) {
                $seen[$packageName] = $true
                $uniqueLines += $line
            } else {
                Write-Host "⚠️  Removendo duplicata: $packageName" -ForegroundColor Yellow
                $modified = $true
            }
        } else {
            $uniqueLines += $line
        }
    }
    
    if ($modified) {
        # Criar backup
        $backupFile = "$requirementsFile.backup"
        Copy-Item $requirementsFile $backupFile
        Write-Host "✅ Backup criado: $backupFile" -ForegroundColor Green
        
        # Salvar arquivo corrigido
        $uniqueLines -join "`n" | Set-Content $requirementsFile -Encoding UTF8
        Write-Host "✅ Arquivo corrigido: $requirementsFile" -ForegroundColor Green
    } else {
        Write-Host "✅ Nenhuma correção necessária" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "📋 Conteúdo do arquivo (primeiras 20 linhas):" -ForegroundColor Cyan
    Get-Content $requirementsFile | Select-Object -First 20 | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
    
} else {
    Write-Host "❌ Arquivo não encontrado: $requirementsFile" -ForegroundColor Red
    Write-Host "   Certifique-se de estar no diretório correto do projeto" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ CORREÇÃO CONCLUÍDA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximo passo: Fazer deploy novamente" -ForegroundColor Yellow
Write-Host ""

