# Script para fazer commit e push para GitHub
# Execute no PowerShell na pasta do projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FAZER PUSH PARA GITHUB" -ForegroundColor Cyan
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

# Verificar status
Write-Host "Verificando status do Git..." -ForegroundColor Yellow
git status

Write-Host ""
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
$mensagem = "Corrigir: remover django-logging, adicionar documentacao de deploy e verificacao Google Search Console"
git commit -m $mensagem

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Erro ao fazer commit!" -ForegroundColor Red
    Write-Host "  Verifique se ha mudancas para commitar" -ForegroundColor Yellow
    exit 1
}

# Fazer push
Write-Host ""
Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
git push origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  PUSH CONCLUIDO COM SUCESSO!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Clonar no Cloud Shell: git clone https://github.com/LMONCAO/Monpec_GestaoRural.git" -ForegroundColor Cyan
    Write-Host "  2. Fazer deploy no Cloud Shell" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "X Erro ao fazer push!" -ForegroundColor Red
    Write-Host "  Verifique suas credenciais do GitHub" -ForegroundColor Yellow
    exit 1
}

