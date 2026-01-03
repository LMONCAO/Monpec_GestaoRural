# Solução Final Completa: Criar tabela + Rebuild + Deploy
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 SOLUÇÃO FINAL: Criar tabela + Rebuild + Deploy" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud config set project $PROJECT_ID

# Passo 1: Criar tabela UsuarioAtivo
Write-Host "📦 Passo 1: Criando tabela UsuarioAtivo..." -ForegroundColor Yellow
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null

gcloud run jobs create criar-usuarioativo-final `
  --region=$REGION `
  --image="gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest" `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db" `
  --set-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
  --command="python" `
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(`"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')`");exists=cursor.fetchone()[0];print('Tabela existe:',exists);if not exists:print('Criando...');cursor.execute('''CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)''');cursor.execute(`"CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)`");cursor.execute(`"INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING`");cursor.execute(`"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')`");exists=cursor.fetchone()[0];print('✅ Criada!' if exists else '❌ Erro')" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando job (aguarde 1-2 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute criar-usuarioativo-final --region=$REGION --wait
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null

# Passo 2: Rebuild com código atualizado
Write-Host ""
Write-Host "🔨 Passo 2: Fazendo rebuild com código atualizado..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 5-10 minutos..." -ForegroundColor Yellow
Write-Host ""

# Navegar para o diretório do projeto
$projectPath = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
Set-Location $projectPath

gcloud builds submit --tag $IMAGE_NAME --timeout=600s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build concluído!" -ForegroundColor Green
    
    # Passo 3: Deploy
    Write-Host ""
    Write-Host "🚀 Passo 3: Fazendo deploy..." -ForegroundColor Yellow
    
    gcloud run deploy $SERVICE_NAME `
      --region=$REGION `
      --image=$IMAGE_NAME `
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db" `
      --set-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
      --memory=2Gi `
      --cpu=2 `
      --timeout=300 `
      --allow-unauthenticated `
      --quiet
    
    Write-Host ""
    Write-Host "✅✅✅ CONCLUÍDO! ✅✅✅" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Erro no build. Verifique os logs acima." -ForegroundColor Red
}

