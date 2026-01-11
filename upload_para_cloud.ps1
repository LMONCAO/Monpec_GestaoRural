# UPLOAD PARA GOOGLE CLOUD POWERSHELL
# Execute este script no PowerShell para fazer upload do projeto

Write-Host "🚀 Fazendo upload do projeto MONPEC para Google Cloud" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Verificar se gcloud está instalado
try {
    $gcloudVersion = gcloud --version 2>$null
    Write-Host "✅ GCloud CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ GCloud CLI não encontrado!" -ForegroundColor Red
    Write-Host "📥 Baixe de: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar se está logado
try {
    $authList = gcloud auth list --filter=status:ACTIVE 2>$null
    if ($authList) {
        Write-Host "✅ Logado no Google Cloud" -ForegroundColor Green
    } else {
        Write-Host "❌ Não está logado no Google Cloud!" -ForegroundColor Red
        Write-Host "🔑 Execute: gcloud auth login" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Erro ao verificar login" -ForegroundColor Red
    exit 1
}

# Configurar projeto
Write-Host "⚙️ Configurando projeto..." -ForegroundColor Cyan
try {
    gcloud config set project monpec-sistema-rural
    Write-Host "✅ Projeto configurado: monpec-sistema-rural" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao configurar projeto" -ForegroundColor Red
    exit 1
}

# Preparar arquivos
Write-Host "📦 Preparando arquivos..." -ForegroundColor Cyan

# Criar .gcloudignore se não existir
$gcloudignorePath = ".gcloudignore"
if (!(Test-Path $gcloudignorePath)) {
    $gcloudignoreContent = @"
# Arquivos a ignorar no upload
.git/
.gitignore
*.pyc
__pycache__/
*.log
.env*
venv/
.venv/
node_modules/
staticfiles/
media/
*.sqlite3
backup_*/
test_*/
debug_*/
temp/
.vscode/
.idea/
"@
    Set-Content -Path $gcloudignorePath -Value $gcloudignoreContent
    Write-Host "✅ Arquivo .gcloudignore criado" -ForegroundColor Green
}

# Coletar arquivos estáticos
Write-Host "📂 Coletando arquivos estáticos..." -ForegroundColor Cyan
try {
    python manage.py collectstatic --noinput --clear
    Write-Host "✅ Arquivos estáticos coletados" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao coletar estáticos (continuando)" -ForegroundColor Yellow
}

# Fazer upload
Write-Host "⬆️ Fazendo upload dos arquivos..." -ForegroundColor Cyan
try {
    gcloud storage cp . gs://monpec-deploy-bucket/ --recursive --skip-if-newer
    Write-Host "✅ Upload concluído!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro no upload" -ForegroundColor Red
    exit 1
}

Write-Host "`n" + "=" * 60 -ForegroundColor Yellow
Write-Host "🎉 UPLOAD CONCLUÍDO!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Abra: https://console.cloud.google.com/cloudshell" -ForegroundColor White
Write-Host "2. Execute os comandos abaixo:" -ForegroundColor White
Write-Host ""

Write-Host "# Baixar arquivos do bucket" -ForegroundColor Green
Write-Host "gsutil cp -r gs://monpec-deploy-bucket/* ." -ForegroundColor White
Write-Host ""

Write-Host "# Executar deploy" -ForegroundColor Green
Write-Host "chmod +x deploy_atualizado.sh" -ForegroundColor White
Write-Host "bash deploy_atualizado.sh" -ForegroundColor White
Write-Host ""

Write-Host "🌐 Após o deploy, o sistema estará disponível!" -ForegroundColor Green
Write-Host "📊 Dashboard: propriedade/5/pecuaria/" -ForegroundColor White
Write-Host "📅 Planejamento: propriedade/5/pecuaria/planejamento/" -ForegroundColor White