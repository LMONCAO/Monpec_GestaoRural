# ✅ Solução Final para Erro 400

## Problemas Identificados

1. **Middleware usando `request.get_host()`**: O middleware estava tentando usar `request.get_host()` que já valida ALLOWED_HOSTS ANTES do middleware poder adicionar o host. Isso causava `DisallowedHost` exception.

2. **CLOUD_SQL_CONNECTION_NAME vazio**: A variável de ambiente estava vazia, resultando em `/cloudsql//.s.PGSQL.5432` (duas barras indicam valor vazio).

3. **Conexão Cloud SQL não configurada**: O serviço Cloud Run não tinha a conexão com Cloud SQL configurada.

4. **Comando do job de migração incorreto**: Estava usando `--cloud-sql-instances` ao invés de `--set-cloudsql-instances`.

## Correções Aplicadas

### 1. Middleware Corrigido (`sistema_rural/middleware.py`)
- ✅ Removido uso de `request.get_host()` que valida antes do middleware
- ✅ Usa `request.META.get('HTTP_HOST')` diretamente
- ✅ Adiciona hosts do Cloud Run dinamicamente ao ALLOWED_HOSTS
- ✅ Tratamento de exceções melhorado

### 2. Settings GCP Melhorado (`sistema_rural/settings_gcp.py`)
- ✅ Adicionados padrões de hosts do Cloud Run (`*.run.app`, `*.a.run.app`)
- ✅ Logging melhorado para CLOUD_SQL_CONNECTION_NAME
- ✅ Valor padrão garantido se variável estiver vazia

### 3. Scripts Corrigidos
- ✅ `CORRIGIR_ERRO_400_CLOUD_RUN.sh` - Comando do job corrigido
- ✅ `CORRIGIR_CLOUD_SQL_E_ALLOWED_HOSTS.sh` - Novo script para configurar Cloud SQL

## Como Aplicar as Correções

### Passo 1: Fazer novo deploy com as correções

```bash
# No Cloud Shell, faça um novo deploy
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed
```

### Passo 2: Configurar Cloud SQL Connection

Execute o script:

```bash
chmod +x CORRIGIR_CLOUD_SQL_E_ALLOWED_HOSTS.sh
./CORRIGIR_CLOUD_SQL_E_ALLOWED_HOSTS.sh
```

Ou manualmente:

```bash
# Adicionar conexão Cloud SQL ao serviço
gcloud run services update monpec \
    --region=us-central1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

# Configurar variável de ambiente
gcloud run services update monpec \
    --region=us-central1 \
    --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"
```

### Passo 3: Verificar variáveis de ambiente

```bash
gcloud run services describe monpec \
    --region=us-central1 \
    --format="value(spec.template.spec.containers[0].env)"
```

Deve incluir:
- `SECRET_KEY` (já configurada)
- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp` (já configurada)
- `DEBUG=False` (já configurada)
- `CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db` (precisa ser configurada)

### Passo 4: Testar o serviço

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe monpec \
    --region=us-central1 \
    --format="value(status.url)")

echo "Testando: $SERVICE_URL"
curl -I "$SERVICE_URL"
```

## Verificação Final

Após aplicar as correções, verifique:

1. ✅ O serviço responde sem erro 400
2. ✅ Os logs não mostram mais `DisallowedHost`
3. ✅ A conexão com Cloud SQL funciona (sem erro de socket)
4. ✅ As migrações podem ser aplicadas

## Se o Erro Persistir

1. **Verifique os logs mais recentes:**
   ```bash
   gcloud logging read \
       "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
       --limit=20 \
       --format="table(timestamp,severity,textPayload)" \
       --project=monpec-sistema-rural
   ```

2. **Verifique se o middleware está sendo carregado:**
   ```bash
   gcloud logging read \
       "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND textPayload=~'CloudRunHostMiddleware'" \
       --limit=10 \
       --project=monpec-sistema-rural
   ```

3. **Verifique se o Cloud SQL está acessível:**
   ```bash
   gcloud sql instances describe monpec-db
   ```

## Notas Importantes

- O middleware agora intercepta ANTES da validação do Django
- O ALLOWED_HOSTS inclui `*` e padrões do Cloud Run
- O CLOUD_SQL_CONNECTION_NAME tem valor padrão se não estiver configurado
- A conexão Cloud SQL deve ser adicionada ao serviço via `--add-cloudsql-instances`





