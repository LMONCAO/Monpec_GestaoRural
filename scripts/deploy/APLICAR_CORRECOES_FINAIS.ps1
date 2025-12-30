# Script para aplicar todas as correções finais
Write-Host "🔧 Aplicando correções finais..." -ForegroundColor Cyan
Write-Host ""

# Adicionar todos os arquivos modificados
Write-Host "📦 Adicionando arquivos modificados..." -ForegroundColor Yellow
git add gestao_rural/middleware_protecao_codigo.py Dockerfile.prod sistema_rural/settings_gcp.py 2>&1 | Out-Null

# Verificar status
$status = git status --short gestao_rural/middleware_protecao_codigo.py 2>&1
if ($status) {
    Write-Host "✓ Arquivos adicionados" -ForegroundColor Green
} else {
    Write-Host "⚠️  Nenhuma mudança detectada (pode ser normal)" -ForegroundColor Yellow
}

# Fazer commit
Write-Host ""
Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m "CORREÇÃO FINAL: Middleware ignora arquivos estáticos e verificação segura de request.user" 2>&1 | ForEach-Object {
    if ($_ -match "nothing to commit|no changes") {
        Write-Host "⚠️  Nenhuma mudança para commitar" -ForegroundColor Yellow
    } else {
        Write-Host $_
    }
}

# Fazer push
Write-Host ""
Write-Host "📤 Fazendo push..." -ForegroundColor Yellow
git push origin master 2>&1 | ForEach-Object {
    if ($_ -match "error|fatal|failed") {
        Write-Host $_ -ForegroundColor Red
    } else {
        Write-Host $_
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Correções aplicadas com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ O build será acionado automaticamente..." -ForegroundColor Cyan
    Write-Host "   Aguarde 3-5 minutos e teste:" -ForegroundColor Yellow
    Write-Host "   https://monpec-fzzfjppzva-uc.a.run.app"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    Write-Host "   Verifique sua conexão e autenticação git" -ForegroundColor Yellow
}



