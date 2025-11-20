# 📋 Comandos Individuais - Cloud Shell

## ⚡ **Copie e cole um comando por vez no terminal do Cloud Shell**

---

### **1. Verificar Autenticação**
```bash
gcloud auth list
```

### **2. Criar Projeto**
```bash
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"
```

### **3. Configurar Projeto**
```bash
gcloud config set project monpec-sistema-rural
```

### **4. Habilitar APIs**
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com cloudresourcemanager.googleapis.com containerregistry.googleapis.com
```

### **5. Criar Banco de Dados**
```bash
# Criar instância (pode levar 5-10 minutos)
gcloud sql instances create monpec-db --database-version=POSTGRES_14 --tier=db-f1-micro --region=us-central1 --root-password=Monpec2025!

# Criar banco
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user --instance=monpec-db --password=Monpec2025!

# Obter connection name (ANOTE ISSO!)
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

### **6. Fazer Upload do Código**

**Via Interface:**
1. No Cloud Shell Editor, clique no ícone de **pasta** (File Explorer) no lado esquerdo
2. Clique com botão direito na pasta raiz (`/home/USER`)
3. Selecione **"Upload Files"** ou **"Upload Folder"**
4. Faça upload da pasta `Monpec_projetista` completa

**Depois do upload:**
```bash
cd Monpec_projetista
ls -la  # Verificar se os arquivos estão lá
```

### **7. Build da Imagem**
```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### **8. Deploy no Cloud Run**
```bash
# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Definir connection name (use o valor que você anotou)
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300

# Obter URL
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

### **9. Atualizar CLOUD_RUN_HOST**
```bash
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')
gcloud run services update monpec --region us-central1 --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST
```

### **10. Executar Migrações**
```bash
# Criar job
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY \
    --command python \
    --args manage.py,migrate \
    --max-retries=1 \
    --memory=512Mi \
    --cpu=1

# Executar
gcloud run jobs execute migrate-db --region us-central1
```

### **11. Ver Logs**
```bash
gcloud run services logs tail monpec --region us-central1
```

### **12. Ver Status**
```bash
gcloud run services describe monpec --region us-central1
```

---

## 🚀 **OU USE OS SCRIPTS AUTOMÁTICOS**

### **Script 1: Configuração Inicial**
```bash
bash COMANDOS_CLOUD_SHELL_PRONTOS.sh
```

### **Script 2: Deploy Completo (após upload do código)**
```bash
cd Monpec_projetista
bash COMANDOS_DEPLOY_COMPLETO.sh
```

---

**💡 Dica: Execute os comandos um por vez para ver o progresso!**







