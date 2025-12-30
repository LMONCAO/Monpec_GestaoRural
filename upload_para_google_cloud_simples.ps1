# Script SIMPLES para upload rápido - sem perguntas
# Uso: .\upload_para_google_cloud_simples.ps1 -BucketName "meu-bucket"

param(
    [Parameter(Mandatory=$true)]
    [string]$BucketName,
    
    [string]$ProjectName = "",
    [switch]$Sync = $true
)

Write-Host "Upload para Google Cloud Storage..." -ForegroundColor Cyan
Write-Host "Bucket: $BucketName" -ForegroundColor Yellow

# Se não especificar nome do projeto, usar nome da pasta atual
if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    $ProjectName = Split-Path -Leaf (Get-Location)
}

# Verificar gsutil
if (-not (Get-Command gsutil -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: gsutil não encontrado! Instale o Google Cloud SDK." -ForegroundColor Red
    exit 1
}

# Excluir arquivos desnecessários
$excludeArgs = @(
    "-x", "venv/**",
    "-x", "__pycache__/**",
    "-x", ".git/**",
    "-x", "node_modules/**",
    "-x", "*.pyc",
    "-x", ".env",
    "-x", "logs/**",
    "-x", "temp/**",
    "-x", "staticfiles/**",
    "-x", "*.log"
)

Write-Host "Iniciando upload para gs://$BucketName/$ProjectName/ ..." -ForegroundColor Green

if ($Sync) {
    gsutil -m rsync -r $excludeArgs "." "gs://$BucketName/$ProjectName/"
} else {
    gsutil -m cp -r $excludeArgs "." "gs://$BucketName/$ProjectName/"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Upload concluído!" -ForegroundColor Green
} else {
    Write-Host "Erro no upload!" -ForegroundColor Red
    exit 1
}

