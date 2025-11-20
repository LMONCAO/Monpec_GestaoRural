# 🚀 Deploy no Google Cloud - Guia Prático

## ✅ **OPÇÃO RECOMENDADA: Cloud Shell Editor**

O Cloud Shell Editor é a forma mais fácil porque:
- ✅ Já vem com gcloud instalado
- ✅ Não precisa instalar nada
- ✅ Funciona direto no navegador
- ✅ Interface visual amigável

---

## 📋 **PASSO A PASSO COMPLETO**

### **PASSO 1: Acessar Cloud Shell Editor** (2 minutos)

1. Acesse: **https://shell.cloud.google.com**
2. Faça login com sua conta Google
3. Aguarde o Cloud Shell carregar

### **PASSO 2: Autenticar e Configurar Projeto** (3 minutos)

No terminal do Cloud Shell, execute:

```bash
# Autenticar (se ainda não fez)
gcloud auth login

# Criar projeto (se ainda não criou)
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"

# Definir como projeto ativo
gcloud config set project monpec-sistema-rural

# Verificar
gcloud config list
```

### **PASSO 3: Habilitar APIs** (2 minutos)

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com
```

### **PASSO 4: Criar Banco de Dados Cloud SQL** (10 minutos)

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

# Quando estiver "RUNNABLE", continuar:
echo "📊 Criando banco de dados..."
gcloud sql databases create monpec_db --instance=monpec-db

echo "👤 Criando usuário..."
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!

# Obter connection name (IMPORTANTE - anote isso!)
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
echo "✅ Connection Name: $CONNECTION_NAME"
echo "⚠️  ANOTE ESSE VALOR: $CONNECTION_NAME"
```

### **PASSO 5: Fazer Upload do Código** (5 minutos)

**No Cloud Shell Editor:**

1. Clique no ícone de **pasta** (File Explorer) no lado esquerdo
2. Clique com botão direito na pasta raiz (`/home/USER`)
3. Selecione **"Upload Files"** ou **"Upload Folder"**
4. Faça upload da pasta `Monpec_projetista` completa

**OU via Git (se tiver repositório):**
```bash
git clone SEU_REPOSITORIO_URL
cd Monpec_projetista
```

**Depois do upload:**
```bash
cd Monpec_projetista
ls -la  # Verificar se os arquivos estão lá
```

### **PASSO 6: Build da Imagem Docker** (10-15 minutos)

```bash
# Verificar se está na pasta correta
pwd
ls -la Dockerfile requirements_producao.txt

# Build da imagem Docker
echo "🏗️  Iniciando build da imagem (pode levar 10-15 minutos)..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

echo "✅ Build concluído!"
```

### **PASSO 7: Deploy no Cloud Run** (5 minutos)

```bash
# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy (use o CONNECTION_NAME que você anotou)
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

### **PASSO 8: Executar Migrações** (5 minutos)

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

### **PASSO 9: Testar o Site** (2 minutos)

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

## 🆘 **RESOLUÇÃO DE PROBLEMAS**

### **Erro: "Permission denied"**
```bash
gcloud auth login
gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="user:SEU_EMAIL@gmail.com" \
    --role="roles/owner"
```

### **Erro: "Billing not enabled"**
1. Acesse: https://console.cloud.google.com/billing
2. Vincule uma conta de faturamento ao projeto

### **Erro: "Database connection failed"**
```bash
# Verificar connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

### **Erro: "502 Bad Gateway"**
```bash
# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Verificar se migrações foram executadas
gcloud run jobs executions list --job=migrate-db --region us-central1
```

---

## 📊 **CHECKLIST**

- [ ] Cloud Shell Editor aberto
- [ ] Autenticado no Google Cloud
- [ ] Projeto criado: `monpec-sistema-rural`
- [ ] APIs habilitadas
- [ ] Banco de dados Cloud SQL criado
- [ ] Connection Name anotado
- [ ] Código enviado para Cloud Shell
- [ ] Build da imagem concluído
- [ ] Deploy no Cloud Run realizado
- [ ] Migrações executadas
- [ ] Site acessível via URL

---

## 💰 **CUSTOS ESTIMADOS**

- **Cloud Run**: ~R$ 20-50/mês
- **Cloud SQL (db-f1-micro)**: ~R$ 30/mês
- **Total**: ~R$ 50-80/mês

---

## 🎯 **PRÓXIMOS PASSOS (Opcional)**

### **Configurar Domínio:**
```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### **Criar Superusuário:**
```bash
# Conectar ao container e criar via Django admin
# Ou usar o Django admin via interface web
```

---

**🚀 BOM DEPLOY!**

**Comece agora: https://shell.cloud.google.com**







