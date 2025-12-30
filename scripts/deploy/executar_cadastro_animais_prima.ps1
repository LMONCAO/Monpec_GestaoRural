# Script para executar cadastro de animais da Prima
# Propriedade: 8

Write-Host "🐄 CADASTRO DE ANIMAIS DA PRIMA" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""

# Verificar se Python está disponível
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python não encontrado no PATH!" -ForegroundColor Red
    Write-Host "Por favor, execute manualmente:" -ForegroundColor Yellow
    Write-Host "python manage.py cadastrar_animais_prima --propriedade 8" -ForegroundColor Cyan
    exit 1
}

Write-Host "📋 Lendo arquivo: c:\Users\joaoz\Downloads\animais prima.txt" -ForegroundColor Cyan

# Contar linhas do arquivo
$arquivoPath = "c:\Users\joaoz\Downloads\animais prima.txt"
if (Test-Path $arquivoPath) {
    $linhas = (Get-Content $arquivoPath | Measure-Object -Line).Lines
    Write-Host "✅ Arquivo encontrado com $linhas códigos" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo não encontrado: $arquivoPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⚠️  ATENÇÃO:" -ForegroundColor Yellow
Write-Host "  - Propriedade ID: 8" -ForegroundColor White
Write-Host "  - Animais existentes em outras propriedades serão EXCLUÍDOS" -ForegroundColor White
Write-Host "  - Serão cadastrados $linhas animais com dados completos" -ForegroundColor White
Write-Host ""

$confirmar = Read-Host "Deseja continuar? (s/N)"
if ($confirmar -ne "s" -and $confirmar -ne "S") {
    Write-Host "❌ Operação cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🚀 Executando cadastro..." -ForegroundColor Green
Write-Host ""

# Executar o comando
# Primeiro vamos tentar encontrar um usuário admin
Write-Host "🔍 Verificando usuários disponíveis..." -ForegroundColor Cyan

python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.filter(is_staff=True).first(); print(f'USER_ID={u.id}' if u else 'USER_ID=1')" | ForEach-Object {
    if ($_ -match 'USER_ID=(\d+)') {
        $script:userId = $matches[1]
    }
}

if (-not $script:userId) {
    Write-Host "⚠️  Não foi possível determinar o usuário automaticamente" -ForegroundColor Yellow
    Write-Host "Executando com confirmação interativa..." -ForegroundColor Cyan
    python manage.py cadastrar_animais_prima --propriedade 8
} else {
    Write-Host "✅ Usando usuário ID: $script:userId" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executando com confirmação automática..." -ForegroundColor Cyan
    python manage.py cadastrar_animais_prima --propriedade 8 --usuario $script:userId
}

Write-Host ""
Write-Host "✅ Processo concluído!" -ForegroundColor Green



