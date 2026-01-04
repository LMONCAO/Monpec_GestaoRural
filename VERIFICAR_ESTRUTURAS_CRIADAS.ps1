# Verificar se as estruturas foram criadas
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando se estruturas foram criadas" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete verificar-estruturas --region=$REGION --quiet 2>$null

$script = "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;c=connection.cursor();"
$script += "c.execute('SELECT column_name FROM information_schema.columns WHERE table_name=''gestao_rural_assinaturacliente'' AND column_name=''mercadopago_customer_id''');r1=c.fetchone();print('mercadopago_customer_id:', 'EXISTE' if r1 else 'NAO EXISTE');"
$script += "c.execute('SELECT column_name FROM information_schema.columns WHERE table_name=''gestao_rural_produtorrural'' AND column_name=''certificado_digital''');r2=c.fetchone();print('certificado_digital:', 'EXISTE' if r2 else 'NAO EXISTE');"
$script += "c.execute('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema=''public'' AND table_name=''gestao_rural_usuarioativo'')');r3=c.fetchone()[0];print('UsuarioAtivo:', 'EXISTE' if r3 else 'NAO EXISTE');"

gcloud run jobs create verificar-estruturas `
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

Write-Host "⏱️  Verificando..." -ForegroundColor Yellow
gcloud run jobs execute verificar-estruturas --region=$REGION --wait

Write-Host ""
Write-Host "📋 Resultado:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-estruturas" `
  --limit=20 `
  --format="value(textPayload)" `
  --freshness=5m

gcloud run jobs delete verificar-estruturas --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "🌐 Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan


