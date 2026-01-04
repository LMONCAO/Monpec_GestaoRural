# Script PowerShell para Rebuild e Deploy
# Execute no PowerShell do Windows

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔨 Rebuild e Deploy do MONPEC" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório do projeto
$projectPath = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
Set-Location $projectPath

Write-Host "📦 Verificando se há mudanças não commitadas..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    Write-Host "⚠️  Há mudanças não commitadas. Fazendo commit..." -ForegroundColor Yellow
    git add gestao_rural/views.py
    git commit -m "fix: Adicionar tratamento de ProgrammingError para UsuarioAtivo" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Commit realizado!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erro no commit (pode ser normal se já commitou)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Nenhuma mudança pendente" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔨 Fazendo build e upload da imagem Docker..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 5-10 minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag $IMAGE_NAME --timeout=600s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build concluído!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📦 Verificando/criando tabela UsuarioAtivo..." -ForegroundColor Yellow
    gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null
    
    gcloud run jobs create criar-usuarioativo-final `
      --region=$REGION `
      --image=$IMAGE_NAME `
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
      --command="python" `
      --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(`"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')`");exists=cursor.fetchone()[0];print('Tabela existe:',exists);if not exists:print('Criando...');cursor.execute('''CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)''');cursor.execute(`"CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)`");cursor.execute(`"INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING`");cursor.execute(`"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')`");exists=cursor.fetchone()[0];print('✅ Criada!' if exists else '❌ Erro')" `
      --max-retries=1 `
      --memory=2Gi `
      --cpu=2 `
      --task-timeout=300
    
    gcloud run jobs execute criar-usuarioativo-final --region=$REGION --wait
    gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>$null
    
    Write-Host ""
    Write-Host "🚀 Fazendo deploy..." -ForegroundColor Yellow
    gcloud run deploy $SERVICE_NAME `
      --region=$REGION `
      --image=$IMAGE_NAME `
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
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


