# Script PowerShell para atualizar o site MONPEC em produção
# Execute: .\atualizar_producao.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ATUALIZANDO SITE MONPEC EM PRODUÇÃO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erro: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto Django."
    exit 1
}

# Ativar virtualenv se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Ativando virtualenv..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Coletar arquivos estáticos
Write-Host "📁 Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Criar/corrigir usuário admin
Write-Host "👤 Criando/corrigindo usuário admin..." -ForegroundColor Yellow
python criar_admin_fix.py

# Aplicar migrações (se houver)
Write-Host "🗄️  Verificando migrações..." -ForegroundColor Yellow
python manage.py migrate --noinput

# Verificar se as imagens existem
Write-Host "🖼️  Verificando imagens..." -ForegroundColor Yellow
if (Test-Path "static\site") {
    $imageCount = (Get-ChildItem -Path "static\site\foto*.jpeg" -ErrorAction SilentlyContinue).Count
    if ($imageCount -gt 0) {
        Write-Host "✅ Encontradas $imageCount imagens" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Nenhuma imagem encontrada em static\site\" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Diretório static\site não encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ ATUALIZAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "1. Fazer upload dos arquivos para o servidor"
Write-Host "2. Executar collectstatic no servidor"
Write-Host "3. Executar criar_admin_fix.py no servidor"
Write-Host "4. Reiniciar o servidor web"
Write-Host "5. Testar o site em https://monpec.com.br"
Write-Host ""



