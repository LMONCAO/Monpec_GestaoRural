# 🚀 Próximos Passos - Após gcloud init

## ✅ **Você já fez:**
- [x] Autenticado no Google Cloud
- [x] Selecionado o projeto `monpec-sistema-rural`

## 📋 **Agora continue assim:**

### **1. Habilitar APIs** (1 minuto)

No terminal, execute:

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com
```

### **2. Criar Banco de Dados** (10 minutos)

```bash
# Criar instância PostgreSQL
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!

# Aguardar criação (pode levar 5-10 minutos)
# Verificar status:
gcloud sql instances describe monpec-db --format="value(state)"

# Quando estiver "RUNNABLE", continuar:
gcloud sql databases create monpec_db --instance=monpec-db

gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!

# Obter connection name (IMPORTANTE!)
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
```

### **3. Fazer Upload do Código**

**No Cloud Shell Editor:**
1. Clique no ícone de **pasta** (File Explorer) no lado esquerdo
2. Clique com botão direito na pasta raiz (`/home/USER`)
3. Selecione **"Upload Files"** ou **"Upload Folder"**
4. Faça upload da pasta `Monpec_projetista` completa

**Depois do upload:**
```bash
cd Monpec_projetista
ls -la  # Verificar se os arquivos estão lá
```

### **4. Build da Imagem** (10-15 minutos)

```bash
# Verificar se está na pasta correta
pwd
ls -la Dockerfile requirements_producao.txt

# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### **5. Deploy no Cloud Run** (5 minutos)

```bash
# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy (use o CONNECTION_NAME que você anotou)
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"

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
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300

# Obter URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')

echo "🌐 URL: $SERVICE_URL"

# Atualizar CLOUD_RUN_HOST
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST
```

### **6. Executar Migrações** (5 minutos)

```bash
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --command python \
    --args manage.py,migrate \
    --max-retries=1 \
    --memory=512Mi \
    --cpu=1

# Executar
gcloud run jobs execute migrate-db --region us-central1
```

### **7. Testar**

```bash
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
echo "🌐 Seu site está em: $SERVICE_URL"
```

---

## 🆘 **Se Precisar de Ajuda**

- Ver logs: `gcloud run services logs read monpec --region us-central1 --limit 50`
- Ver status: `gcloud run services describe monpec --region us-central1`
- Verificar banco: `gcloud sql instances describe monpec-db`

---

**📖 Ou continue seguindo o arquivo `COMECE_AGORA.md` a partir do Passo 2!**






