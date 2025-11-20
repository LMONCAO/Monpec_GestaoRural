# 🚀 INÍCIO RÁPIDO - Deploy no Google Cloud

## ⚡ 3 Passos para Colocar o Site no Ar

### 1️⃣ **Preparar Ambiente** (5 minutos)

**No Cloud Shell Editor** (já está aberto na sua tela):
```bash
# Autenticar
gcloud auth login

# Criar projeto (se ainda não criou)
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"
gcloud config set project monpec-sistema-rural

# Habilitar billing (via console web)
# Acesse: https://console.cloud.google.com/billing
```

### 2️⃣ **Criar Banco de Dados** (5 minutos)

```bash
# Criar instância PostgreSQL
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!

# Criar banco e usuário
gcloud sql databases create monpec_db --instance=monpec-db
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!
```

### 3️⃣ **Fazer Deploy** (10 minutos)

```bash
# Habilitar APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com

# Build e Deploy
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Obter connection name do banco
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# Deploy no Cloud Run
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME

# Obter URL do site
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

## ✅ Pronto!

Seu site estará acessível na URL retornada pelo último comando!

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **Guia Completo**: `GUIA_DEPLOY_GOOGLE_CLOUD_PASSO_A_PASSO.md`
- **Script Automático**: Execute `deploy_google_cloud.ps1` no PowerShell
- **Comandos Rápidos**: `COMANDOS_RAPIDOS_GOOGLE_CLOUD.md`

---

## 🆘 Problemas?

### Erro: "Permission denied"
```bash
gcloud auth login
gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="user:SEU_EMAIL@gmail.com" \
    --role="roles/owner"
```

### Erro: "Billing not enabled"
1. Acesse: https://console.cloud.google.com/billing
2. Vincule uma conta de faturamento ao projeto

### Erro: "Database connection failed"
Verifique se o connection name está correto:
```bash
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

---

**💡 Dica**: Use o Cloud Shell Editor que já está aberto - tudo já vem configurado!







