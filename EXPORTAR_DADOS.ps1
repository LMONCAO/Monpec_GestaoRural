# Script para exportar dados do banco local
$ErrorActionPreference = "Stop"

# Mudar para o diretório do script
Set-Location $PSScriptRoot

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "📊 Exportando dados do banco local..." -ForegroundColor Cyan

try {
    python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
    
    if (Test-Path "dados_backup.json") {
        $fileSize = (Get-Item "dados_backup.json").Length / 1MB
        Write-Host ""
        Write-Host "✅ Exportação concluída com sucesso!" -ForegroundColor Green
        Write-Host "📁 Arquivo criado: dados_backup.json" -ForegroundColor Green
        Write-Host "📏 Tamanho: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Próximos passos:" -ForegroundColor Cyan
        Write-Host "1. Faça upload do arquivo dados_backup.json para o Google Cloud Shell"
        Write-Host "2. No Cloud Shell, execute: python3 manage.py loaddata dados_backup.json"
        Write-Host "3. Carregue as categorias: python3 manage.py carregar_categorias"
    } else {
        Write-Host ""
        Write-Host "❌ Erro: Arquivo não foi criado" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erro na exportação: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique se:" -ForegroundColor Yellow
    Write-Host "- O banco de dados local está acessível"
    Write-Host "- O Django está instalado corretamente"
    Write-Host "- Você está no diretório correto do projeto"
}

