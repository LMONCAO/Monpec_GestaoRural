# 🔧 Solução Definitiva - Erro 500 Internal Server Error

## 🎯 Primeiro: Ver o Erro Real

Execute no Cloud Shell:

```bash
gcloud run services logs read monpec --region us-central1 --limit=100
```

**Procure por:**
- `ERROR`
- `Exception`
- `Traceback`
- `Failed`
- `Database connection`
- `SECRET_KEY`

---

## 🔍 Problemas Mais Comuns e Soluções

### **1. Erro: "SECRET_KEY não configurada"**

**Solução:**
```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t"
```

### **2. Erro: "Database connection failed"**

**Solução:**
```bash
# Verificar se Cloud SQL está rodando
gcloud sql instances describe monpec-db

# Verificar connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"

# Atualizar serviço com connection correta
gcloud run services update monpec \
    --region us-central1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```

### **3. Erro: "ModuleNotFoundError" ou "ImportError"**

**Solução:**
```bash
# Verificar requirements.txt
cat requirements.txt | grep -i "gunicorn\|whitenoise\|django"

# Se faltar, adicionar
echo "gunicorn" >> requirements.txt
echo "whitenoise" >> requirements.txt

# Fazer build novamente
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# Fazer deploy novamente
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1
```

### **4. Erro: "No such file or directory" ou arquivo faltando**

**Solução:**
```bash
# Verificar se todos os arquivos foram enviados
# Fazer upload novamente dos arquivos faltantes
```

### **5. Erro: "Migration" ou problemas com banco**

**Solução:**
```bash
# Aplicar migrações novamente
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

---

## 🚀 Solução Completa (Tentativa de Corrigir Tudo)

Execute este comando no Cloud Shell:

```bash
#!/bin/bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "1. Verificando logs..."
gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50 | tail -20

echo ""
echo "2. Atualizando todas as variáveis de ambiente..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

echo ""
echo "3. Aplicando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait

echo ""
echo "4. Obtendo URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "URL: $SERVICE_URL"

echo ""
echo "Aguarde 30 segundos e teste: $SERVICE_URL"
```

---

## 📋 Checklist de Verificação

Execute cada comando e me diga o resultado:

1. **Ver logs:**
   ```bash
   gcloud run services logs read monpec --region us-central1 --limit=100 | grep -i "error\|exception\|failed"
   ```

2. **Ver status:**
   ```bash
   gcloud run services describe monpec --region us-central1 --format="value(status.conditions[0].status)"
   ```

3. **Ver variáveis:**
   ```bash
   gcloud run services describe monpec --region us-central1 --format="yaml(spec.template.spec.containers[0].env)"
   ```

4. **Testar URL:**
   ```bash
   curl -I $(gcloud run services describe monpec --region us-central1 --format="value(status.url)")
   ```

---

## ⚠️ IMPORTANTE

**Me envie o resultado do primeiro comando (logs)** para eu identificar o erro exato e criar a solução correta!

Execute:
```bash
gcloud run services logs read monpec --region us-central1 --limit=100
```

E me mostre o que apareceu, especialmente linhas com:
- ERROR
- Exception
- Traceback
- Failed
















