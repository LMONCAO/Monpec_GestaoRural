# Script de Setup Completo do Sistema MonPEC
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETO DO SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Criar pasta scripts
Write-Host "[1/5] Criando pasta scripts..." -ForegroundColor Yellow
if (-not (Test-Path "scripts")) {
    New-Item -ItemType Directory -Path "scripts" | Out-Null
    Write-Host "OK - Pasta scripts criada" -ForegroundColor Green
} else {
    Write-Host "OK - Pasta scripts já existe" -ForegroundColor Green
}
Write-Host ""

# Passo 2: Organizar arquivos temporários
Write-Host "[2/5] Organizando arquivos temporários..." -ForegroundColor Yellow
$arquivosTemp = Get-ChildItem -Path . -Filter "*.py" -File | Where-Object {
    $_.Name -match "^testar_|^verificar_|^corrigir_|^criar_admin|^atualizar_|^aplicar_|^executar_|^fix_|^redefinir_|^diagnosticar_|^configurar_|^autenticar_|^fazer_|^listar_|^create_superuser" -and
    $_.Name -notin @('manage.py', 'SETUP_COMPLETO.py', 'APLICAR_MELHORIAS.py', 'limpar_arquivos_temporarios.py', 'corrigir_problemas_seguranca.py', 'auditoria_sistema.py')
}

$movidos = 0
foreach ($arquivo in $arquivosTemp) {
    try {
        $destino = Join-Path "scripts" $arquivo.Name
        if (Test-Path $destino) {
            $base = [System.IO.Path]::GetFileNameWithoutExtension($arquivo.Name)
            $ext = $arquivo.Extension
            $contador = 1
            while (Test-Path $destino) {
                $destino = Join-Path "scripts" "${base}_${contador}${ext}"
                $contador++
            }
        }
        Move-Item -Path $arquivo.FullName -Destination $destino -Force
        Write-Host "  Movido: $($arquivo.Name)" -ForegroundColor Gray
        $movidos++
    } catch {
        Write-Host "  Erro ao mover $($arquivo.Name): $_" -ForegroundColor Red
    }
}
Write-Host "OK - $movidos arquivo(s) movido(s)" -ForegroundColor Green
Write-Host ""

# Passo 3: Criar .env
Write-Host "[3/5] Verificando arquivo .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "OK - Arquivo .env criado a partir do .env.example" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANTE: Edite o arquivo .env com seus valores reais!" -ForegroundColor Yellow
    } else {
        Write-Host "AVISO - .env.example não encontrado. Criando .env básico..." -ForegroundColor Yellow
        @"
# Configurações do Sistema MonPEC
# ⚠️ NUNCA commite este arquivo com valores reais!

DEBUG=True
SECRET_KEY=sua-secret-key-aqui

# Banco de Dados
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=sua-senha-aqui
DB_HOST=localhost
DB_PORT=5432

# Administrador
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@monpec.com.br
ADMIN_PASSWORD=sua-senha-admin-aqui

# Demo
DEMO_USER_PASSWORD=monpec

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu-token-aqui
MERCADOPAGO_PUBLIC_KEY=sua-public-key-aqui
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "OK - Arquivo .env básico criado" -ForegroundColor Green
    }
} else {
    Write-Host "OK - Arquivo .env já existe" -ForegroundColor Green
}
Write-Host ""

# Passo 4: Instalar ferramentas
Write-Host "[4/5] Verificando ferramentas de qualidade..." -ForegroundColor Yellow
if (Test-Path "requirements-dev.txt") {
    Write-Host "Instalando ferramentas de desenvolvimento..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Ferramentas instaladas" -ForegroundColor Green
    } else {
        Write-Host "AVISO - Alguns pacotes podem não ter sido instalados" -ForegroundColor Yellow
    }
} else {
    Write-Host "AVISO - requirements-dev.txt não encontrado" -ForegroundColor Yellow
}
Write-Host ""

# Passo 5: Verificar configurações
Write-Host "[5/5] Verificando configurações..." -ForegroundColor Yellow
$configs = @{
    ".pylintrc" = "Pylint"
    ".flake8" = "Flake8"
    "pyproject.toml" = "Black/Isort"
    "requirements-dev.txt" = "Dependências de desenvolvimento"
}

foreach ($arquivo in $configs.Keys) {
    if (Test-Path $arquivo) {
        Write-Host "OK - $($configs[$arquivo]) configurado" -ForegroundColor Green
    } else {
        Write-Host "AVISO - $($configs[$arquivo]) não encontrado ($arquivo)" -ForegroundColor Yellow
    }
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Edite o arquivo .env com seus valores reais"
Write-Host "2. Execute: python manage.py runserver"
Write-Host "3. Revise os arquivos em scripts/"
Write-Host ""
Read-Host "Pressione Enter para continuar"






