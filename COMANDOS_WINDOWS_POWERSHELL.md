# 🪟 Comandos para Windows PowerShell

## ⚠️ **IMPORTANTE: Use o Cloud Shell Editor!**

Os comandos abaixo são para **Windows PowerShell**, mas é **MUITO MAIS FÁCIL** usar o **Cloud Shell Editor** (navegador) onde tudo já vem configurado!

### **🌐 RECOMENDAÇÃO: Use Cloud Shell Editor**
1. Acesse: https://shell.cloud.google.com
2. Faça login
3. Use os comandos do arquivo `COMECE_AGORA.md` (funcionam direto!)

---

## 💻 **Se Precisar Usar Windows PowerShell:**

### **1. Habilitar APIs**

```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### **2. Criar Banco de Dados**

```powershell
# Criar instância
gcloud sql instances create monpec-db --database-version=POSTGRES_14 --tier=db-f1-micro --region=us-central1 --root-password=Monpec2025!

# Criar banco
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user --instance=monpec-db --password=Monpec2025!

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)"
Write-Host "Connection Name: $CONNECTION_NAME"
```

### **3. Build da Imagem**

```powershell
# Navegar até a pasta do projeto
cd C:\Monpec_projetista

# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### **4. Deploy no Cloud Run**

```powershell
# Gerar SECRET_KEY
$SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Definir connection name (substitua pelo valor real)
$CONNECTION_NAME = "monpec-sistema-rural:us-central1:monpec-db"

# Deploy (tudo em uma linha)
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300

# Obter URL
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format "value(status.url)"
Write-Host "URL: $SERVICE_URL"

# Extrair host
$CLOUD_RUN_HOST = $SERVICE_URL -replace "https://", ""
Write-Host "Host: $CLOUD_RUN_HOST"

# Atualizar CLOUD_RUN_HOST
gcloud run services update monpec --region us-central1 --update-env-vars "CLOUD_RUN_HOST=$CLOUD_RUN_HOST"
```

### **5. Executar Migrações**

```powershell
# Criar job
gcloud run jobs create migrate-db --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --command python --args "manage.py,migrate" --max-retries=1 --memory=512Mi --cpu=1

# Executar
gcloud run jobs execute migrate-db --region us-central1
```

---

## 🆘 **Problemas Comuns no Windows**

### **Erro: "bash não é reconhecido"**
- ✅ Use PowerShell, não CMD
- ✅ Ou use Cloud Shell Editor (recomendado!)

### **Erro: "comando com \ não funciona"**
- ✅ No Windows, não use `\` para quebrar linha
- ✅ Coloque tudo em uma linha, ou use aspas

### **Erro: "python não encontrado"**
```powershell
# Verificar se Python está instalado
python --version

# Se não funcionar, tente:
py --version
```

---

## ✅ **MELHOR OPÇÃO: Cloud Shell Editor**

1. Acesse: https://shell.cloud.google.com
2. Faça login
3. Use os comandos do `COMECE_AGORA.md` (funcionam direto!)
4. Não precisa instalar nada, tudo já vem configurado!

---

**💡 Dica: O Cloud Shell Editor é muito mais fácil e tudo já vem pronto!**






