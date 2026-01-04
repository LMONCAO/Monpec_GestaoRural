# Script para aplicar migration 0077 diretamente via SQL
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/sistema-rural:latest"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  APLICAR MIGRATION 0077 (DIRETO SQL)" -ForegroundColor Cyan
Write-Host "  (mercadopago_customer_id)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "[2/4] Criando script SQL para adicionar colunas..." -ForegroundColor Yellow

# Script Python para verificar e criar as colunas
$script = @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Verificar se mercadopago_customer_id existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'gestao_rural_assinaturacliente' 
        AND column_name = 'mercadopago_customer_id'
    """)
    existe_customer = cursor.fetchone() is not None
    
    # Verificar se mercadopago_subscription_id existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'gestao_rural_assinaturacliente' 
        AND column_name = 'mercadopago_subscription_id'
    """)
    existe_subscription = cursor.fetchone() is not None
    
    if not existe_customer:
        print("Criando coluna mercadopago_customer_id...")
        cursor.execute("""
            ALTER TABLE gestao_rural_assinaturacliente 
            ADD COLUMN mercadopago_customer_id VARCHAR(120) NULL
        """)
        print("✅ mercadopago_customer_id criada")
    else:
        print("✅ mercadopago_customer_id já existe")
    
    if not existe_subscription:
        print("Criando coluna mercadopago_subscription_id...")
        cursor.execute("""
            ALTER TABLE gestao_rural_assinaturacliente 
            ADD COLUMN mercadopago_subscription_id VARCHAR(120) NULL
        """)
        print("✅ mercadopago_subscription_id criada")
    else:
        print("✅ mercadopago_subscription_id já existe")
    
    # Criar índices se não existirem
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx 
            ON gestao_rural_assinaturacliente(mercadopago_customer_id)
        """)
        print("✅ Índice para mercadopago_customer_id criado/verificado")
    except Exception as e:
        print(f"ℹ️  Índice para mercadopago_customer_id: {e}")
    
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS gestao_rura_mercado_3577a7_idx 
            ON gestao_rural_assinaturacliente(mercadopago_subscription_id)
        """)
        print("✅ Índice para mercadopago_subscription_id criado/verificado")
    except Exception as e:
        print(f"ℹ️  Índice para mercadopago_subscription_id: {e}")
    
    print("✅ Todas as colunas e índices estão prontos!")
"@

Write-Host ""
Write-Host "[3/4] Criando job no Cloud Run..." -ForegroundColor Yellow

# Deletar job anterior se existir
gcloud run jobs delete aplicar-migration-0077-direto --region=$REGION --quiet 2>$null

# Criar job
$CLOUD_SQL_CONN = "$PROJECT_ID`:$REGION`:monpec-db"

gcloud run jobs create aplicar-migration-0077-direto `
    --region=$REGION `
    --image=$IMAGE_NAME `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONN" `
    --set-cloudsql-instances=$CLOUD_SQL_CONN `
    --command="python" `
    --args="-c",$script `
    --max-retries=1 `
    --memory=2Gi `
    --cpu=2 `
    --task-timeout=300

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha ao criar job!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/4] Executando job..." -ForegroundColor Yellow
gcloud run jobs execute aplicar-migration-0077-direto --region=$REGION --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha ao executar!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Verificando logs..." -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migration-0077-direto" --limit=30 --format="value(textPayload)" --freshness=5m

Write-Host ""
Write-Host "Limpando job..." -ForegroundColor Yellow
gcloud run jobs delete aplicar-migration-0077-direto --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ MIGRATION APLICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Teste acessando: https://monpec-29862706245.us-central1.run.app/dashboard/" -ForegroundColor Green
Write-Host ""


