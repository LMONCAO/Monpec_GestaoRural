# 🔧 Como Corrigir Erro 400 no Cloud Run

## Problema
O serviço Cloud Run está retornando erro 400 (Bad Request) ao acessar a URL.

## Possíveis Causas

1. **Variáveis de ambiente não configuradas**
   - `SECRET_KEY` não configurada
   - `DJANGO_SETTINGS_MODULE` não configurado
   - `DB_PASSWORD` ou outras variáveis de banco não configuradas

2. **ALLOWED_HOSTS bloqueando o host**
   - O host do Cloud Run não está em `ALLOWED_HOSTS`
   - O middleware não está sendo carregado corretamente

3. **Migrações não aplicadas**
   - O banco de dados não está com as tabelas criadas

4. **Problemas com conexão ao banco**
   - `CLOUD_SQL_CONNECTION_NAME` não configurado
   - Credenciais do banco incorretas

## Solução Passo a Passo

### 1. Verificar e Configurar Variáveis de Ambiente

Execute no Cloud Shell:

```bash
# Definir projeto
gcloud config set project monpec-sistema-rural

# Verificar variáveis atuais
gcloud run services describe monpec \
    --region=us-central1 \
    --format="value(spec.template.spec.containers[0].env)"

# Configurar variáveis essenciais
gcloud run services update monpec \
    --region=us-central1 \
    --update-env-vars \
        "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))'),\
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --quiet
```

### 2. Configurar Variáveis do Banco de Dados

Se ainda não configurou, adicione:

```bash
gcloud run services update monpec \
    --region=us-central1 \
    --update-env-vars \
        "DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=SUA_SENHA_AQUI" \
    --quiet
```

### 3. Aplicar Migrações

```bash
# Criar job de migração (se não existir)
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region=us-central1 \
    --command python \
    --args "manage.py,migrate,--noinput" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --cloud-sql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --quiet

# Executar migrações
gcloud run jobs execute migrate-monpec \
    --region=us-central1 \
    --wait
```

### 4. Verificar Logs

```bash
# Ver logs recentes
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=monpec-sistema-rural
```

### 5. Testar o Serviço

```bash
# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe monpec \
    --region=us-central1 \
    --format="value(status.url)")

echo "URL do serviço: $SERVICE_URL"

# Testar acesso
curl -I "$SERVICE_URL"
```

## Script Automatizado

Use o script `CORRIGIR_ERRO_400_CLOUD_RUN.sh` que faz tudo automaticamente:

```bash
chmod +x CORRIGIR_ERRO_400_CLOUD_RUN.sh
./CORRIGIR_ERRO_400_CLOUD_RUN.sh
```

## Verificações Adicionais

### Verificar se o serviço está rodando

```bash
gcloud run services describe monpec \
    --region=us-central1 \
    --format="table(status.conditions[0].type,status.conditions[0].status,status.url)"
```

### Verificar conexão com Cloud SQL

```bash
# Verificar se o Cloud SQL está acessível
gcloud sql instances describe monpec-db \
    --format="value(connectionName)"
```

### Verificar ALLOWED_HOSTS

O arquivo `sistema_rural/settings_gcp.py` já está configurado com:
- `'*'` em `ALLOWED_HOSTS` para permitir todos os hosts
- Middleware `CloudRunHostMiddleware` para adicionar hosts dinamicamente

Se ainda assim houver erro, verifique se o middleware está sendo carregado:

```bash
# Ver logs do serviço procurando por "CloudRunHostMiddleware"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND textPayload=~'CloudRunHostMiddleware'" \
    --limit=10 \
    --project=monpec-sistema-rural
```

## Solução de Problemas

### Erro 400 persiste após configurar variáveis

1. **Verifique os logs detalhados:**
   ```bash
   gcloud logging read \
       "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
       --limit=20 \
       --project=monpec-sistema-rural
   ```

2. **Verifique se o SECRET_KEY está configurado:**
   ```bash
   gcloud run services describe monpec \
       --region=us-central1 \
       --format="value(spec.template.spec.containers[0].env[?(@.name=='SECRET_KEY')].value)"
   ```

3. **Teste localmente com as mesmas variáveis:**
   ```bash
   export SECRET_KEY="sua_secret_key"
   export DJANGO_SETTINGS_MODULE="sistema_rural.settings_gcp"
   python manage.py check --deploy
   ```

### Erro de conexão com banco

1. **Verifique se o Cloud SQL está acessível:**
   ```bash
   gcloud sql instances describe monpec-db
   ```

2. **Verifique se o Cloud Run tem permissão para acessar o Cloud SQL:**
   ```bash
   # Adicionar Cloud SQL connection ao serviço
   gcloud run services update monpec \
       --region=us-central1 \
       --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
   ```

## Próximos Passos

Após corrigir o erro 400:

1. ✅ Verificar se o serviço está acessível
2. ✅ Aplicar migrações do banco de dados
3. ✅ Configurar domínio personalizado (opcional)
4. ✅ Configurar variáveis de ambiente adicionais conforme necessário

## Contato

Se o problema persistir, verifique:
- Logs do Cloud Run
- Logs do Cloud SQL
- Status do serviço no Console do Google Cloud





