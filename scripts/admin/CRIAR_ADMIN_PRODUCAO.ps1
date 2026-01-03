# 🚀 Script para Criar Admin em Produção
# Cria o usuário admin com senha L6171r12@@

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "👤 CRIANDO ADMIN EM PRODUÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$JOB_NAME = "criar-admin-producao"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Verificar projeto
Write-Host "▶ Configurando projeto..." -ForegroundColor Blue
gcloud config set project $PROJECT_ID --quiet 2>&1 | Out-Null

# Variáveis de ambiente
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Adicionar outras variáveis se necessário
$dbName = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>&1 | Select-String -Pattern "DB_NAME" | ForEach-Object { ($_ -split "=")[1] }
if ($dbName) {
    $envVars += "DB_NAME=$dbName"
}

$envVarsString = $envVars -join ","

Write-Host "▶ Criando/atualizando job para criar admin..." -ForegroundColor Blue

# Criar ou atualizar job
$jobArgs = @(
    "run", "jobs", "create", $JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $envVarsString,
    "--memory", "1Gi",
    "--cpu", "1",
    "--max-retries", "1",
    "--task-timeout", "300",
    "--command", "python",
    "--args", "criar_admin_producao.py",
    "--quiet"
)

# Verificar se job existe
$jobExists = gcloud run jobs describe $JOB_NAME --region $REGION 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Job já existe, atualizando..." -ForegroundColor Gray
    $jobArgs[2] = "update"
} else {
    Write-Host "   Criando novo job..." -ForegroundColor Gray
}

$createResult = & gcloud $jobArgs 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar/atualizar job!" -ForegroundColor Red
    Write-Host $createResult
    exit 1
}

Write-Host "✅ Job criado/atualizado!" -ForegroundColor Green
Write-Host ""

# Verificar se o arquivo criar_admin_producao.py existe na imagem
# Se não existir, precisamos fazer upload ou usar outro método
Write-Host "▶ Executando criação do admin..." -ForegroundColor Blue
Write-Host "   Aguarde..." -ForegroundColor Gray
Write-Host ""

$executeResult = gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Admin criado/atualizado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
    Write-Host "   Usuário: admin" -ForegroundColor White
    Write-Host "   Senha: L6171r12@@" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Acesse: https://monpec.com.br/login/" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Verificando logs..." -ForegroundColor Yellow
    Write-Host ""
    
    # Tentar método alternativo: executar diretamente via Cloud Run
    Write-Host "▶ Tentando método alternativo..." -ForegroundColor Blue
    
    # Criar script inline
    $scriptContent = @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'
if User.objects.filter(username=username).exists():
    usuario = User.objects.get(username=username)
    usuario.set_password(password)
    usuario.is_superuser = True
    usuario.is_staff = True
    usuario.is_active = True
    usuario.email = email
    usuario.save()
    print(f'✅ Superusuário atualizado!')
else:
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superusuário criado!')
print(f'Usuário: {username}')
print(f'Senha: {password}')
"@
    
    # Salvar script temporário
    $tempScript = "temp_criar_admin.py"
    $scriptContent | Out-File -FilePath $tempScript -Encoding UTF8
    
    Write-Host "   Script criado. Execute manualmente:" -ForegroundColor Gray
    Write-Host "   python $tempScript" -ForegroundColor White
    Write-Host ""
}

Write-Host ""








