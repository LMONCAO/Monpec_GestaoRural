# 🚀 COMECE AGORA - Deploy no Google Cloud

## ⚡ **INÍCIO RÁPIDO - Copie e Cole no Cloud Shell**

### **PASSO 1: Autenticar e Configurar** (2 min)

```bash
# Autenticar no Google Cloud
gcloud auth login

# Criar projeto (se ainda não criou)
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"

# Definir como projeto ativo
gcloud config set project monpec-sistema-rural

# Verificar
echo "✅ Projeto configurado: $(gcloud config get-value project)"
```

### **PASSO 2: Habilitar APIs** (1 min)

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com

echo "✅ APIs habilitadas!"
```

### **PASSO 3: Criar Banco de Dados** (10 min - aguarde!)

```bash
# Criar instância PostgreSQL
echo "⏳ Criando instância PostgreSQL (pode levar 5-10 minutos)..."
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!

# Aguardar criação (verificar status)
echo "⏳ Aguardando instância ficar pronta..."
gcloud sql instances describe monpec-db --format="value(state)"

# Criar banco de dados
echo "📊 Criando banco de dados..."
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
echo "👤 Criando usuário..."
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!

# Obter connection name (IMPORTANTE - anote isso!)
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
echo "✅ Connection Name: $CONNECTION_NAME"
echo "⚠️  ANOTE ESSE VALOR: $CONNECTION_NAME"
```

### **PASSO 4: Upload do Código** (5 min)

**Opção A: Se você já está no Cloud Shell Editor:**
```bash
# Navegar para a pasta do projeto
cd ~
# Se você fez upload via interface, o código já está lá
# Verificar se está na pasta correta
pwd
ls -la
```

**Opção B: Fazer upload via interface:**
1. No Cloud Shell Editor, clique no ícone de **pasta** (File Explorer)
2. Clique com botão direito na pasta raiz (`/home/USER`)
3. Selecione **"Upload Files"** ou **"Upload Folder"**
4. Faça upload da pasta `Monpec_projetista` completa

**Depois do upload:**
```bash
cd Monpec_projetista
ls -la  # Verificar se os arquivos estão lá
```

### **PASSO 5: Build da Imagem** (10-15 min)

```bash
# Verificar se está na pasta correta
pwd
ls -la Dockerfile requirements_producao.txt

# Build da imagem Docker
echo "🏗️  Iniciando build da imagem (pode levar 10-15 minutos)..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

echo "✅ Build concluído!"
```

### **PASSO 6: Deploy no Cloud Run** (5 min)

```bash
# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy (substitua CONNECTION_NAME pelo valor que você anotou)
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"  # ⚠️ SUBSTITUA SE DIFERENTE!

echo "🚀 Fazendo deploy no Cloud Run..."
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
    --timeout=300 \
    --max-instances=10

# Obter URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')

echo "🌐 URL do serviço: $SERVICE_URL"
echo "📝 Host: $CLOUD_RUN_HOST"

# Atualizar CLOUD_RUN_HOST
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST

echo "✅ Deploy concluído!"
```

### **PASSO 7: Executar Migrações** (5 min)

```bash
# Criar job de migração
echo "🔄 Criando job de migração..."
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

# Executar job
echo "⏳ Executando migrações..."
gcloud run jobs execute migrate-db --region us-central1

# Aguardar conclusão
echo "⏳ Aguardando conclusão..."
sleep 10

# Ver logs
echo "📋 Logs da migração:"
gcloud run jobs executions list --job=migrate-db --region us-central1 --limit=1

echo "✅ Migrações executadas!"
```

### **PASSO 8: Testar o Site** (2 min)

```bash
# Obter URL final
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
echo "🌐 Seu site está em: $SERVICE_URL"
echo ""
echo "📋 Para ver logs:"
echo "gcloud run services logs tail monpec --region us-central1"
echo ""
echo "🎉 Deploy concluído com sucesso!"
```

---

## 🆘 **SE ALGO DER ERRADO**

### **Ver Logs:**
```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### **Verificar Status:**
```bash
gcloud run services describe monpec --region us-central1
```

### **Verificar Banco:**
```bash
gcloud sql instances describe monpec-db
```

### **Re-executar Migrações:**
```bash
gcloud run jobs execute migrate-db --region us-central1
```

---

## ✅ **CHECKLIST RÁPIDO**

- [ ] Passo 1: Autenticado e projeto criado
- [ ] Passo 2: APIs habilitadas
- [ ] Passo 3: Banco de dados criado (anotar CONNECTION_NAME)
- [ ] Passo 4: Código enviado para Cloud Shell
- [ ] Passo 5: Build concluído
- [ ] Passo 6: Deploy concluído (anotar URL)
- [ ] Passo 7: Migrações executadas
- [ ] Passo 8: Site acessível

---

## 🎯 **PRÓXIMOS PASSOS (Opcional)**

### **Criar Superusuário:**
```bash
# Conectar ao container e criar superusuário manualmente
# Ou usar o Django admin via interface web
```

### **Configurar Domínio:**
```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

---

**🚀 BOM DEPLOY!**

