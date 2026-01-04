# Ver logs e criar tabela UsuarioAtivo
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando logs do erro 500" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$logs = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=5 `
  --format="value(textPayload)" `
  --freshness=5m

if ($logs) {
    Write-Host "📋 Últimos erros:" -ForegroundColor Yellow
    $logs | Select-Object -First 30
} else {
    Write-Host "✅ Nenhum erro encontrado nos últimos 5 minutos" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 Criando tabela UsuarioAtivo" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Deletar job anterior
gcloud run jobs delete criar-tabela-usuarioativo --region=$REGION --quiet 2>$null

# Criar job usando Python inline mais simples
Write-Host "⏱️  Criando job..." -ForegroundColor Yellow

# Usar um arquivo Python temporário seria melhor, mas vamos usar comando inline
$pythonCode = @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Verificar se existe
cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')")
exists = cursor.fetchone()[0]

if not exists:
    print('Criando tabela...')
    cursor.execute('''
        CREATE TABLE gestao_rural_usuarioativo (
            id BIGSERIAL NOT NULL PRIMARY KEY,
            nome_completo VARCHAR(255) NOT NULL,
            email VARCHAR(254) NOT NULL,
            telefone VARCHAR(20),
            primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            total_acessos INTEGER NOT NULL DEFAULT 0,
            ativo BOOLEAN NOT NULL DEFAULT true,
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            usuario_id BIGINT NOT NULL UNIQUE,
            CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey 
            FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)')
    cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING")
    print('✅ Tabela criada!')
else:
    print('✅ Tabela já existe!')
"@

# Salvar código em arquivo temporário
$tempFile = [System.IO.Path]::GetTempFileName() + ".py"
$pythonCode | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "⏱️  Executando job (aguarde 1-2 minutos)..." -ForegroundColor Yellow

# Criar job que executa o arquivo Python
gcloud run jobs create criar-tabela-usuarioativo `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="-c,$($pythonCode -replace "`r`n",' ' -replace '"','\"')" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

# Alternativa: usar manage.py migrate diretamente
Write-Host ""
Write-Host "🔄 Tentando criar via migrate..." -ForegroundColor Yellow

gcloud run jobs update criar-tabela-usuarioativo `
  --region=$REGION `
  --args="manage.py,migrate,gestao_rural,0081_add_usuario_ativo" `
  --quiet

gcloud run jobs execute criar-tabela-usuarioativo --region=$REGION --wait

# Limpar
gcloud run jobs delete criar-tabela-usuarioativo --region=$REGION --quiet 2>$null
Remove-Item $tempFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green


