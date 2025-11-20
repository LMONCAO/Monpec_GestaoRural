# 🚀 GUIA COMPLETO: Como Fazer o Site Funcionar no Google Cloud

## 📋 ÍNDICE
1. [Pré-requisitos](#pré-requisitos)
2. [Opção 1: Cloud Run (Recomendado)](#opção-1-cloud-run-recomendado)
3. [Opção 2: App Engine](#opção-2-app-engine)
4. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
5. [Deploy Automático](#deploy-automático)
6. [Configuração de Domínio](#configuração-de-domínio)
7. [Troubleshooting](#troubleshooting)

---

## ✅ PRÉ-REQUISITOS

### 1. Conta Google Cloud
- Acesse: https://console.cloud.google.com
- Crie uma conta ou faça login
- **IMPORTANTE**: Ative o billing (cartão de crédito necessário)

### 2. Criar Projeto no Google Cloud
```bash
# No Cloud Shell ou terminal local
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"
gcloud config set project monpec-sistema-rural
```

### 3. Instalar Google Cloud SDK (gcloud CLI)

**Windows (PowerShell como Administrador):**
```powershell
# Opção 1: Download direto
Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile "$env:TEMP\GoogleCloudSDKInstaller.exe"
Start-Process "$env:TEMP\GoogleCloudSDKInstaller.exe"

# Opção 2: Via Chocolatey (se tiver instalado)
choco install gcloudsdk
```

**Ou use o Cloud Shell Editor** (já está aberto na sua tela):
- Acesse: https://shell.cloud.google.com
- O gcloud já vem instalado!

---

## 🚀 OPÇÃO 1: CLOUD RUN (RECOMENDADO) ⭐

### **Por que Cloud Run?**
- ✅ Serverless (paga apenas pelo uso)
- ✅ Auto-scaling automático
- ✅ HTTPS gratuito
- ✅ Deploy simples e rápido
- ✅ Custo baixo (~R$ 20-50/mês)

### **Passo 1: Autenticar no Google Cloud**

No Cloud Shell Editor (ou terminal local):
```bash
gcloud auth login
# Abrirá o navegador para autenticar
```

### **Passo 2: Configurar Projeto**

```bash
# Definir projeto
gcloud config set project monpec-sistema-rural

# Verificar configuração
gcloud config list
```

### **Passo 3: Habilitar APIs Necessárias**

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com
```

### **Passo 4: Criar Banco de Dados Cloud SQL**

```bash
# Criar instância PostgreSQL
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

**⚠️ IMPORTANTE**: Anote a connection name:
```bash
gcloud sql instances describe monpec-db --format="value(connectionName)"
# Exemplo: monpec-sistema-rural:us-central1:monpec-db
```

### **Passo 5: Fazer Upload do Código**

**No Cloud Shell Editor:**
1. Clique em "Open Editor" (ícone de pasta)
2. Faça upload dos arquivos do projeto ou clone do Git
3. Navegue até a pasta do projeto

**Ou via terminal:**
```bash
# Se o código estiver no seu PC, use o Cloud Shell para fazer upload
# Ou clone de um repositório Git
git clone SEU_REPOSITORIO
cd Monpec_projetista
```

### **Passo 6: Build e Deploy**

```bash
# Build da imagem Docker
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy no Cloud Run
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
        CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,\
        SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
```

### **Passo 7: Executar Migrações**

```bash
# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')

# Executar migrações via Cloud Run Jobs ou manualmente
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db \
    --command python \
    --args manage.py,migrate

# Executar o job
gcloud run jobs execute migrate-db --region us-central1
```

**Ou execute manualmente conectando ao container:**
```bash
# Criar container temporário para executar comandos
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars RUN_MIGRATIONS=true
```

### **Passo 8: Verificar Deploy**

```bash
# Obter URL do serviço
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Testar no navegador
# A URL será algo como: https://monpec-xxxxx-uc.a.run.app
```

---

## 🚀 OPÇÃO 2: APP ENGINE

### **Passo 1: Deploy**

```bash
gcloud app deploy app.yaml
```

### **Passo 2: Abrir no Navegador**

```bash
gcloud app browse
```

---

## 🗄️ CONFIGURAÇÃO DO BANCO DE DADOS

### **Migrar Dados da Locaweb para Cloud SQL**

Se você já tem dados na Locaweb:

```bash
# 1. Exportar do servidor Locaweb
pg_dump -h 10.1.1.234 -U monpec_user monpec_db > backup.sql

# 2. Fazer upload para Cloud Storage
gsutil mb gs://monpec-backups
gsutil cp backup.sql gs://monpec-backups/

# 3. Importar no Cloud SQL
gcloud sql import sql monpec-db \
    gs://monpec-backups/backup.sql \
    --database=monpec_db
```

---

## 🌐 CONFIGURAÇÃO DE DOMÍNIO

### **Mapear monpec.com.br para Cloud Run**

```bash
# 1. Verificar domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

# 2. Configurar DNS no seu provedor
# Adicionar registro CNAME:
# Nome: @ (ou monpec.com.br)
# Valor: ghs.googlehosted.com
```

**Configuração DNS:**
- No seu provedor de domínio (Registro.br, GoDaddy, etc.)
- Adicionar registro CNAME apontando para `ghs.googlehosted.com`
- Aguardar propagação (pode levar até 48h)

---

## 🔧 DEPLOY AUTOMÁTICO

### **Usando Cloud Build (CI/CD)**

O arquivo `cloudbuild.yaml` já está configurado! Basta:

```bash
# Conectar repositório Git (GitHub, GitLab, etc.)
gcloud builds triggers create github \
    --repo-name=SEU_REPO \
    --repo-owner=SEU_USUARIO \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml

# Ou fazer deploy manual
gcloud builds submit --config cloudbuild.yaml
```

---

## 🆘 TROUBLESHOOTING

### **Erro: "Permission denied"**
```bash
# Verificar permissões
gcloud projects get-iam-policy monpec-sistema-rural

# Adicionar permissões necessárias
gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="user:SEU_EMAIL@gmail.com" \
    --role="roles/owner"
```

### **Erro: "Database connection failed"**
```bash
# Verificar conexão Cloud SQL
gcloud sql instances describe monpec-db

# Verificar se a connection name está correta
echo $CLOUD_SQL_CONNECTION_NAME
```

### **Erro: "502 Bad Gateway"**
```bash
# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Verificar se as migrações foram executadas
gcloud run jobs logs read migrate-db --region us-central1
```

### **Erro: "Static files not found"**
```bash
# Coletar arquivos estáticos localmente
python manage.py collectstatic --noinput

# Ou configurar Cloud Storage (recomendado)
gsutil mb gs://monpec-static
gsutil -m rsync -r staticfiles/ gs://monpec-static/
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

## ✅ CHECKLIST FINAL

- [ ] Conta Google Cloud criada e billing ativado
- [ ] Projeto criado: `monpec-sistema-rural`
- [ ] APIs habilitadas
- [ ] Cloud SQL criado e configurado
- [ ] Código enviado para Cloud Shell ou repositório
- [ ] Build da imagem Docker concluído
- [ ] Deploy no Cloud Run realizado
- [ ] Migrações executadas
- [ ] Site acessível via URL do Cloud Run
- [ ] Domínio configurado (opcional)
- [ ] Testes realizados

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Fazer deploy de teste
2. ✅ Migrar dados (se necessário)
3. ✅ Configurar domínio customizado
4. ✅ Configurar monitoramento e alertas
5. ✅ Configurar backup automático do banco
6. ✅ Configurar CI/CD para deploy automático

---

**🎉 Pronto! Seu site estará funcionando no Google Cloud!**

Para mais ajuda, consulte:
- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Documentação Cloud SQL](https://cloud.google.com/sql/docs)
- [Documentação Django no GCP](https://cloud.google.com/python/django)






