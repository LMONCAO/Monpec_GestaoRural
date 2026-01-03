# 🔧 Solução Completa para Erro 500

## Problema
O erro 500 ocorre porque a tabela `gestao_rural_usuarioativo` não existe no banco de dados, mas o código tenta acessá-la.

## Solução em 3 Passos

### Passo 1: Fazer commit e push das correções no código

As correções já foram feitas no arquivo `gestao_rural/views.py` para tratar o caso quando a tabela não existe. Agora você precisa fazer commit e push:

```bash
git add gestao_rural/views.py
git commit -m "fix: Adicionar tratamento de ProgrammingError para UsuarioAtivo"
git push
```

### Passo 2: Rebuild da imagem Docker (se necessário)

Se você usa CI/CD automático, o push acima já vai fazer o rebuild. Caso contrário, execute:

```bash
# No seu ambiente local ou CI/CD
docker build -f Dockerfile.prod -t gcr.io/monpec-sistema-rural/sistema-rural:latest .
docker push gcr.io/monpec-sistema-rural/sistema-rural:latest
```

### Passo 3: Criar tabela e fazer deploy

Execute este comando no **Google Cloud Shell**:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Criando tabela UsuarioAtivo..."
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create criar-usuarioativo-final \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')\");exists=cursor.fetchone()[0];print('Tabela existe:',exists);if not exists:print('Criando...');cursor.execute('''CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)''');cursor.execute(\"CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)\");cursor.execute(\"INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING\");cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')\");exists=cursor.fetchone()[0];print('✅ Criada!' if exists else '❌ Erro')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

echo "⏱️  Executando..."
gcloud run jobs execute criar-usuarioativo-final --region=$REGION --wait

echo ""
echo "🔄 Fazendo deploy..."
gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet

echo ""
echo "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/"

gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>/dev/null || true
```

## O que foi corrigido

1. **Código**: Adicionado tratamento de `ProgrammingError` em todos os lugares onde `UsuarioAtivo` é acessado
2. **Banco de dados**: Script para criar a tabela `gestao_rural_usuarioativo` se não existir
3. **Deploy**: Deploy automático após criar a tabela

## Verificação

Após executar os passos acima, acesse:
- https://monpec-29862706245.us-central1.run.app/login/

O erro 500 deve estar resolvido! ✅

