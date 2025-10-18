# 📦 CRIANDO PACOTE DE DEPLOY - SISTEMA RURAL COM IA

Write-Host "📦 Criando pacote de deploy..." -ForegroundColor Green

# Navegar para o diretório do projeto
Set-Location "C:\Software_Projetos_Rural"

# Lista de arquivos e pastas para incluir
$includeItems = @(
    "manage.py",
    "requirements.txt",
    "gestao_rural",
    "sistema_rural", 
    "templates",
    "static",
    "*.py",
    "*.md",
    "*.sh",
    "*.ps1",
    ".env*",
    "deploy_*",
    "*.txt"
)

# Lista de arquivos e pastas para excluir
$excludeItems = @(
    "venv",
    "__pycache__",
    "*.pyc",
    "db.sqlite3",
    "*.log",
    ".git",
    "node_modules",
    "*.tmp",
    "*.temp"
)

Write-Host "🔍 Coletando arquivos para deploy..." -ForegroundColor Yellow

# Coletar arquivos
$files = @()

# Adicionar arquivos específicos
foreach ($item in $includeItems) {
    if (Test-Path $item) {
        if ((Get-Item $item).PSIsContainer) {
            # É uma pasta
            $files += Get-ChildItem -Path $item -Recurse | Where-Object {
                $include = $true
                foreach ($exclude in $excludeItems) {
                    if ($_.FullName -like "*\$exclude\*" -or $_.FullName -like "*\$exclude") {
                        $include = $false
                        break
                    }
                }
                $include
            }
        } else {
            # É um arquivo
            $files += Get-Item $item
        }
    }
}

Write-Host "📁 Arquivos coletados: $($files.Count)" -ForegroundColor Cyan

# Criar arquivo tar
$deployFile = "sistema-rural-deploy.tar.gz"

Write-Host "🗜️ Criando arquivo de deploy: $deployFile" -ForegroundColor Yellow

try {
    # Usar tar com lista de arquivos específicos
    $files | ForEach-Object { $_.FullName } | tar -czf $deployFile -T -
    
    if (Test-Path $deployFile) {
        $fileSize = (Get-Item $deployFile).Length / 1MB
        Write-Host "✅ Arquivo criado com sucesso: $deployFile ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
        
        # Mostrar conteúdo do arquivo
        Write-Host "📋 Conteúdo do pacote:" -ForegroundColor Cyan
        tar -tzf $deployFile | Select-Object -First 20 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        
        if ((tar -tzf $deployFile | Measure-Object).Count -gt 20) {
            Write-Host "  ... e mais $((tar -tzf $deployFile | Measure-Object).Count - 20) arquivos" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
        Write-Host "1. Upload: scp $deployFile root@45.32.219.76:/tmp/" -ForegroundColor White
        Write-Host "2. Deploy: ssh root@45.32.219.76 'cd /tmp && tar -xzf $deployFile -C /home/django/sistema-rural/ && chown -R django:django /home/django/sistema-rural && cd /home/django/sistema-rural && chmod +x deploy_automatico.sh && ./deploy_automatico.sh'" -ForegroundColor White
        
    } else {
        Write-Host "❌ Erro ao criar arquivo de deploy" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Script concluído!" -ForegroundColor Green



