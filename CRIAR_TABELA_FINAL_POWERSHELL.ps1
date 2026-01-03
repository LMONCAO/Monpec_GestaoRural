# Criar tabela UsuarioAtivo - Versão Final
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 Criando tabela UsuarioAtivo" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Deletar job anterior se existir
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null

# Criar job para criar tabela
Write-Host "⏱️  Criando job..." -ForegroundColor Yellow
gcloud run jobs create criar-usuarioativo-final `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db" `
  --set-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
  --command="python" `
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema=''public'' AND table_name=''gestao_rural_usuarioativo'')');exists=cursor.fetchone()[0];print('Tabela existe:',exists);exec('if not exists:\n    print(\"Criando...\")\n    cursor.execute(\"\"\"CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)\"\"\")\n    cursor.execute(\"CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)\")\n    cursor.execute(\"INSERT INTO django_migrations (app, name, applied) VALUES (''gestao_rural'', ''0081_add_usuario_ativo'', NOW()) ON CONFLICT (app, name) DO NOTHING\")\n    cursor.execute('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema=''public'' AND table_name=''gestao_rural_usuarioativo'')')\n    exists=cursor.fetchone()[0]\n    print(\"✅ Criada!\" if exists else \"❌ Erro\")') if not exists else print('✅ Tabela já existe!')" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando job (aguarde 1-2 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute criar-usuarioativo-final --region=$REGION --wait

# Limpar
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

