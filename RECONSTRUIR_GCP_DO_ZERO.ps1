# ========================================
# RECONSTRUIR PROJETO GCP DO ZERO
# ⚠️ ATENÇÃO: Este script irá REMOVER recursos existentes e recriar tudo
# ========================================

param(
    [switch]$SkipDatabase = $false,  # Pular remoção do banco de dados (mais seguro)
    [switch]$Force = $false  # Pular confirmações (não recomendado)
)

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$JOB_NAME = "migrate-monpec"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$CLOUD_SQL_INSTANCE = "monpec-db"
$CLOUD_SQL_CONNECTION = "$PROJECT_ID:$REGION:$CLOUD_SQL_INSTANCE"

# Cores
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Blue }

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║  ⚠️  RECONSTRUÇÃO COMPLETA DO PROJETO GCP  ⚠️        ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""
Write-Warning "Este script irá:"
Write-Host "  1. ❌ Remover serviços Cloud Run existentes"
Write-Host "  2. ❌ Remover jobs Cloud Run existentes"
Write-Host "  3. ❌ Remover imagens Docker do Container Registry"
if (-not $SkipDatabase) {
    Write-Host "  4. ⚠️  REMOVER INSTÂNCIA DO BANCO DE DADOS (todos os dados serão perdidos!)"
} else {
    Write-Host "  4. ✅ Manter banco de dados (pulado)"
}
Write-Host "  5. ✅ Reconstruir tudo do zero"
Write-Host ""

if (-not $Force) {
    Write-Warning "⚠️  Você tem certeza que deseja continuar?"
    Write-Host "   Digite 'SIM' para confirmar: " -NoNewline -ForegroundColor Yellow
    $confirmation = Read-Host
    
    if ($confirmation -ne "SIM") {
        Write-Info "Operação cancelada pelo usuário."
        exit 0
    }
    
    if (-not $SkipDatabase) {
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  ⚠️  ATENÇÃO: BANCO DE DADOS SERÁ REMOVIDO  ⚠️       ║" -ForegroundColor Red
        Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
        Write-Warning "Todos os dados do banco de dados serão PERDIDOS PERMANENTEMENTE!"
        Write-Host "   Digite 'CONFIRMO' para continuar: " -NoNewline -ForegroundColor Red
        $dbConfirmation = Read-Host
        
        if ($dbConfirmation -ne "CONFIRMO") {
            Write-Info "Operação cancelada. Para manter o banco, execute com -SkipDatabase"
            exit 0
        }
    }
}

Write-Host ""
Write-Step "Iniciando processo de reconstrução..."
Write-Host ""

# Verificar se gcloud está instalado
$gcloudAvailable = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudAvailable) {
    Write-Error "❌ gcloud CLI não encontrado!"
    Write-Info "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar autenticação
Write-Step "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Warning "⚠ Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Falha na autenticação!"
        exit 1
    }
}
Write-Success "✅ Autenticado: $authCheck"

# Configurar projeto
Write-Step "Configurando projeto $PROJECT_ID..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao configurar projeto!"
    exit 1
}
Write-Success "✅ Projeto configurado!"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 1: LISTANDO RECURSOS EXISTENTES" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Listar serviços Cloud Run
Write-Step "Listando serviços Cloud Run..."
$services = gcloud run services list --region $REGION --project $PROJECT_ID --format="value(name)" 2>&1
if ($services) {
    Write-Info "Serviços encontrados:"
    $services | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Info "Nenhum serviço encontrado"
}
Write-Host ""

# Listar jobs Cloud Run
Write-Step "Listando jobs Cloud Run..."
$jobs = gcloud run jobs list --region $REGION --project $PROJECT_ID --format="value(name)" 2>&1
if ($jobs) {
    Write-Info "Jobs encontrados:"
    $jobs | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Info "Nenhum job encontrado"
}
Write-Host ""

# Listar imagens Docker
Write-Step "Listando imagens Docker..."
$images = gcloud container images list --repository gcr.io/$PROJECT_ID --format="value(name)" 2>&1
if ($images) {
    Write-Info "Repositórios encontrados:"
    $images | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Info "Nenhuma imagem encontrada"
}
Write-Host ""

# Listar instâncias Cloud SQL
if (-not $SkipDatabase) {
    Write-Step "Listando instâncias Cloud SQL..."
    $sqlInstances = gcloud sql instances list --project $PROJECT_ID --format="value(name)" 2>&1
    if ($sqlInstances) {
        Write-Info "Instâncias encontradas:"
        $sqlInstances | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    } else {
        Write-Info "Nenhuma instância encontrada"
    }
    Write-Host ""
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 2: REMOVENDO RECURSOS EXISTENTES" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Remover serviços Cloud Run
Write-Step "Removendo serviços Cloud Run..."
$servicesToDelete = gcloud run services list --region $REGION --project $PROJECT_ID --format="value(name)" 2>&1
if ($servicesToDelete) {
    foreach ($service in $servicesToDelete) {
        Write-Info "  Removendo serviço: $service"
        gcloud run services delete $service --region $REGION --project $PROJECT_ID --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "    ✅ Removido: $service"
        } else {
            Write-Warning "    ⚠️  Erro ao remover: $service (continuando...)"
        }
    }
} else {
    Write-Info "  Nenhum serviço para remover"
}
Write-Host ""

# Remover jobs Cloud Run
Write-Step "Removendo jobs Cloud Run..."
$jobsToDelete = gcloud run jobs list --region $REGION --project $PROJECT_ID --format="value(name)" 2>&1
if ($jobsToDelete) {
    foreach ($job in $jobsToDelete) {
        Write-Info "  Removendo job: $job"
        gcloud run jobs delete $job --region $REGION --project $PROJECT_ID --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "    ✅ Removido: $job"
        } else {
            Write-Warning "    ⚠️  Erro ao remover: $job (continuando...)"
        }
    }
} else {
    Write-Info "  Nenhum job para remover"
}
Write-Host ""

# Remover imagens Docker
Write-Step "Removendo imagens Docker..."
$repos = gcloud container images list --repository gcr.io/$PROJECT_ID --format="value(name)" 2>&1
if ($repos) {
    foreach ($repo in $repos) {
        Write-Info "  Removendo imagens do repositório: $repo"
        $tags = gcloud container images list-tags $repo --format="value(digest)" --limit=100 2>&1
        if ($tags) {
            foreach ($tag in $tags) {
                gcloud container images delete "$repo@$tag" --quiet --force-delete-tags 2>&1 | Out-Null
            }
        }
        # Tentar remover o repositório completo
        gcloud container images delete $repo --quiet --force-delete-tags 2>&1 | Out-Null
        Write-Success "    ✅ Removido: $repo"
    }
} else {
    Write-Info "  Nenhuma imagem para remover"
}
Write-Host ""

# Remover instância Cloud SQL (se não estiver pulado)
if (-not $SkipDatabase) {
    Write-Step "Removendo instância Cloud SQL..."
    $instanceExists = gcloud sql instances describe $CLOUD_SQL_INSTANCE --project $PROJECT_ID 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "  ⚠️  REMOVENDO INSTÂNCIA: $CLOUD_SQL_INSTANCE"
        Write-Warning "  ⚠️  TODOS OS DADOS SERÃO PERDIDOS!"
        gcloud sql instances delete $CLOUD_SQL_INSTANCE --project $PROJECT_ID --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Success "    ✅ Instância removida: $CLOUD_SQL_INSTANCE"
            Write-Info "    Aguardando 30 segundos para garantir remoção completa..."
            Start-Sleep -Seconds 30
        } else {
            Write-Warning "    ⚠️  Erro ao remover instância (pode não existir ou ter dependências)"
        }
    } else {
        Write-Info "  Instância não existe ou já foi removida"
    }
    Write-Host ""
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 3: HABILITANDO APIs NECESSÁRIAS" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Step "Habilitando APIs do Google Cloud..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Habilitando $api..."
    gcloud services enable $api --project $PROJECT_ID --quiet 2>&1 | Out-Null
}
Write-Success "✅ APIs habilitadas!"
Write-Host ""

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 4: RECRIANDO BANCO DE DADOS" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Criar instância Cloud SQL (se foi removida)
if (-not $SkipDatabase) {
    Write-Step "Criando nova instância Cloud SQL..."
    Write-Info "  Isso pode levar 5-10 minutos..."
    
    gcloud sql instances create $CLOUD_SQL_INSTANCE `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$REGION `
        --project=$PROJECT_ID `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Instância Cloud SQL criada!"
        
        # Criar banco de dados
        Write-Step "Criando banco de dados..."
        gcloud sql databases create monpec_db --instance=$CLOUD_SQL_INSTANCE --project=$PROJECT_ID 2>&1 | Out-Null
        
        # Criar usuário
        Write-Step "Criando usuário do banco de dados..."
        gcloud sql users create monpec_user --instance=$CLOUD_SQL_INSTANCE --password="Django2025@" --project=$PROJECT_ID 2>&1 | Out-Null
        
        Write-Success "✅ Banco de dados configurado!"
        Write-Host ""
        Write-Warning "⚠️  IMPORTANTE: Altere a senha do banco de dados após o primeiro deploy!"
    } else {
        Write-Error "❌ Erro ao criar instância Cloud SQL!"
        Write-Info "Verifique se a instância já existe ou se há problemas de permissão"
    }
} else {
    Write-Info "⚠️  Pulando criação do banco de dados (usando existente)"
}
Write-Host ""

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 5: CONSTRUINDO IMAGEM DOCKER" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Step "Verificando Dockerfile..."
if (-not (Test-Path "Dockerfile.prod")) {
    Write-Error "❌ Dockerfile.prod não encontrado!"
    Write-Info "Execute este script na raiz do projeto Django"
    exit 1
}

# Criar build-config.yaml
Write-Step "Criando configuração de build..."
$buildConfig = @"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '--no-cache', '--tag', 'gcr.io/`$PROJECT_ID/monpec:latest', '--file', 'Dockerfile.prod', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/`$PROJECT_ID/monpec:latest']
images:
  - 'gcr.io/`$PROJECT_ID/monpec:latest'
options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
timeout: '1800s'
"@

$buildConfig | Out-File -FilePath "build-config.yaml" -Encoding UTF8 -Force
Write-Success "✅ build-config.yaml criado!"

# Build da imagem
Write-Step "Construindo imagem Docker..."
Write-Warning "⚠️  Isso pode levar 10-15 minutos..."
Write-Host ""

gcloud builds submit --config=build-config.yaml --timeout=30m --project=$PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro no build da imagem!"
    exit 1
}

Write-Success "✅ Imagem Docker construída com sucesso!"
Write-Host ""

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 6: CRIANDO SERVIÇO CLOUD RUN" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Step "Criando serviço Cloud Run..."

# Variáveis de ambiente (você pode precisar ajustar estas)
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t",
    "DB_NAME=monpec_db",
    "DB_USER=monpec_user",
    "DB_PASSWORD=Django2025@",
    "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION",
    "PYTHONUNBUFFERED=1"
) -join ","

Write-Warning "⚠️  IMPORTANTE: Configure as variáveis de ambiente corretamente após o deploy!"
Write-Info "  Execute: .\CONFIGURAR_VARIAVEIS_GCP.ps1 ou configure manualmente no console"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME:latest `
    --platform managed `
    --region $REGION `
    --project $PROJECT_ID `
    --allow-unauthenticated `
    --set-env-vars $envVars `
    --set-cloudsql-instances=$CLOUD_SQL_CONNECTION `
    --memory=1Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1 `
    --port=8080

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao criar serviço Cloud Run!"
    exit 1
}

Write-Success "✅ Serviço Cloud Run criado!"
Write-Host ""

# Obter URL do serviço
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --project $PROJECT_ID --format='value(status.url)' 2>&1
if ($serviceUrl) {
    Write-Success "🌐 URL do serviço: $serviceUrl"
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "FASE 7: EXECUTANDO MIGRAÇÕES" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Step "Criando job de migração..."

gcloud run jobs create $JOB_NAME `
    --image ${IMAGE_NAME}:latest `
    --region $REGION `
    --project $PROJECT_ID `
    --set-env-vars $envVars `
    --command python `
    --args manage.py,migrate,--noinput `
    --max-retries 1 `
    --task-timeout 900 `
    --memory=2Gi `
    --cpu=2 `
    --set-cloudsql-instances=$CLOUD_SQL_CONNECTION

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao criar job de migração!"
    exit 1
}

Write-Success "✅ Job de migração criado!"

Write-Step "Executando migrações..."
Write-Warning "⚠️  Isso pode levar alguns minutos..."

gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

if ($LASTEXITCODE -ne 0) {
    Write-Warning "⚠️  Erro na execução das migrações!"
    Write-Info "Execute manualmente: gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID"
} else {
    Write-Success "✅ Migrações executadas com sucesso!"
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ RECONSTRUÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Info "📋 Próximos passos:"
Write-Host ""
Write-Host "1. Configure as variáveis de ambiente (se necessário):" -ForegroundColor Yellow
Write-Host "   .\CONFIGURAR_VARIAVEIS_GCP.ps1" -ForegroundColor Gray
Write-Host ""

if ($serviceUrl) {
    Write-Host "2. Acesse o sistema:" -ForegroundColor Yellow
    Write-Host "   $serviceUrl" -ForegroundColor Green
    Write-Host ""
}

Write-Host "3. Configure o domínio personalizado (se necessário):" -ForegroundColor Yellow
Write-Host "   gcloud run domain-mappings create --service $SERVICE_NAME --domain monpec.com.br --region $REGION" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Crie um superusuário:" -ForegroundColor Yellow
Write-Host "   .\criar_admin_cloud_run.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "5. Verifique os logs:" -ForegroundColor Yellow
Write-Host "   gcloud run services logs read $SERVICE_NAME --region $REGION --project $PROJECT_ID" -ForegroundColor Gray
Write-Host ""

Write-Success "🎉 Processo concluído!"
Write-Host ""







