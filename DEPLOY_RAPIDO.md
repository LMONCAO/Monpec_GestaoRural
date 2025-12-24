# 🚀 Deploy Rápido - Google Cloud Run

Guia rápido para fazer deploy do MonPEC no Google Cloud em poucos minutos.

## ⚡ Deploy em 5 Passos

### 1. Preparar Ambiente

```bash
# Instalar Google Cloud SDK (se ainda não tiver)
# https://cloud.google.com/sdk/docs/install

# Fazer login
gcloud auth login

# Configurar projeto
gcloud config set project SEU_PROJECT_ID
```

### 2. Habilitar APIs

```bash
gcloud services enable cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  sqladmin.googleapis.com
```

### 3. Criar Banco de Dados (Cloud SQL)

```bash
# Criar instância PostgreSQL
gcloud sql instances create monpec-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=SUA_SENHA_ROOT

# Criar banco e usuário
gcloud sql databases create monpec_db --instance=monpec-db
gcloud sql users create monpec_user \
  --instance=monpec-db \
  --password=SUA_SENHA_DB

# Obter connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

### 4. Deploy da Aplicação

```bash
# Opção A: Script automatizado (recomendado)
chmod +x deploy.sh
./deploy.sh

# Opção B: Manual
gcloud builds submit --config cloudbuild-config.yaml
```

### 5. Configurar Variáveis de Ambiente

```bash
# Gerar SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar variáveis (use o script ou manualmente)
chmod +x configurar-variaveis-ambiente.sh
./configurar-variaveis-ambiente.sh

# Ou manualmente:
gcloud run services update monpec \
  --region=us-central1 \
  --set-env-vars="SECRET_KEY=SUA_SECRET_KEY" \
  --set-env-vars="DB_NAME=monpec_db" \
  --set-env-vars="DB_USER=monpec_user" \
  --set-env-vars="DB_PASSWORD=SUA_SENHA" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:monpec-db" \
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db
```

### 6. Aplicar Migrações

```bash
chmod +x executar-migracoes.sh
./executar-migracoes.sh
```

### 7. Criar Superusuário

Após o deploy, acesse a URL do serviço e crie o superusuário via interface web, ou use:

```bash
# Conectar ao Cloud Shell e executar
gcloud run jobs create create-superuser \
  --image=gcr.io/PROJECT_ID/monpec:latest \
  --region=us-central1 \
  --command=python \
  --args=manage.py,createsuperuser \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db \
  --interactive

gcloud run jobs execute create-superuser --region=us-central1
```

## 📋 Checklist Rápido

- [ ] Projeto Google Cloud criado
- [ ] APIs habilitadas
- [ ] Cloud SQL criado
- [ ] Deploy executado
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações aplicadas
- [ ] Superusuário criado
- [ ] Sistema testado

## 🔗 URLs Úteis

- **Console Cloud Run:** https://console.cloud.google.com/run
- **Console Cloud SQL:** https://console.cloud.google.com/sql
- **Logs:** `gcloud run services logs tail monpec --region=us-central1`

## ⚠️ Problemas Comuns

**502 Bad Gateway:** Verifique logs e variáveis de ambiente

**Erro de conexão DB:** Verifique CLOUD_SQL_CONNECTION_NAME e permissões

**Arquivos estáticos não carregam:** Execute collectstatic manualmente

## 📚 Documentação Completa

Para instruções detalhadas, consulte: `DEPLOY_GCP_COMPLETO.md`

---

**Tempo estimado:** 15-30 minutos
