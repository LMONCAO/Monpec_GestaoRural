# ==========================================
# Script de Configuração PostgreSQL Local
# Para Windows PowerShell
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Configuração PostgreSQL Local" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se PostgreSQL está instalado
Write-Host "1. Verificando instalação do PostgreSQL..." -ForegroundColor Yellow
$pgPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $pgPath) {
    Write-Host "❌ PostgreSQL não encontrado no PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale o PostgreSQL:" -ForegroundColor Yellow
    Write-Host "  1. Baixe em: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  2. Durante a instalação, anote a senha do usuário 'postgres'" -ForegroundColor White
    Write-Host "  3. Adicione o PostgreSQL ao PATH do sistema" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou instale via Chocolatey:" -ForegroundColor Yellow
    Write-Host "  choco install postgresql" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ PostgreSQL encontrado!" -ForegroundColor Green
Write-Host ""

# Solicitar informações do banco
Write-Host "2. Configuração do banco de dados:" -ForegroundColor Yellow
$dbName = Read-Host "Nome do banco de dados (padrão: monpec_db_local)"
if ([string]::IsNullOrWhiteSpace($dbName)) {
    $dbName = "monpec_db_local"
}

$dbUser = Read-Host "Usuário PostgreSQL (padrão: postgres)"
if ([string]::IsNullOrWhiteSpace($dbUser)) {
    $dbUser = "postgres"
}

$dbPassword = Read-Host "Senha do PostgreSQL" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

$dbHost = Read-Host "Host (padrão: localhost)"
if ([string]::IsNullOrWhiteSpace($dbHost)) {
    $dbHost = "localhost"
}

$dbPort = Read-Host "Porta (padrão: 5432)"
if ([string]::IsNullOrWhiteSpace($dbPort)) {
    $dbPort = "5432"
}

Write-Host ""
Write-Host "3. Criando banco de dados..." -ForegroundColor Yellow

# Criar variável de ambiente temporária para senha
$env:PGPASSWORD = $dbPasswordPlain

# Criar banco de dados
$createDbQuery = "CREATE DATABASE $dbName;"
try {
    psql -U $dbUser -h $dbHost -p $dbPort -d postgres -c $createDbQuery 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Banco de dados '$dbName' criado com sucesso!" -ForegroundColor Green
    } else {
        # Pode ser que o banco já exista, verificar
        $checkDbQuery = "SELECT 1 FROM pg_database WHERE datname = '$dbName';"
        $result = psql -U $dbUser -h $dbHost -p $dbPort -d postgres -t -c $checkDbQuery 2>&1
        if ($result -match "1") {
            Write-Host "⚠️  Banco de dados '$dbName' já existe. Continuando..." -ForegroundColor Yellow
        } else {
            Write-Host "❌ Erro ao criar banco de dados. Verifique as credenciais." -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Erro ao criar banco de dados: $_" -ForegroundColor Red
    exit 1
} finally {
    Remove-Item Env:\PGPASSWORD
}

Write-Host ""
Write-Host "4. Atualizando arquivo .env.local..." -ForegroundColor Yellow

# Atualizar .env.local
$envContent = @"
# ==========================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO LOCAL
# PostgreSQL Local (igual ao Google Cloud)
# ==========================================

# Modo de debug
DEBUG=True

# Chave secreta Django (desenvolvimento)
SECRET_KEY=django-insecure-dev-local-2025-temp-key-change-in-production

# ==========================================
# CONFIGURAÇÕES DO BANCO DE DADOS - POSTGRESQL LOCAL
# ==========================================

# PostgreSQL Local
DB_NAME=$dbName
DB_USER=$dbUser
DB_PASSWORD=$dbPasswordPlain
DB_HOST=$dbHost
DB_PORT=$dbPort

# ==========================================
# CONFIGURAÇÕES DE EMAIL (OPCIONAL)
# ==========================================

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# ==========================================
# CONFIGURAÇÕES DO MERCADO PAGO (OPCIONAL)
# ==========================================

MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_PUBLIC_KEY=
MERCADOPAGO_WEBHOOK_SECRET=
"@

$envContent | Out-File -FilePath ".env.local" -Encoding UTF8
Write-Host "✅ Arquivo .env.local atualizado!" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Certifique-se de que o arquivo .env.local está na raiz do projeto" -ForegroundColor White
Write-Host "  2. Execute: python manage.py migrate" -ForegroundColor White
Write-Host "  3. Execute: python manage.py createsuperuser (se necessário)" -ForegroundColor White
Write-Host ""

