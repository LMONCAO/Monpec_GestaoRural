# ⚡ Comandos Rápidos - Google Cloud

## 🔐 Autenticação e Configuração

```bash
# Autenticar
gcloud auth login

# Definir projeto
gcloud config set project monpec-sistema-rural

# Ver configuração atual
gcloud config list
```

## 🗄️ Banco de Dados Cloud SQL

```bash
# Criar instância
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!

# Criar banco
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!

# Ver connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

## 🚀 Deploy Cloud Run

```bash
# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db

# Obter URL
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

## 🔄 Migrações

```bash
# Criar job de migração
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db \
    --command python \
    --args manage.py,migrate

# Executar
gcloud run jobs execute migrate-db --region us-central1
```

## 📊 Verificar Status

```bash
# Status do serviço
gcloud run services describe monpec --region us-central1

# Logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Status do banco
gcloud sql instances describe monpec-db
```

## 🌐 Configurar Domínio

```bash
# Mapear domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

## 🔧 Atualizar Variáveis de Ambiente

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars \
        DEBUG=False,\
        NOVA_VARIAVEL=valor
```

## 🗑️ Limpar Recursos (CUIDADO!)

```bash
# Deletar serviço Cloud Run
gcloud run services delete monpec --region us-central1

# Deletar instância Cloud SQL
gcloud sql instances delete monpec-db
```






