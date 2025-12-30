# Script AUTOMATICO - Upload completo sem perguntas
# Uso: .\UPLOAD_COMPLETO_AUTOMATICO.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPLOAD COMPLETO AUTOMATICO" -ForegroundColor Cyan
Write-Host "  Enviando pasta inteira para Google Cloud" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gsutil
if (-not (Get-Command gsutil -ErrorAction SilentlyContinue)) {
    Write-Host "[ERRO] gsutil não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale o Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Obter projeto atual
$projectId = gcloud config get-value project 2>&1
if (-not $projectId -or $projectId -match "ERROR") {
    Write-Host "[ERRO] Nenhum projeto configurado no gcloud!" -ForegroundColor Red
    Write-Host "Execute: gcloud config set project SEU_PROJECT_ID" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Projeto Google Cloud: $projectId" -ForegroundColor Green
Write-Host ""

# Nome do bucket (usar nome do projeto + -backup)
$bucketName = "$projectId-backup-completo"

# Nome da pasta no bucket (usar nome da pasta atual)
$folderName = Split-Path -Leaf (Get-Location)

Write-Host "Pasta local: $(Get-Location)" -ForegroundColor Gray
Write-Host "Pasta no Cloud: $folderName" -ForegroundColor Gray
Write-Host "Bucket: $bucketName" -ForegroundColor Gray
Write-Host ""

# Verificar se bucket existe, se não existir, criar
Write-Host "Verificando bucket..." -ForegroundColor Yellow
$bucketExists = gsutil ls -b "gs://$bucketName" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Bucket não existe. Criando..." -ForegroundColor Yellow
    gsutil mb -p $projectId -l us-central1 "gs://$bucketName"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Não foi possível criar o bucket!" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    Write-Host "Bucket criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Bucket já existe!" -ForegroundColor Green
}
Write-Host ""

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
    "-x", "*.log",
    "-x", ".gitignore",
    "-x", "*.md",
    "-x", "docs/**"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO UPLOAD..." -ForegroundColor Cyan
Write-Host "  Isso pode levar vários minutos!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Excluindo automaticamente:" -ForegroundColor Yellow
Write-Host "  - venv, __pycache__, .git, node_modules" -ForegroundColor Gray
Write-Host "  - *.pyc, .env, logs, temp, staticfiles" -ForegroundColor Gray
Write-Host "  - *.log, .gitignore, *.md, docs" -ForegroundColor Gray
Write-Host ""

# Fazer upload usando rsync (sincronização - mais rápido)
Write-Host "Fazendo upload..." -ForegroundColor Green
gsutil -m rsync -r $excludeArgs "." "gs://$bucketName/$folderName/"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  [ERRO] Falha no upload!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Verifique as mensagens de erro acima." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  UPLOAD CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Seus arquivos estão em:" -ForegroundColor Cyan
Write-Host "gs://$bucketName/$folderName/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para verificar:" -ForegroundColor Gray
Write-Host "gsutil ls -r gs://$bucketName/$folderName/" -ForegroundColor Gray
Write-Host ""
Read-Host "Pressione Enter para sair"

