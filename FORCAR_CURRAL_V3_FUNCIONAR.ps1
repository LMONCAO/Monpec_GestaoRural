# Script para FORÇAR a página Curral V3 a funcionar
# Faz commit, push e deploy automaticamente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FORÇAR CURRAL V3 A FUNCIONAR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivos
Write-Host "Verificando arquivos da tela Curral V3..." -ForegroundColor Yellow
$arquivosV3 = @(
    "templates\gestao_rural\curral_dashboard_v3.html",
    "gestao_rural\views_curral.py",
    "gestao_rural\urls.py",
    "sistema_rural\urls.py"
)

$todosPresentes = $true
foreach ($arquivo in $arquivosV3) {
    if (Test-Path $arquivo) {
        Write-Host "  [OK] $arquivo" -ForegroundColor Green
    } else {
        Write-Host "  [ERRO] $arquivo NÃO ENCONTRADO!" -ForegroundColor Red
        $todosPresentes = $false
    }
}

if (-not $todosPresentes) {
    Write-Host ""
    Write-Host "ERRO: Arquivos faltando!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Todos os arquivos estão presentes!" -ForegroundColor Green
Write-Host ""

# Procurar Git
Write-Host "Procurando Git..." -ForegroundColor Yellow
$gitPath = $null

# Procurar Git do GitHub Desktop
$githubDesktopGit = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($githubDesktopGit) {
    $gitPath = $githubDesktopGit.FullName
    Write-Host "  [OK] Git do GitHub Desktop encontrado!" -ForegroundColor Green
}

# Procurar em outros locais
if (-not $gitPath) {
    $possiblePaths = @(
        "$env:ProgramFiles\Git\cmd\git.exe",
        "$env:ProgramFiles\Git\bin\git.exe",
        "${env:ProgramFiles(x86)}\Git\cmd\git.exe",
        "${env:ProgramFiles(x86)}\Git\bin\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $gitPath = $path
            Write-Host "  [OK] Git encontrado em: $path" -ForegroundColor Green
            break
        }
    }
}

# Tentar no PATH
if (-not $gitPath) {
    try {
        $gitPath = (Get-Command git -ErrorAction Stop).Source
        Write-Host "  [OK] Git encontrado no PATH!" -ForegroundColor Green
    } catch {
        Write-Host "  [AVISO] Git não encontrado, pulando commit/push" -ForegroundColor Yellow
        Write-Host "  Você precisará fazer commit manualmente antes do deploy" -ForegroundColor Yellow
    }
}

# Função para executar Git
function Invoke-Git {
    param([string[]]$Arguments)
    if ($gitPath) {
        & $gitPath $Arguments
        return $LASTEXITCODE
    } else {
        return 1
    }
}

# Tentar fazer commit e push se Git foi encontrado
if ($gitPath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  PASSO 1/3: COMMIT E PUSH" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar status
    Write-Host "Verificando status do repositório..." -ForegroundColor Yellow
    $status = Invoke-Git @("status", "--porcelain")
    
    if ($status -eq 0) {
        $hasChanges = (Invoke-Git @("status", "--porcelain")) -ne ""
        
        if ($hasChanges) {
            Write-Host "Há alterações não commitadas. Fazendo commit..." -ForegroundColor Yellow
            
            # Adicionar arquivos
            Invoke-Git @("add", ".") | Out-Null
            
            # Commit
            $mensagem = "FORÇAR: Garantir que tela Curral V3 está no deploy - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            $commitResult = Invoke-Git @("commit", "-m", $mensagem)
            
            if ($commitResult -eq 0) {
                Write-Host "Commit realizado com sucesso!" -ForegroundColor Green
                
                # Push
                Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
                $pushResult = Invoke-Git @("push", "origin", "master")
                
                if ($pushResult -eq 0) {
                    Write-Host "Push realizado com sucesso!" -ForegroundColor Green
                } else {
                    Write-Host "AVISO: Push falhou, mas continuando com deploy..." -ForegroundColor Yellow
                    Write-Host "Você pode precisar fazer push manualmente depois" -ForegroundColor Yellow
                }
            } else {
                Write-Host "AVISO: Commit falhou ou não há mudanças, continuando..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "Nenhuma alteração pendente." -ForegroundColor Green
        }
    } else {
        Write-Host "AVISO: Não foi possível verificar status, continuando com deploy..." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "⚠️  ATENÇÃO: Git não encontrado!" -ForegroundColor Yellow
    Write-Host "   O deploy será feito, mas certifique-se de que os arquivos estão no GitHub!" -ForegroundColor Yellow
    Write-Host "   Use GitHub Desktop ou outro cliente Git para fazer commit e push." -ForegroundColor Yellow
    Write-Host ""
}

# Verificar gcloud
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 2/3: VERIFICANDO GCLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "ERRO: Google Cloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "Google Cloud CLI encontrado!" -ForegroundColor Green
Write-Host ""

# Configurar projeto
$PROJECT_ID = "monpec-sistema-rural"
Write-Host "Configurando projeto: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host ""

# Build
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 3/3: BUILD E DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "BUILD DA IMAGEM DOCKER" -ForegroundColor Yellow
Write-Host "Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host "O build usa o código do repositório GitHub." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag gcr.io/$PROJECT_ID/monpec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "DEPLOY NO CLOUD RUN" -ForegroundColor Yellow
Write-Host "Isso pode levar 2-3 minutos..." -ForegroundColor Yellow
Write-Host ""

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>$null

# Gerar SECRET_KEY
$SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
if (-not $SECRET_KEY) {
    $SECRET_KEY = "temp-key-$(Get-Random)"
}

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY"

if ($CONNECTION_NAME) {
    $envVars += ",DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
    
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
} else {
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Deploy falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do serviço:" -ForegroundColor Cyan
Write-Host "  $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "Teste a tela Curral V3:" -ForegroundColor Yellow
Write-Host "  $SERVICE_URL/propriedade/1/curral/v3/" -ForegroundColor White
Write-Host ""
Write-Host "Se a tela não aparecer, verifique:" -ForegroundColor Yellow
Write-Host "  1. Se os arquivos estão commitados no GitHub" -ForegroundColor White
Write-Host "  2. Se o build usou a versão mais recente do código" -ForegroundColor White
Write-Host "  3. Os logs do Cloud Run para erros" -ForegroundColor White
Write-Host ""

