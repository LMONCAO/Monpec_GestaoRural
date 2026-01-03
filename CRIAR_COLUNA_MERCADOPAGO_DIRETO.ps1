# Criar coluna mercadopago_customer_id diretamente
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "🔧 Criando coluna mercadopago_customer_id..." -ForegroundColor Yellow

gcloud run jobs delete criar-mercadopago-col --region=$REGION --quiet 2>$null

# Script Python simples
$script = "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;c=connection.cursor();"
$script += "try:"
$script += "  c.execute('SELECT column_name FROM information_schema.columns WHERE table_name=''gestao_rural_assinaturacliente'' AND column_name=''mercadopago_customer_id''');"
$script += "  if not c.fetchone():"
$script += "    print('Criando coluna mercadopago_customer_id...');"
$script += "    c.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL');"
$script += "    c.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)');"
$script += "    print('SUCCESS: mercadopago_customer_id criada');"
$script += "  else:"
$script += "    print('INFO: mercadopago_customer_id ja existe');"
$script += "except Exception as e:"
$script += "  print(f'ERROR: {e}');"

gcloud run jobs create criar-mercadopago-col `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="-c,$script" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando..." -ForegroundColor Yellow
gcloud run jobs execute criar-mercadopago-col --region=$REGION --wait

Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=criar-mercadopago-col" `
  --limit=30 `
  --format="value(textPayload)" `
  --freshness=5m

gcloud run jobs delete criar-mercadopago-col --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

