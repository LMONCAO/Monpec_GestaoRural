# Criar estruturas faltantes - Versão Simples
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "🔧 Criando estruturas faltantes..." -ForegroundColor Yellow
Write-Host ""

# Função para executar SQL
function Executar-SQL {
    param($sql, $descricao)
    
    Write-Host "📦 $descricao..." -ForegroundColor Yellow
    
    gcloud run jobs delete temp-sql --region=$REGION --quiet 2>$null
    
    $pythonCode = "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;c=connection.cursor();$sql;print('✅ Sucesso!')"
    
    gcloud run jobs create temp-sql `
      --region=$REGION `
      --image=$IMAGE_NAME `
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
      --command="python" `
      --args="-c,$pythonCode" `
      --max-retries=1 `
      --memory=2Gi `
      --cpu=2 `
      --task-timeout=300 `
      --quiet
    
    gcloud run jobs execute temp-sql --region=$REGION --wait --quiet
    gcloud run jobs delete temp-sql --region=$REGION --quiet 2>$null
}

# 1. Criar coluna mercadopago_customer_id
$sql1 = "c.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN IF NOT EXISTS mercadopago_customer_id VARCHAR(255) NULL');c.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)')"
Executar-SQL -sql $sql1 -descricao "Criando mercadopago_customer_id"

# 2. Criar coluna certificado_digital
$sql2 = "c.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN IF NOT EXISTS certificado_digital VARCHAR(100) NULL')"
Executar-SQL -sql $sql2 -descricao "Criando certificado_digital"

# 3. Criar tabela UsuarioAtivo
$sql3 = "c.execute('CREATE TABLE IF NOT EXISTS gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)');c.execute('CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)')"
Executar-SQL -sql $sql3 -descricao "Criando tabela UsuarioAtivo"

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

