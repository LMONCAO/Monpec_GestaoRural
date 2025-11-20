# ⚡ INÍCIO RÁPIDO - Cloud Shell Editor

## 🎯 **3 Passos para Começar AGORA**

### **1. Abrir Cloud Shell Editor**
👉 **Acesse:** https://shell.cloud.google.com

### **2. Autenticar e Configurar**
```bash
gcloud auth login
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"
gcloud config set project monpec-sistema-rural
```

### **3. Seguir o Guia Completo**
👉 **Abra o arquivo:** `DEPLOY_GOOGLE_CLOUD_AGORA.md`

---

## 📋 **Comandos Essenciais (Copy/Paste)**

### **Habilitar APIs:**
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com
```

### **Criar Banco:**
```bash
gcloud sql instances create monpec-db --database-version=POSTGRES_14 --tier=db-f1-micro --region=us-central1 --root-password=Monpec2025!
gcloud sql databases create monpec_db --instance=monpec-db
gcloud sql users create monpec_user --instance=monpec-db --password=Monpec2025!
```

### **Build e Deploy:**
```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated
```

---

**🚀 Comece agora em: https://shell.cloud.google.com**






