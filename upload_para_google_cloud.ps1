# Script para fazer upload da pasta inteira para Google Cloud Storage
# Uso: .\upload_para_google_cloud.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Upload para Google Cloud Storage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gsutil está instalado
$gsutilPath = Get-Command gsutil -ErrorAction SilentlyContinue
if (-not $gsutilPath) {
    Write-Host "ERRO: gsutil não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para instalar o gsutil:" -ForegroundColor Yellow
    Write-Host "1. Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host "2. Execute: gcloud init" -ForegroundColor Yellow
    Write-Host "3. Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

# Verificar se está autenticado
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Host "ERRO: Você precisa fazer login no Google Cloud!" -ForegroundColor Red
    Write-Host "Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "Autenticado como: $authCheck" -ForegroundColor Green
Write-Host ""

# Solicitar nome do bucket
$bucketName = Read-Host "Digite o nome do bucket (ex: monpec-static ou monpec-backup)"
if ([string]::IsNullOrWhiteSpace($bucketName)) {
    Write-Host "ERRO: Nome do bucket é obrigatório!" -ForegroundColor Red
    exit 1
}

# Verificar se o bucket existe
Write-Host "Verificando bucket '$bucketName'..." -ForegroundColor Yellow
$bucketExists = gsutil ls -b "gs://$bucketName" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Bucket não encontrado. Deseja criar? (S/N)" -ForegroundColor Yellow
    $createBucket = Read-Host
    if ($createBucket -eq "S" -or $createBucket -eq "s") {
        Write-Host "Criando bucket '$bucketName'..." -ForegroundColor Yellow
        gsutil mb -p $(gcloud config get-value project) -l us-central1 "gs://$bucketName"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERRO: Não foi possível criar o bucket!" -ForegroundColor Red
            exit 1
        }
        Write-Host "Bucket criado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Operação cancelada." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "Bucket encontrado!" -ForegroundColor Green
}
Write-Host ""

# Perguntar sobre exclusões
Write-Host "Deseja excluir arquivos/pastas específicos do upload? (S/N)" -ForegroundColor Yellow
$excluirArquivos = Read-Host
$excludePatterns = @()

if ($excluirArquivos -eq "S" -or $excluirArquivos -eq "s") {
    Write-Host ""
    Write-Host "Pastas/arquivos que serão EXCLUÍDOS automaticamente:" -ForegroundColor Yellow
    Write-Host "  - venv/ (ambiente virtual Python)" -ForegroundColor Gray
    Write-Host "  - __pycache__/ (cache Python)" -ForegroundColor Gray
    Write-Host "  - .git/ (repositório Git)" -ForegroundColor Gray
    Write-Host "  - node_modules/ (dependências Node)" -ForegroundColor Gray
    Write-Host "  - *.pyc (arquivos compilados Python)" -ForegroundColor Gray
    Write-Host "  - .env (variáveis de ambiente)" -ForegroundColor Gray
    Write-Host "  - logs/ (arquivos de log)" -ForegroundColor Gray
    Write-Host "  - temp/ (arquivos temporários)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Deseja adicionar mais exclusões? (S/N)" -ForegroundColor Yellow
    $adicionarExclusoes = Read-Host
    
    if ($adicionarExclusoes -eq "S" -or $adicionarExclusoes -eq "s") {
        Write-Host "Digite os padrões a excluir (um por linha, deixe vazio para terminar):" -ForegroundColor Yellow
        Write-Host "Exemplos: backups/, *.log, staticfiles/" -ForegroundColor Gray
        while ($true) {
            $pattern = Read-Host "Padrão"
            if ([string]::IsNullOrWhiteSpace($pattern)) {
                break
            }
            $excludePatterns += $pattern
        }
    }
}

# Construir comando de exclusão
$excludeArgs = @()
$excludeArgs += "-x", "venv/**"
$excludeArgs += "-x", "__pycache__/**"
$excludeArgs += "-x", ".git/**"
$excludeArgs += "-x", "node_modules/**"
$excludeArgs += "-x", "*.pyc"
$excludeArgs += "-x", ".env"
$excludeArgs += "-x", "logs/**"
$excludeArgs += "-x", "temp/**"

foreach ($pattern in $excludePatterns) {
    $excludeArgs += "-x", $pattern
}

# Perguntar sobre modo de upload
Write-Host ""
Write-Host "Escolha o modo de upload:" -ForegroundColor Yellow
Write-Host "1. Sincronizar (rsync) - mais rápido, só envia arquivos novos/modificados" -ForegroundColor Cyan
Write-Host "2. Copiar completo - envia tudo novamente" -ForegroundColor Cyan
$modoUpload = Read-Host "Digite 1 ou 2 (padrão: 1)"

if ([string]::IsNullOrWhiteSpace($modoUpload)) {
    $modoUpload = "1"
}

# Obter diretório atual
$currentDir = Get-Location
$projectName = Split-Path -Leaf $currentDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando upload..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Origem: $currentDir" -ForegroundColor Gray
Write-Host "Destino: gs://$bucketName/$projectName/" -ForegroundColor Gray
Write-Host ""

# Executar upload
if ($modoUpload -eq "1") {
    Write-Host "Modo: Sincronização (rsync)" -ForegroundColor Green
    Write-Host "Isso pode levar alguns minutos dependendo do tamanho da pasta..." -ForegroundColor Yellow
    Write-Host ""
    
    if ($excludeArgs.Count -gt 0) {
        gsutil -m rsync -r $excludeArgs "." "gs://$bucketName/$projectName/"
    } else {
        gsutil -m rsync -r "." "gs://$bucketName/$projectName/"
    }
} else {
    Write-Host "Modo: Cópia completa" -ForegroundColor Green
    Write-Host "Isso pode levar vários minutos dependendo do tamanho da pasta..." -ForegroundColor Yellow
    Write-Host ""
    
    if ($excludeArgs.Count -gt 0) {
        gsutil -m cp -r $excludeArgs "." "gs://$bucketName/$projectName/"
    } else {
        gsutil -m cp -r "." "gs://$bucketName/$projectName/"
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Upload concluído com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Seus arquivos estão disponíveis em:" -ForegroundColor Cyan
    Write-Host "gs://$bucketName/$projectName/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para verificar os arquivos:" -ForegroundColor Gray
    Write-Host "gsutil ls -r gs://$bucketName/$projectName/" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Erro durante o upload!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Verifique as mensagens de erro acima." -ForegroundColor Yellow
    exit 1
}

