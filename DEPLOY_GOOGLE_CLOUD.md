# ☁️ GUIA DE DEPLOY NO GOOGLE CLOUD PLATFORM

## 📋 PRÉ-REQUISITOS

1. ✅ Conta Google Cloud ativa
2. ✅ Projeto criado: `monpec-sistema-rural`
3. ✅ Billing habilitado
4. ✅ gcloud CLI instalado

---

## 🚀 OPÇÃO 1: CLOUD RUN (RECOMENDADO) ⭐

### **Vantagens:**
- ✅ Serverless (paga por uso)
- ✅ Auto-scaling automático
- ✅ HTTPS automático
- ✅ Deploy simples

### **Passo 1: Instalar gcloud CLI**

```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# Ou via Chocolatey
choco install gcloudsdk
```

### **Passo 2: Configurar gcloud**

```bash
gcloud init
# Selecionar projeto: monpec-sistema-rural
# Selecionar região: us-central1
```

### **Passo 3: Habilitar APIs**

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com
```

### **Passo 4: Criar Cloud SQL (PostgreSQL)**

```bash
# Criar instância Cloud SQL
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!

# Criar banco de dados
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!
```

### **Passo 5: Build e Deploy**

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy no Cloud Run
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!
```

### **Passo 6: Configurar Domínio**

```bash
# Mapear domínio customizado
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

---

## 🚀 OPÇÃO 2: APP ENGINE

### **Passo 1: Deploy**

```bash
gcloud app deploy app.yaml
```

### **Passo 2: Abrir no navegador**

```bash
gcloud app browse
```

---

## 🚀 OPÇÃO 3: COMPUTE ENGINE (VM)

### **Passo 1: Criar VM**

```bash
gcloud compute instances create monpec-vm \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
```

### **Passo 2: Conectar e Configurar**

```bash
# Conectar via SSH
gcloud compute ssh monpec-vm --zone=us-central1-a

# No servidor, executar:
sudo apt update
sudo apt install -y python3 python3-pip postgresql nginx git
# ... seguir configuração similar à Locaweb
```

---

## 🔧 CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE

### **No Cloud Run:**

```bash
gcloud run services update monpec \
    --update-env-vars \
    DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
    DEBUG=False,\
    DB_NAME=monpec_db,\
    DB_USER=monpec_user,\
    DB_PASSWORD=Monpec2025!,\
    SECRET_KEY=sua-chave-secreta-aqui
```

### **Ou via Console Web:**

1. Acesse Cloud Run no console
2. Selecione o serviço `monpec`
3. Vá em **Edit & Deploy New Revision**
4. Configure as variáveis de ambiente

---

## 📊 MIGRAÇÃO DE DADOS

### **Exportar da Locaweb:**

```bash
# No servidor Locaweb
pg_dump -h localhost -U monpec_user monpec_db > backup.sql
```

### **Importar no Cloud SQL:**

```bash
# Fazer upload do backup
gcloud sql import sql monpec-db gs://seu-bucket/backup.sql \
    --database=monpec_db
```

---

## 💰 ESTIMATIVA DE CUSTOS

### **Cloud Run:**
- Requisições: ~R$ 0,40 por milhão
- CPU/Memória: ~R$ 0,10 por GB-hora
- **Estimado: R$ 20-50/mês**

### **Cloud SQL (db-f1-micro):**
- Instância: ~R$ 30/mês
- Armazenamento: ~R$ 0,17/GB
- **Estimado: R$ 30-40/mês**

### **Cloud Storage:**
- Armazenamento: ~R$ 0,02/GB
- Transferência: ~R$ 0,12/GB
- **Estimado: R$ 5-10/mês**

**Total: ~R$ 55-100/mês** (similar à Locaweb, mas com mais recursos)

---

## ✅ VERIFICAÇÃO PÓS-DEPLOY

### **Testar Acesso:**

```bash
# Obter URL do Cloud Run
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Testar
curl https://seu-url.a.run.app
```

### **Ver Logs:**

```bash
gcloud run services logs read monpec --region us-central1
```

---

## 🆘 RESOLUÇÃO DE PROBLEMAS

### **Erro de Conexão com Banco:**

```bash
# Verificar conexão Cloud SQL
gcloud sql instances describe monpec-db
```

### **Erro 502 Bad Gateway:**

```bash
# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50
```

### **Custos Altos:**

```bash
# Configurar alertas de orçamento
gcloud billing budgets create \
    --billing-account=SEU_BILLING_ACCOUNT \
    --display-name="Monpec Budget" \
    --budget-amount=100USD \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100
```

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Fazer deploy de teste
2. ✅ Migrar dados
3. ✅ Configurar domínio
4. ✅ Configurar monitoramento
5. ✅ Configurar alertas de custo

---

**🎉 Sistema rodando no Google Cloud!**







