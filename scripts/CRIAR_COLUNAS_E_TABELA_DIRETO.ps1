# Criar colunas e tabela diretamente no banco
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 Criando colunas e tabela diretamente no banco" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete criar-colunas-tabela --region=$REGION --quiet 2>$null

# Criar job que executa SQL direto
$pythonCode = @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection
cursor = connection.cursor()

print('Verificando e criando estruturas...')

# 1. Verificar e criar coluna mercadopago_customer_id
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_customer_id'")
    if not cursor.fetchone():
        print('Criando coluna mercadopago_customer_id...')
        cursor.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL')
        cursor.execute("CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)")
        print('✅ Coluna mercadopago_customer_id criada!')
    else:
        print('✅ Coluna mercadopago_customer_id já existe!')
except Exception as e:
    print(f'Erro ao criar mercadopago_customer_id: {e}')

# 2. Verificar e criar coluna certificado_digital
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_digital'")
    if not cursor.fetchone():
        print('Criando coluna certificado_digital...')
        cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_digital TEXT NULL')
        print('✅ Coluna certificado_digital criada!')
    else:
        print('✅ Coluna certificado_digital já existe!')
except Exception as e:
    print(f'Erro ao criar certificado_digital: {e}')

# 3. Verificar e criar tabela UsuarioAtivo
try:
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')")
    if not cursor.fetchone()[0]:
        print('Criando tabela UsuarioAtivo...')
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
        print('✅ Tabela UsuarioAtivo criada!')
    else:
        print('✅ Tabela UsuarioAtivo já existe!')
except Exception as e:
    print(f'Erro ao criar UsuarioAtivo: {e}')

print('✅ Concluído!')
"@

# Salvar em arquivo temporário
$tempFile = [System.IO.Path]::GetTempFileName() + ".py"
$pythonCode | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "⏱️  Criando job..." -ForegroundColor Yellow

# Criar job que executa o arquivo Python
gcloud run jobs create criar-colunas-tabela `
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

Write-Host "⏱️  Executando (aguarde 1-2 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute criar-colunas-tabela --region=$REGION --wait

# Ver logs
Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=criar-colunas-tabela" `
  --limit=50 `
  --format="value(textPayload)" `
  --freshness=5m | Select-Object -First 50

# Limpar
gcloud run jobs delete criar-colunas-tabela --region=$REGION --quiet 2>$null
Remove-Item $tempFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green


