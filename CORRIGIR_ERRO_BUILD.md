# 🔧 Corrigir Erro de Build

## ✅ Problema Corrigido

O erro era causado pelo pacote **`django-logging==0.1.0`** que não existe no PyPI.

**Correção aplicada:**
- ✅ Removido `django-logging==0.1.0` do `requirements_producao.txt`
- ✅ Otimizado Dockerfile (removida instalação redundante do gunicorn)

---

## 🚀 Próximos Passos no Cloud Shell

### **Opção 1: Fazer Upload dos Arquivos Corrigidos**

1. No Cloud Shell, clique nos **3 pontos (⋮)** → **"Upload file"**
2. Faça upload do arquivo `requirements_producao.txt` corrigido
3. Faça upload do arquivo `Dockerfile` corrigido
4. Execute o deploy novamente

### **Opção 2: Editar Direto no Cloud Shell**

1. No Cloud Shell, entre na pasta do projeto:
   ```bash
   cd Monpec_GestaoRural
   ```

2. Edite o arquivo requirements_producao.txt:
   ```bash
   nano requirements_producao.txt
   ```

3. Remova ou comente a linha 55:
   - Antes: `django-logging==0.1.0`
   - Depois: `# django-logging==0.1.0  # Removido: pacote não existe`

4. Salve: `Ctrl+X`, depois `Y`, depois `Enter`

5. Edite o Dockerfile:
   ```bash
   nano Dockerfile
   ```

6. Remova a linha redundante (linha 27):
   - Remova: `pip install --no-cache-dir gunicorn`
   - O gunicorn já está no requirements_producao.txt

7. Salve: `Ctrl+X`, depois `Y`, depois `Enter`

---

## 🔄 Executar Deploy Novamente

Depois de corrigir os arquivos, execute novamente:

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

# Build (agora deve funcionar!)
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
```

---

## ✅ O que Foi Corrigido

1. **Removido `django-logging==0.1.0`** (pacote não existe)
2. **Otimizado Dockerfile** (removida instalação redundante)

---

## 🔍 Se Ainda Der Erro

Verifique se há outras dependências problemáticas:

```bash
# Testar instalação localmente (no Cloud Shell)
pip install --dry-run -r requirements_producao.txt
```

---

**Agora o build deve funcionar!** 🚀

