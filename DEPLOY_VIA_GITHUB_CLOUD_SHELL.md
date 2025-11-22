# 🚀 Deploy via GitHub no Cloud Shell

Como fazer deploy usando o repositório GitHub que está sincronizado com seu código local.

---

## ✅ Vantagens

- ✅ Não precisa fazer upload manual
- ✅ Código sempre sincronizado
- ✅ Mais rápido e confiável
- ✅ Fácil de atualizar depois

---

## 📋 Passo 1: Fazer Commit e Push das Correções

**No seu computador local (PowerShell):**

```powershell
# 1. Verificar status
git status

# 2. Adicionar arquivos corrigidos
git add requirements_producao.txt Dockerfile

# 3. Fazer commit
git commit -m "Corrigir: remover django-logging e otimizar Dockerfile"

# 4. Fazer push para GitHub
git push origin main
# ou: git push origin master (depende do nome da branch)
```

---

## 📋 Passo 2: Clonar no Cloud Shell

**No Google Cloud Shell:**

```bash
# 1. Clonar repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# 2. Entrar na pasta
cd SEU_REPOSITORIO

# 3. Verificar se os arquivos corrigidos estão lá
grep -n "django-logging" requirements_producao.txt || echo "✅ Correto: django-logging não encontrado"
```

---

## 📋 Passo 3: Executar Deploy

**No Cloud Shell:**

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Variáveis
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
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
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
```

---

## 🔄 Atualizar Depois (Quando Fizer Mudanças)

**No seu computador:**
```powershell
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

**No Cloud Shell:**
```bash
cd SEU_REPOSITORIO
git pull origin main
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1
```

---

## 🔐 Se o Repositório for Privado

Se seu repositório GitHub for privado, você precisa autenticar:

```bash
# No Cloud Shell
gh auth login
# Ou use token:
git clone https://SEU_TOKEN@github.com/SEU_USUARIO/SEU_REPOSITORIO.git
```

---

## ✅ Checklist

- [ ] Fazer commit e push das correções no computador local
- [ ] Clonar repositório no Cloud Shell
- [ ] Verificar se arquivos corrigidos estão presentes
- [ ] Executar deploy
- [ ] Verificar URL do serviço

---

**Última atualização:** Dezembro 2025

