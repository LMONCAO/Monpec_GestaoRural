# Verificar e criar coluna mercadopago_customer_id
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "🔍 Verificando se coluna existe..." -ForegroundColor Yellow

gcloud run jobs delete verificar-mercadopago --region=$REGION --quiet 2>$null

# Script que verifica e cria se necessário
$script = @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection
c = connection.cursor()

# Verificar se coluna existe
c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_customer_id'")
r = c.fetchone()

if r:
    print('✅ Coluna mercadopago_customer_id JÁ EXISTE')
else:
    print('❌ Coluna mercadopago_customer_id NÃO EXISTE - Criando...')
    try:
        c.execute("ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL")
        c.execute("CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)")
        print('✅ Coluna mercadopago_customer_id CRIADA COM SUCESSO')
    except Exception as e:
        print(f'❌ ERRO ao criar coluna: {e}')
"@

gcloud run jobs create verificar-mercadopago `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="-c","$script" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando..." -ForegroundColor Yellow
gcloud run jobs execute verificar-mercadopago --region=$REGION --wait

Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-mercadopago" `
  --limit=30 `
  --format="value(textPayload)" `
  --freshness=5m

gcloud run jobs delete verificar-mercadopago --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Verificação concluída!" -ForegroundColor Green

