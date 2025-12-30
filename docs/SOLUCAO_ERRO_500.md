# 🔧 Solução para Erro 500

## Problema
Agora está dando erro 500 (Server Error) ao invés de "usuário não encontrado". Isso indica que o serviço está tentando conectar, mas há um erro no servidor.

## Possíveis Causas

1. **Migrações do banco não executadas** - Tabelas não existem
2. **Erro de conexão com o banco** - Variáveis incorretas
3. **Erro no código Django** - Algum erro de configuração

## Solução Passo a Passo

### 1. Verificar Logs

Execute no Cloud Shell:

```bash
# Ver logs recentes
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
  --limit 50 \
  --format="table(timestamp,severity,textPayload)"
```

Isso mostrará o erro exato que está acontecendo.

### 2. Executar Migrações

Se o erro for sobre tabelas não existentes, execute as migrações:

```bash
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

gcloud run jobs create run-migrations \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,--noinput \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1

gcloud run jobs execute run-migrations --region us-central1 --wait
```

### 3. Verificar Variáveis do Serviço

```bash
# Ver todas as variáveis
gcloud run services describe monpec --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### 4. Recriar Admin após Migrações

Depois das migrações, execute novamente:

```bash
gcloud run jobs execute create-admin --region us-central1 --wait
```

## Próximos Passos

1. ✅ Execute o comando de verificar logs primeiro
2. ✅ Veja qual é o erro específico
3. ✅ Execute migrações se necessário
4. ✅ Teste novamente








