# Script para atualizar o repositório no GitHub
# Repositório: https://github.com/LMONCAO/Monpec_GestaoRural

Write-Host "=== Atualizando repositório no GitHub ===" -ForegroundColor Cyan

# Verificar se Git está disponível
$gitPath = $null
$possiblePaths = @(
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe",
    "$env:ProgramFiles (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $gitPath = $path
        break
    }
}

if (-not $gitPath) {
    # Tentar encontrar git no PATH
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
    } catch {
        Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
        Write-Host "Por favor, instale o Git ou adicione-o ao PATH." -ForegroundColor Yellow
        Write-Host "Download: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Git encontrado em: $gitPath" -ForegroundColor Green

# Função para executar comandos Git
function Invoke-Git {
    param([string[]]$Arguments)
    & $gitPath $Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao executar: git $($Arguments -join ' ')" -ForegroundColor Red
        exit 1
    }
}

# Verificar status
Write-Host "`nVerificando status do repositório..." -ForegroundColor Cyan
Invoke-Git @("status")

# Atualizar remote para o repositório correto
Write-Host "`nAtualizando remote para Monpec_GestaoRural..." -ForegroundColor Cyan
Invoke-Git @("remote", "set-url", "origin", "https://github.com/LMONCAO/Monpec_GestaoRural.git")

# Verificar remote atualizado
Write-Host "`nVerificando remote configurado..." -ForegroundColor Cyan
Invoke-Git @("remote", "-v")

# Adicionar todos os arquivos
Write-Host "`nAdicionando arquivos ao staging..." -ForegroundColor Cyan
Invoke-Git @("add", ".")

# Verificar o que será commitado
Write-Host "`nArquivos prontos para commit:" -ForegroundColor Cyan
Invoke-Git @("status", "--short")

# Fazer commit (se houver alterações)
$status = Invoke-Git @("status", "--porcelain")
if ($status) {
    Write-Host "`nFazendo commit das alterações..." -ForegroundColor Cyan
    $commitMessage = "Atualização do projeto Monpec Gestão Rural"
    Invoke-Git @("commit", "-m", $commitMessage)
} else {
    Write-Host "`nNenhuma alteração para commitar." -ForegroundColor Yellow
}

# Fazer push para o GitHub
Write-Host "`nEnviando alterações para o GitHub..." -ForegroundColor Cyan
Write-Host "Isso pode solicitar suas credenciais do GitHub." -ForegroundColor Yellow
Invoke-Git @("push", "-u", "origin", "master")

Write-Host "`n=== Atualização concluída com sucesso! ===" -ForegroundColor Green
Write-Host "Repositório: https://github.com/LMONCAO/Monpec_GestaoRural" -ForegroundColor Cyan

