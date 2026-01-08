# ==========================================
# Script para Corrigir Problemas de Migrações
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Correção de Problemas de Migrações" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está usando PostgreSQL
Write-Host "1. Verificando configuração..." -ForegroundColor Yellow

$dbName = python -c "import os; from decouple import config; print(config('DB_NAME', default=''))" 2>&1

if ([string]::IsNullOrWhiteSpace($dbName) -or $dbName -match "\.sqlite3$") {
    Write-Host "⚠️  Você está usando SQLite. Para compatibilidade com Google Cloud:" -ForegroundColor Yellow
    Write-Host "   1. Configure PostgreSQL: .\configurar_postgresql_local.ps1" -ForegroundColor White
    Write-Host "   2. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Deseja continuar mesmo assim? (S/N)"
    if ($continue -ne "S" -and $continue -ne "s") {
        exit 0
    }
}

Write-Host ""
Write-Host "2. Verificando migrações com problemas..." -ForegroundColor Yellow

# Listar migrações com problemas
python manage.py showmigrations 2>&1 | Out-String | Select-String "\[X\]|\[ \]"

Write-Host ""
Write-Host "3. Opções de correção:" -ForegroundColor Yellow
Write-Host "   [1] Aplicar todas as migrações pendentes" -ForegroundColor White
Write-Host "   [2] Fazer fake de migrações específicas (se já aplicadas manualmente)" -ForegroundColor White
Write-Host "   [3] Resetar migrações (CUIDADO: apaga dados!)" -ForegroundColor Red
Write-Host "   [4] Verificar diferenças entre modelos e banco" -ForegroundColor White
Write-Host "   [5] Criar novas migrações para modelos sem migração" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Escolha uma opção (1-5)"

switch ($opcao) {
    "1" {
        Write-Host ""
        Write-Host "Aplicando todas as migrações..." -ForegroundColor Yellow
        python manage.py migrate
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Migrações aplicadas!" -ForegroundColor Green
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Fake de migrações (marca como aplicadas sem executar)" -ForegroundColor Yellow
        $app = Read-Host "Nome do app (ex: gestao_rural)"
        $migration = Read-Host "Nome da migração (ex: 0090) ou 'all' para todas pendentes"
        
        if ($migration -eq "all") {
            Write-Host "⚠️  Isso marcará TODAS as migrações pendentes como aplicadas!" -ForegroundColor Red
            $confirm = Read-Host "Tem certeza? (S/N)"
            if ($confirm -eq "S" -or $confirm -eq "s") {
                python manage.py migrate $app --fake
            }
        } else {
            python manage.py migrate $app $migration --fake
        }
    }
    "3" {
        Write-Host ""
        Write-Host "⚠️  ⚠️  ⚠️  ATENÇÃO: Isso vai APAGAR TODOS OS DADOS! ⚠️  ⚠️  ⚠️" -ForegroundColor Red
        Write-Host ""
        $confirm = Read-Host "Você tem CERTEZA ABSOLUTA? Digite 'SIM' para confirmar"
        
        if ($confirm -eq "SIM") {
            Write-Host ""
            Write-Host "Resetando banco de dados..." -ForegroundColor Yellow
            Write-Host "  (Isso pode demorar alguns minutos)" -ForegroundColor White
            
            # Fazer backup primeiro
            $backupFile = "backup_antes_reset_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            Write-Host "  Fazendo backup para: $backupFile" -ForegroundColor Yellow
            python manage.py dumpdata > $backupFile 2>&1
            
            # Resetar
            python manage.py flush --no-input
            python manage.py migrate
            
            Write-Host "✅ Banco resetado! Backup salvo em: $backupFile" -ForegroundColor Green
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host ""
        Write-Host "Verificando diferenças..." -ForegroundColor Yellow
        python manage.py makemigrations --dry-run --verbosity 2
    }
    "5" {
        Write-Host ""
        Write-Host "Criando novas migrações..." -ForegroundColor Yellow
        python manage.py makemigrations
        
        Write-Host ""
        Write-Host "Aplicando novas migrações..." -ForegroundColor Yellow
        python manage.py migrate
    }
    default {
        Write-Host "Opção inválida!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Processo concluído!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""


