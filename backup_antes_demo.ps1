# ========================================
# BACKUP SEGURO ANTES DE CONFIGURAR DEMO
# ========================================

Write-Host ""
Write-Host "CRIANDO BACKUP SEGURO DO SISTEMA" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: Arquivo manage.py nao encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script no diretorio raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Obter data e hora para nome do backup
$dataBackup = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$nomeBackup = "backup_antes_demo_$dataBackup"
$pastaBackup = ".\backups\$nomeBackup"

Write-Host "Criando pasta de backup: $pastaBackup" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $pastaBackup | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\banco_dados" | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\codigo_fonte" | Out-Null
New-Item -ItemType Directory -Force -Path "$pastaBackup\configuracoes" | Out-Null

# 1. BACKUP DO BANCO DE DADOS (CRITICO)
Write-Host ""
Write-Host "1. Fazendo backup do banco de dados..." -ForegroundColor Cyan

if (Test-Path ".\db.sqlite3") {
    # Parar qualquer processo que esteja usando o banco
    Write-Host "   Verificando processos Python..." -ForegroundColor Yellow
    $processosPython = Get-Process python -ErrorAction SilentlyContinue
    if ($processosPython) {
        Write-Host "   ATENCAO: Processos Python detectados!" -ForegroundColor Yellow
        Write-Host "   Recomendado: Pare o servidor Django antes do backup" -ForegroundColor Yellow
        $continuar = Read-Host "   Continuar mesmo assim? (S/N)"
        if ($continuar -ne "S" -and $continuar -ne "s") {
            Write-Host "   Backup cancelado pelo usuario." -ForegroundColor Yellow
            exit 0
        }
    }
    
    # Copiar banco de dados
    Copy-Item -Path ".\db.sqlite3" -Destination "$pastaBackup\banco_dados\db.sqlite3" -Force
    Copy-Item -Path ".\db.sqlite3-shm" -Destination "$pastaBackup\banco_dados\db.sqlite3-shm" -Force -ErrorAction SilentlyContinue
    Copy-Item -Path ".\db.sqlite3-wal" -Destination "$pastaBackup\banco_dados\db.sqlite3-wal" -Force -ErrorAction SilentlyContinue
    
    # Verificar tamanho do backup
    $tamanhoBanco = (Get-Item "$pastaBackup\banco_dados\db.sqlite3").Length
    $tamanhoMB = [math]::Round($tamanhoBanco / 1MB, 2)
    Write-Host "   OK Banco de dados copiado ($tamanhoMB MB)" -ForegroundColor Green
} else {
    Write-Host "   AVISO: Banco de dados nao encontrado (db.sqlite3)" -ForegroundColor Yellow
}

# 2. BACKUP DE CONFIGURACOES IMPORTANTES
Write-Host ""
Write-Host "2. Fazendo backup de configuracoes..." -ForegroundColor Cyan

$arquivosConfig = @(
    "sistema_rural\settings.py",
    "sistema_rural\urls.py",
    "manage.py",
    "requirements.txt"
)

foreach ($arquivo in $arquivosConfig) {
    if (Test-Path $arquivo) {
        $nomeArquivo = Split-Path $arquivo -Leaf
        Copy-Item -Path $arquivo -Destination "$pastaBackup\configuracoes\$nomeArquivo" -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "   OK Configuracoes copiadas" -ForegroundColor Green

# 3. BACKUP DE SCRIPTS DE DEMO (para referencia)
Write-Host ""
Write-Host "3. Salvando scripts de demo..." -ForegroundColor Cyan
if (Test-Path ".\setup_demo.ps1") {
    Copy-Item -Path ".\setup_demo.ps1" -Destination "$pastaBackup\configuracoes\setup_demo.ps1" -Force
}
if (Test-Path ".\populate_test_data.py") {
    Copy-Item -Path ".\populate_test_data.py" -Destination "$pastaBackup\configuracoes\populate_test_data.py" -Force
}
Write-Host "   OK Scripts salvos" -ForegroundColor Green

# 4. Criar arquivo de informacoes do backup
Write-Host ""
Write-Host "4. Criando arquivo de informacoes..." -ForegroundColor Cyan

$infoBackup = @"
=== BACKUP ANTES DE CONFIGURAR DEMO ===
Data/Hora: $dataBackup
Nome: $nomeBackup

=== CONTEUDO DO BACKUP ===
- Banco de dados SQLite completo (db.sqlite3)
- Arquivos de configuracao do Django
- Scripts de demo (para referencia)

=== IMPORTANTE ===
Este backup foi criado ANTES de configurar a versao de demonstracao.
Se algo der errado, voce pode restaurar usando este backup.

=== RESTAURACAO ===
Para restaurar este backup:

1. PARAR o servidor Django (se estiver rodando)
2. Copiar o banco de dados de volta:
   Copy-Item ".\backups\$nomeBackup\banco_dados\db.sqlite3" -Destination ".\db.sqlite3" -Force
   Copy-Item ".\backups\$nomeBackup\banco_dados\db.sqlite3-shm" -Destination ".\db.sqlite3-shm" -Force
   Copy-Item ".\backups\$nomeBackup\banco_dados\db.sqlite3-wal" -Destination ".\db.sqlite3-wal" -Force

3. Verificar se esta funcionando:
   python manage.py migrate
   python manage.py runserver

=== SEGURANCA ===
- Este backup contem TODOS os seus dados atuais
- Mantenha este backup seguro
- Nao compartilhe este backup com ninguem
- O backup esta localizado em: $pastaBackup

=== PROXIMOS PASSOS ===
Agora voce pode executar: .\setup_demo.ps1
Os dados de demo serao ADICIONADOS ao banco, nao substituirao dados existentes.
"@

$infoBackup | Out-File -FilePath "$pastaBackup\INFO_BACKUP.txt" -Encoding UTF8
Write-Host "   OK Arquivo de informacoes criado" -ForegroundColor Green

# 5. Calcular tamanho total
Write-Host ""
Write-Host "Calculando tamanho do backup..." -ForegroundColor Cyan
$tamanhoTotal = (Get-ChildItem -Path $pastaBackup -Recurse -File | Measure-Object -Property Length -Sum).Sum
$tamanhoMB = [math]::Round($tamanhoTotal / 1MB, 2)

# 6. Resumo final
Write-Host ""
Write-Host "===================================" -ForegroundColor Yellow
Write-Host "BACKUP CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Localizacao: $pastaBackup" -ForegroundColor Cyan
Write-Host "Tamanho: $tamanhoMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "SEU SISTEMA ESTA PROTEGIDO!" -ForegroundColor Green
Write-Host ""
Write-Host "Agora voce pode executar:" -ForegroundColor Yellow
Write-Host "   .\setup_demo.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Os dados de demo serao ADICIONADOS, nao substituirao seus dados!" -ForegroundColor Cyan
Write-Host ""

