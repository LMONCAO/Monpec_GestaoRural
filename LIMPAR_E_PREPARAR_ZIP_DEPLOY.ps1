# Script PowerShell para limpar e criar ZIP apenas com arquivos necessários para deploy
# Execute: .\LIMPAR_E_PREPARAR_ZIP_DEPLOY.ps1

Write-Host "🧹 Limpando e preparando arquivos para deploy..." -ForegroundColor Cyan
Write-Host ""

# Criar pasta temporária limpa
$pastaLimpa = "Monpec_GestaoRural_LIMPO"
$zipFinal = "Monpec_Deploy.zip"

# Remover pasta e ZIP anteriores se existirem
if (Test-Path $pastaLimpa) {
    Remove-Item -Recurse -Force $pastaLimpa
    Write-Host "✅ Pasta anterior removida" -ForegroundColor Green
}

if (Test-Path $zipFinal) {
    Remove-Item -Force $zipFinal
    Write-Host "✅ ZIP anterior removido" -ForegroundColor Green
}

# Criar pasta limpa
New-Item -ItemType Directory -Path $pastaLimpa | Out-Null
Write-Host "✅ Pasta limpa criada: $pastaLimpa" -ForegroundColor Green
Write-Host ""

# Arquivos e pastas ESSENCIAIS para deploy
$arquivosEssenciais = @(
    "manage.py",
    "Dockerfile.prod",
    "requirements_producao.txt",
    "app.yaml",
    "cloudbuild.yaml",
    "RESETAR_E_DEPLOY_DO_ZERO.sh",
    "README.md"
)

# Pastas ESSENCIAIS
$pastasEssenciais = @(
    "sistema_rural",
    "gestao_rural",
    "templates",
    "static",
    "api",
    "scripts"
)

Write-Host "📋 Copiando arquivos essenciais..." -ForegroundColor Yellow

# Copiar arquivos essenciais
foreach ($arquivo in $arquivosEssenciais) {
    if (Test-Path $arquivo) {
        Copy-Item -Path $arquivo -Destination $pastaLimpa -Force
        Write-Host "  ✅ $arquivo" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $arquivo não encontrado (pode ser opcional)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📁 Copiando pastas essenciais..." -ForegroundColor Yellow

# Copiar pastas essenciais
foreach ($pasta in $pastasEssenciais) {
    if (Test-Path $pasta) {
        Copy-Item -Path $pasta -Destination $pastaLimpa -Recurse -Force
        Write-Host "  ✅ $pasta/" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $pasta/ não encontrada (pode ser opcional)" -ForegroundColor Yellow
    }
}

# Verificar se manage.py foi copiado (essencial)
if (-not (Test-Path "$pastaLimpa\manage.py")) {
    Write-Host ""
    Write-Host "❌ ERRO: manage.py não encontrado! O deploy não funcionará sem ele." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🗜️  Criando ZIP..." -ForegroundColor Yellow

# Criar ZIP
Compress-Archive -Path "$pastaLimpa\*" -DestinationPath $zipFinal -Force

Write-Host ""
Write-Host "✅ ZIP criado com sucesso: $zipFinal" -ForegroundColor Green
Write-Host ""

# Calcular tamanho
$tamanhoZip = (Get-Item $zipFinal).Length / 1MB
Write-Host "📊 Tamanho do ZIP: $([math]::Round($tamanhoZip, 2)) MB" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎉 PRONTO! Arquivo $zipFinal está pronto para upload no Cloud Shell!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Faça upload do arquivo $zipFinal no Google Cloud Shell"
Write-Host "2. Descompacte: unzip $zipFinal"
Write-Host "3. Execute: bash RESETAR_E_DEPLOY_DO_ZERO.sh"
Write-Host ""

# Perguntar se quer limpar a pasta temporária
$resposta = Read-Host "Deseja remover a pasta temporária $pastaLimpa? (S/N)"
if ($resposta -eq "S" -or $resposta -eq "s") {
    Remove-Item -Recurse -Force $pastaLimpa
    Write-Host "✅ Pasta temporária removida" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Concluído!" -ForegroundColor Green

