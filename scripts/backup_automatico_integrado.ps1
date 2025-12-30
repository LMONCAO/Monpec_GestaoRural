# Função de backup automático integrado (PowerShell)
# Pode ser chamada de qualquer script de deploy

function Backup-Automatico {
    param(
        [string]$Tipo = "completo",  # completo, rapido, apenas-db
        [bool]$Comprimir = $true
    )
    
    Write-Host ""
    Write-Host "🔄 [BACKUP AUTOMÁTICO] Iniciando backup ($Tipo)..." -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar se estamos em um projeto Django
    if (-not (Test-Path "manage.py")) {
        Write-Host "⚠️  Erro: manage.py não encontrado. Não é um projeto Django?" -ForegroundColor Yellow
        return $false
    }
    
    # Verificar se o comando existe
    $helpOutput = python manage.py backup_completo --help 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Erro: Comando backup_completo não encontrado" -ForegroundColor Yellow
        return $false
    }
    
    # Fazer backup conforme tipo
    switch ($Tipo) {
        "rapido" {
            Write-Host "📦 Fazendo backup rápido (apenas banco de dados)..." -ForegroundColor Yellow
            python manage.py backup_completo --only-db --keep-days 7
        }
        "apenas-db" {
            Write-Host "📦 Fazendo backup apenas do banco de dados)..." -ForegroundColor Yellow
            python manage.py backup_completo --only-db --keep-days 7
        }
        "completo" {
            if ($Comprimir) {
                Write-Host "📦 Fazendo backup completo comprimido..." -ForegroundColor Yellow
                python manage.py backup_completo --compress --keep-days 7
            } else {
                Write-Host "📦 Fazendo backup completo..." -ForegroundColor Yellow
                python manage.py backup_completo --keep-days 7
            }
        }
        default {
            Write-Host "⚠️  Tipo de backup desconhecido: $Tipo" -ForegroundColor Yellow
            return $false
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ [BACKUP AUTOMÁTICO] Backup concluído com sucesso!" -ForegroundColor Green
        
        # Criar tag Git se estiver em repositório Git
        $gitDir = git rev-parse --git-dir 2>$null
        if ($LASTEXITCODE -eq 0) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $TAG_NAME = "backup-$timestamp"
            git tag -a "$TAG_NAME" -m "Backup automático - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "🏷️  Tag Git criada: $TAG_NAME" -ForegroundColor Green
            }
        }
        
        return $true
    } else {
        Write-Host ""
        Write-Host "❌ [BACKUP AUTOMÁTICO] Erro ao fazer backup!" -ForegroundColor Red
        return $false
    }
}

# Se script for executado diretamente, fazer backup
if ($MyInvocation.InvocationName -ne '.') {
    $tipo = if ($args[0]) { $args[0] } else { "completo" }
    $comprimir = if ($args[1]) { [bool]::Parse($args[1]) } else { $true }
    Backup-Automatico -Tipo $tipo -Comprimir $comprimir
}






