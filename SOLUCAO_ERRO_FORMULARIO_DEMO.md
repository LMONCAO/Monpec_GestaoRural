# Solução: Erro ao Criar Usuário Demo no Sistema Web

Este guia explica como diagnosticar e resolver o erro "Erro ao processar solicitação. Por favor, tente novamente." no formulário de demonstração.

## 🔍 Possíveis Causas

O erro pode ocorrer por várias razões:

1. **Migrações não aplicadas** - A tabela `UsuarioAtivo` não existe no banco
2. **Erro de conexão com banco de dados** - Problemas de conectividade
3. **Erro de CSRF** - Token CSRF inválido ou ausente
4. **Erro de validação** - Campos inválidos ou dados incorretos
5. **Erro no código** - Exception não tratada

## 🔧 Solução 1: Verificar e Aplicar Migrações (Mais Provável)

### Passo 1: Verificar Migrações Pendentes

No Google Cloud Shell, execute:

```bash
gcloud config set project monpec-sistema-rural

# Criar job temporário para verificar migrações
gcloud run jobs create verificar-migracoes \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,showmigrations" \
  --memory=2Gi \
  --cpu=2

# Executar o job
gcloud run jobs execute verificar-migracoes --region=us-central1 --wait

# Deletar job após uso
gcloud run jobs delete verificar-migracoes --region=us-central1
```

### Passo 2: Aplicar Migrações

Se houver migrações pendentes, execute:

```bash
# Criar job para aplicar migrações
gcloud run jobs create aplicar-migracoes \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Executar o job
gcloud run jobs execute aplicar-migracoes --region=us-central1 --wait

# Deletar job após uso
gcloud run jobs delete aplicar-migracoes --region=us-central1
```

## 🔍 Solução 2: Verificar Logs de Erro

### Ver Logs Recentes do Cloud Run

```bash
# Ver logs do serviço Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50 --format=json

# Filtrar apenas erros
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50

# Buscar por erros específicos de demonstração
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND textPayload=~'demonstração'" --limit=50
```

### Verificar Erros Específicos

```bash
# Erros relacionados a UsuarioAtivo
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND (textPayload=~'UsuarioAtivo' OR textPayload=~'usuario_ativo')" --limit=50

# Erros de tabela não encontrada
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND (textPayload=~'no such table' OR textPayload=~'does not exist')" --limit=50
```

## 🔧 Solução 3: Verificar Se a Tabela Existe

Execute este comando para verificar se a tabela `UsuarioAtivo` existe:

```bash
gcloud run jobs create verificar-tabela \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_usuarioativo'\"); print('Tabela existe!' if cursor.fetchone() else 'Tabela NAO existe!')" \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute verificar-tabela --region=us-central1 --wait
gcloud run jobs delete verificar-tabela --region=us-central1
```

## 🔧 Solução 4: Script Completo de Correção

Crie um arquivo `corrigir_formulario_demo.sh`:

```bash
#!/bin/bash
# Script completo para corrigir problemas no formulário de demonstração

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:monpec-db"

echo "============================================================"
echo "CORRIGINDO FORMULÁRIO DE DEMONSTRAÇÃO"
echo "============================================================"
echo ""

gcloud config set project $PROJECT_ID

echo "1. Aplicando migrações..."
gcloud run jobs delete aplicar-migracoes-demo --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-migracoes-demo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

echo "Executando migrações..."
gcloud run jobs execute aplicar-migracoes-demo --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "❌ Erro ao aplicar migrações. Verifique os logs."
    exit 1
fi

echo ""
echo "2. Verificando tabela UsuarioAtivo..."
gcloud run jobs delete verificar-tabela-demo --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-tabela-demo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="-c,import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%usuarioativo%'\"); result = cursor.fetchone(); print('✅ Tabela encontrada:', result[0] if result else '❌ Tabela NAO encontrada')" \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute verificar-tabela-demo --region=$REGION --wait
gcloud run jobs delete verificar-tabela-demo --region=$REGION

echo ""
echo "============================================================"
echo "✅ Processo concluído!"
echo "============================================================"
echo ""
echo "Agora teste o formulário de demonstração novamente."
echo ""

# Limpar jobs
gcloud run jobs delete aplicar-migracoes-demo --region=$REGION --quiet 2>/dev/null || true
```

## 📋 Checklist de Verificação

Use este checklist para diagnosticar o problema:

- [ ] Migrações foram aplicadas no banco de produção?
- [ ] A tabela `gestao_rural_usuarioativo` existe?
- [ ] O serviço Cloud Run está funcionando corretamente?
- [ ] Os logs mostram algum erro específico?
- [ ] A conexão com o Cloud SQL está funcionando?
- [ ] As variáveis de ambiente estão configuradas corretamente?

## 🚨 Erros Comuns e Soluções

### Erro: "no such table: gestao_rural_usuarioativo"

**Solução:** Aplique as migrações:
```bash
python manage.py migrate --noinput
```

### Erro: "Connection refused" ou "OperationalError"

**Solução:** Verifique a conexão com o Cloud SQL:
```bash
# Verificar se a instância está rodando
gcloud sql instances describe monpec-db

# Verificar configuração de conexão
gcloud run services describe monpec --region=us-central1 --format="value(spec.template.spec.containers[0].env)"
```

### Erro: CSRF token missing or incorrect

**Solução:** Verifique `CSRF_TRUSTED_ORIGINS` no settings:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
]
```

## 📞 Próximos Passos

1. Execute o script de correção acima
2. Verifique os logs para identificar o erro específico
3. Teste o formulário novamente
4. Se o problema persistir, verifique os logs detalhados

