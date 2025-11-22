# Script para fazer push para GitHub usando Personal Access Token
# Execute no PowerShell na pasta do projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FAZER PUSH PARA GITHUB (COM TOKEN)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Entrar na pasta do projeto
$projectPath = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
cd $projectPath

Write-Host "Pasta do projeto: $projectPath" -ForegroundColor Yellow
Write-Host ""

# Verificar se é repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "X Esta pasta nao e um repositorio Git!" -ForegroundColor Red
    Write-Host "  Execute: git init" -ForegroundColor Yellow
    exit 1
}

# Configurar Git (se necessário)
Write-Host "Configurando Git..." -ForegroundColor Yellow
git config --global user.email "l.moncaosilva@gmail.com"
git config --global user.name "LMONCAO"
Write-Host "✅ Git configurado!" -ForegroundColor Green
Write-Host ""

# Verificar status
Write-Host "Verificando status do Git..." -ForegroundColor Yellow
git status
Write-Host ""

# Perguntar se deseja continuar
Write-Host "Deseja continuar com commit e push? (S/N)" -ForegroundColor Yellow
$continuar = Read-Host

if ($continuar -ne "S" -and $continuar -ne "s") {
    Write-Host "Operacao cancelada." -ForegroundColor Yellow
    exit 0
}

# Adicionar todos os arquivos
Write-Host ""
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Fazer commit
Write-Host "Fazendo commit..." -ForegroundColor Yellow
$mensagem = "Adicionar meta tag Google Search Console"
git commit -m $mensagem

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Erro ao fazer commit!" -ForegroundColor Red
    Write-Host "  Verifique se ha mudancas para commitar" -ForegroundColor Yellow
    exit 1
}

# Aviso sobre token
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  IMPORTANTE: AUTENTICACAO GITHUB" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "GitHub nao aceita mais senha!" -ForegroundColor Red
Write-Host "Voce precisa usar um Personal Access Token (PAT)." -ForegroundColor Yellow
Write-Host ""
Write-Host "Se ainda nao tem um token:" -ForegroundColor Cyan
Write-Host "  1. Acesse: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "  2. Clique em 'Generate new token (classic)'" -ForegroundColor White
Write-Host "  3. Selecione permissao 'repo'" -ForegroundColor White
Write-Host "  4. Copie o token gerado" -ForegroundColor White
Write-Host ""
Write-Host "Quando pedir:" -ForegroundColor Cyan
Write-Host "  Username: LMONCAO" -ForegroundColor White
Write-Host "  Password: COLE O TOKEN (nao a senha!)" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Enter para continuar..." -ForegroundColor Yellow
Read-Host

# Fazer push
Write-Host ""
Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  Quando pedir senha, cole o TOKEN!" -ForegroundColor Yellow
Write-Host ""
git push origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  PUSH CONCLUIDO COM SUCESSO!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "  1. No Cloud Shell, execute:" -ForegroundColor Cyan
    Write-Host "     cd ~/Monpec_GestaoRural" -ForegroundColor White
    Write-Host "     git pull origin master" -ForegroundColor White
    Write-Host "     chmod +x deploy_completo_cloud_shell.sh" -ForegroundColor White
    Write-Host "     ./deploy_completo_cloud_shell.sh" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "X Erro ao fazer push!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possiveis causas:" -ForegroundColor Yellow
    Write-Host "  1. Token invalido ou expirado" -ForegroundColor White
    Write-Host "  2. Token sem permissao 'repo'" -ForegroundColor White
    Write-Host "  3. Usuario ou senha incorretos" -ForegroundColor White
    Write-Host ""
    Write-Host "Solucao:" -ForegroundColor Yellow
    Write-Host "  - Crie um novo token em: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "  - Use o TOKEN como senha (nao sua senha do GitHub)" -ForegroundColor White
    Write-Host ""
    exit 1
}

