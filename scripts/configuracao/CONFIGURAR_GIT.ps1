# Script para configurar Git e preparar para enviar ao repositório remoto
# Execute: .\CONFIGURAR_GIT.ps1

Write-Host "🔧 CONFIGURAÇÃO DO GIT PARA MONPEC GESTÃO RURAL" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
Write-Host "1️⃣ Verificando se Git está instalado..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não está instalado!" -ForegroundColor Red
    Write-Host "   Instale o Git em: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Verificar se estamos no diretório correto
Write-Host "2️⃣ Verificando diretório..." -ForegroundColor Yellow
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Arquivo manage.py não encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script no diretório raiz do projeto Django" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Diretório correto detectado" -ForegroundColor Green
Write-Host ""

# Verificar se Git está inicializado
Write-Host "3️⃣ Verificando se Git está inicializado..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "⚠️ Git não está inicializado. Inicializando..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git inicializado" -ForegroundColor Green
} else {
    Write-Host "✅ Git já está inicializado" -ForegroundColor Green
}
Write-Host ""

# Verificar configuração do usuário
Write-Host "4️⃣ Verificando configuração do usuário Git..." -ForegroundColor Yellow
$userName = git config --global user.name
$userEmail = git config --global user.email

if (-not $userName -or -not $userEmail) {
    Write-Host "⚠️ Usuário Git não configurado" -ForegroundColor Yellow
    $newName = Read-Host "Digite seu nome para o Git"
    $newEmail = Read-Host "Digite seu email para o Git"
    
    git config --global user.name $newName
    git config --global user.email $newEmail
    Write-Host "✅ Usuário Git configurado" -ForegroundColor Green
} else {
    Write-Host "✅ Usuário Git já configurado:" -ForegroundColor Green
    Write-Host "   Nome: $userName" -ForegroundColor Gray
    Write-Host "   Email: $userEmail" -ForegroundColor Gray
}
Write-Host ""

# Verificar status do repositório
Write-Host "5️⃣ Verificando status do repositório..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "📋 Arquivos não commitados encontrados:" -ForegroundColor Yellow
    git status --short | Select-Object -First 10
    Write-Host ""
    
    $addFiles = Read-Host "Deseja adicionar todos os arquivos ao Git? (S/N)"
    if ($addFiles -eq "S" -or $addFiles -eq "s") {
        Write-Host "📦 Adicionando arquivos..." -ForegroundColor Yellow
        git add .
        Write-Host "✅ Arquivos adicionados" -ForegroundColor Green
        
        $commitMessage = Read-Host "Digite a mensagem do commit (ou pressione Enter para usar padrão)"
        if (-not $commitMessage) {
            $commitMessage = "Commit inicial: projeto Monpec Gestão Rural"
        }
        
        git commit -m $commitMessage
        Write-Host "✅ Commit criado" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Nenhuma mudança pendente" -ForegroundColor Green
}
Write-Host ""

# Verificar repositório remoto
Write-Host "6️⃣ Verificando repositório remoto..." -ForegroundColor Yellow
$remote = git remote -v
if (-not $remote) {
    Write-Host "⚠️ Nenhum repositório remoto configurado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para adicionar um repositório remoto, execute:" -ForegroundColor Cyan
    Write-Host '  git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git' -ForegroundColor White
    Write-Host ""
    Write-Host "Depois, para enviar os arquivos:" -ForegroundColor Cyan
    Write-Host '  git push -u origin main' -ForegroundColor White
    Write-Host "  (ou 'git push -u origin master' se sua branch for master)" -ForegroundColor Gray
    Write-Host ""
    
    $addRemote = Read-Host "Deseja adicionar um repositório remoto agora? (S/N)"
    if ($addRemote -eq "S" -or $addRemote -eq "s") {
        $remoteUrl = Read-Host "Digite a URL do repositório remoto (ex: https://github.com/usuario/repo.git)"
        if ($remoteUrl) {
            git remote add origin $remoteUrl
            Write-Host "✅ Repositório remoto adicionado" -ForegroundColor Green
            Write-Host ""
            Write-Host "Para enviar os arquivos, execute:" -ForegroundColor Cyan
            Write-Host "  git push -u origin main" -ForegroundColor White
        }
    }
} else {
    Write-Host "✅ Repositório remoto configurado:" -ForegroundColor Green
    Write-Host $remote -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para enviar os arquivos, execute:" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor White
}
Write-Host ""

# Resumo
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Crie um repositório no GitHub/GitLab (se ainda não tiver)" -ForegroundColor White
Write-Host "2. Adicione o remote: git remote add origin URL_DO_REPOSITORIO" -ForegroundColor White
Write-Host "3. Envie os arquivos: git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "📖 Para mais informações, consulte: COMO_CONFIGURAR_GIT.md" -ForegroundColor Cyan
Write-Host ""



