# Guia de Troubleshooting - Cloud Run "Service Unavailable"

Este documento ajuda a diagnosticar e resolver o erro "Service Unavailable" no Google Cloud Run.

## Problemas Comuns e Soluções

### 1. Verificar Logs do Serviço

Execute o script de diagnóstico:
```powershell
.\diagnosticar-cloud-run.ps1
```

Ou manualmente:
```bash
# Ver logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --project=monpec-sistema-rural

# Ver apenas erros
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50 --project=monpec-sistema-rural
```

### 2. Verificar Variáveis de Ambiente

Execute o script de verificação:
```powershell
.\verificar-variaveis-ambiente.ps1
```

**Variáveis críticas necessárias:**
- `SECRET_KEY` - Chave secreta do Django
- `DB_NAME` - Nome do banco de dados
- `DB_USER` - Usuário do banco de dados
- `DB_PASSWORD` - Senha do banco de dados
- `CLOUD_SQL_CONNECTION_NAME` - Nome da conexão Cloud SQL (formato: `PROJECT_ID:REGION:INSTANCE_NAME`)

**Para configurar variáveis de ambiente:**
```bash
gcloud run services update monpec \
  --region=us-central1 \
  --project=monpec-sistema-rural \
  --set-env-vars SECRET_KEY=sua-chave-secreta \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=sua-senha \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db
```

### 3. Verificar Conexão com Cloud SQL

O Cloud Run precisa ter permissão para conectar ao Cloud SQL:

```bash
# Verificar se a conexão Cloud SQL está configurada
gcloud run services describe monpec --region=us-central1 --project=monpec-sistema-rural --format="value(spec.template.spec.containers[0].env)"

# Adicionar conexão Cloud SQL ao serviço
gcloud run services update monpec \
  --region=us-central1 \
  --project=monpec-sistema-rural \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```

### 4. Verificar Timeout e Recursos

O Cloud Run tem um timeout padrão de 300 segundos. Se as migrações demorarem muito, o serviço pode não iniciar:

```bash
# Verificar timeout atual
gcloud run services describe monpec --region=us-central1 --project=monpec-sistema-rural --format="value(spec.template.spec.timeoutSeconds)"

# Aumentar timeout se necessário (máximo 3600 segundos)
gcloud run services update monpec \
  --region=us-central1 \
  --project=monpec-sistema-rural \
  --timeout=600
```

**Verificar recursos alocados:**
```bash
gcloud run services describe monpec --region=us-central1 --project=monpec-sistema-rural --format="value(spec.template.spec.containers[0].resources)"
```

Se necessário, aumentar recursos:
```bash
gcloud run services update monpec \
  --region=us-central1 \
  --project=monpec-sistema-rural \
  --memory=2Gi \
  --cpu=2
```

### 5. Verificar Status da Revisão

```bash
# Listar revisões e seus status
gcloud run revisions list --service=monpec --region=us-central1 --project=monpec-sistema-rural

# Ver detalhes de uma revisão específica
gcloud run revisions describe REVISION_NAME --region=us-central1 --project=monpec-sistema-rural
```

### 6. Problemas Comuns de Inicialização

#### Migrações falhando
- Verificar se o banco de dados está acessível
- Verificar se as credenciais estão corretas
- Verificar se o Cloud SQL está rodando

#### Timeout na inicialização
- O script `entrypoint.sh` agora tem timeout de 120 segundos para migrações
- Se ainda falhar, considere executar migrações manualmente antes do deploy

#### Erro de importação de módulos
- Verificar se todas as dependências estão em `requirements_producao.txt`
- Verificar se o build da imagem foi bem-sucedido

### 7. Rebuild e Redeploy

Se o problema persistir, tente fazer um rebuild completo:

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec --project=monpec-sistema-rural

# Deploy no Cloud Run
gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region=us-central1 \
  --project=monpec-sistema-rural \
  --platform=managed \
  --allow-unauthenticated \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --set-env-vars SECRET_KEY=sua-chave \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=sua-senha \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=600
```

### 8. Verificar Permissões IAM

O serviço Cloud Run precisa ter permissões para:
- Conectar ao Cloud SQL
- Acessar Cloud Storage (se usar)
- Escrever logs

```bash
# Verificar conta de serviço do Cloud Run
gcloud run services describe monpec --region=us-central1 --project=monpec-sistema-rural --format="value(spec.template.spec.serviceAccountName)"

# Adicionar permissão para Cloud SQL
gcloud projects add-iam-policy-binding monpec-sistema-rural \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/cloudsql.client"
```

## Checklist de Diagnóstico

- [ ] Logs mostram algum erro específico?
- [ ] Todas as variáveis de ambiente críticas estão configuradas?
- [ ] A conexão Cloud SQL está configurada no serviço?
- [ ] O timeout é suficiente para a inicialização?
- [ ] Os recursos (CPU/memória) são suficientes?
- [ ] A imagem Docker foi construída corretamente?
- [ ] As permissões IAM estão corretas?
- [ ] O banco de dados Cloud SQL está rodando e acessível?

## Próximos Passos

1. Execute `.\diagnosticar-cloud-run.ps1` para obter informações detalhadas
2. Execute `.\verificar-variaveis-ambiente.ps1` para verificar configurações
3. Revise os logs para identificar erros específicos
4. Corrija os problemas identificados
5. Faça um redeploy se necessário









