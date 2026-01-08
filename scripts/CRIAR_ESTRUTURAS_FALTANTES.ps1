# Criar estruturas faltantes diretamente no banco
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 Criando estruturas faltantes no banco" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete criar-estruturas --region=$REGION --quiet 2>$null

# Script Python inline simplificado
$pythonScript = "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;c=connection.cursor();"

# Verificar e criar mercadopago_customer_id
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_customer_id'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL');c.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)');print('✅ mercadopago_customer_id criada');"

# Verificar e criar mercadopago_subscription_id
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_subscription_id'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_subscription_id VARCHAR(255) NULL');c.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_3577a7_idx ON gestao_rural_assinaturacliente(mercadopago_subscription_id)');print('✅ mercadopago_subscription_id criada');"

# Verificar e criar certificado_digital
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_digital'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_digital VARCHAR(100) NULL');print('✅ certificado_digital criada');"

# Verificar e criar senha_certificado
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='senha_certificado'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN senha_certificado VARCHAR(255) NULL');print('✅ senha_certificado criada');"

# Verificar e criar certificado_valido_ate
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_valido_ate'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_valido_ate DATE NULL');print('✅ certificado_valido_ate criada');"

# Verificar e criar certificado_tipo
$pythonScript += "c.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_tipo'\");"
$pythonScript += "if not c.fetchone():c.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_tipo VARCHAR(10) NULL');print('✅ certificado_tipo criada');"

# Verificar e criar tabela UsuarioAtivo
$pythonScript += "c.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')\");"
$pythonScript += "if not c.fetchone()[0]:c.execute('CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)');c.execute('CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)');c.execute(\"INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING\");print('✅ Tabela UsuarioAtivo criada');"

$pythonScript += "print('✅ Concluído!')"

Write-Host "⏱️  Criando job..." -ForegroundColor Yellow

gcloud run jobs create criar-estruturas `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="-c,$pythonScript" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando (aguarde 1-2 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute criar-estruturas --region=$REGION --wait

# Ver logs
Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=criar-estruturas" `
  --limit=30 `
  --format="value(textPayload)" `
  --freshness=5m

# Limpar
gcloud run jobs delete criar-estruturas --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green


