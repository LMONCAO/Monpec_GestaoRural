# Script para adicionar todos os arquivos ao Git e preparar para commit
# Use este script se o GitHub Desktop não estiver detectando os arquivos

Write-Host "=== Adicionando arquivos ao Git ===" -ForegroundColor Cyan

# Verificar se Git está disponível
$gitPath = $null
$possiblePaths = @(
    "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles\GitHub Desktop\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles (x86)\GitHub Desktop\resources\app\git\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe",
    "$env:ProgramFiles (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
)

# Procurar Git do GitHub Desktop (pode ter versão no caminho)
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
}

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
        Write-Host "Por favor, use o GitHub Desktop para adicionar os arquivos." -ForegroundColor Yellow
        Write-Host "Ou instale o Git: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Git encontrado em: $gitPath" -ForegroundColor Green

# Função para executar comandos Git
function Invoke-Git {
    param([string[]]$Arguments)
    Write-Host "Executando: git $($Arguments -join ' ')" -ForegroundColor Gray
    & $gitPath $Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AVISO: Comando retornou código de saída $LASTEXITCODE" -ForegroundColor Yellow
    }
}

# Verificar status atual
Write-Host "`nVerificando status do repositório..." -ForegroundColor Cyan
Invoke-Git @("status")

# Adicionar todos os arquivos (exceto os ignorados pelo .gitignore)
Write-Host "`nAdicionando arquivos ao staging..." -ForegroundColor Cyan
Invoke-Git @("add", ".")

# Verificar o que foi adicionado
Write-Host "`nArquivos adicionados:" -ForegroundColor Cyan
Invoke-Git @("status", "--short")

# Mostrar resumo
Write-Host "`n=== Resumo ===" -ForegroundColor Green
Write-Host "Arquivos foram adicionados ao staging area do Git." -ForegroundColor Green
Write-Host "`nPróximos passos:" -ForegroundColor Yellow
Write-Host "1. Abra o GitHub Desktop" -ForegroundColor White
Write-Host "2. Você deve ver os arquivos na aba 'Changes'" -ForegroundColor White
Write-Host "3. Adicione uma mensagem de commit" -ForegroundColor White
Write-Host "4. Clique em 'Commit to master' (ou 'Commit to main')" -ForegroundColor White
Write-Host "5. Clique em 'Publish branch' ou 'Push origin'" -ForegroundColor White

Write-Host "`n=== Concluído! ===" -ForegroundColor Green

