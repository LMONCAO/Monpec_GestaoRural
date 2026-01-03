# 🚨 Resolver Erro 500 DEFINITIVO

## 🔍 Problema Identificado

Pelos logs, há **57 migrations não aplicadas**. Isso está causando o erro 500.

## ⚡ Solução (3 Passos)

### Passo 1: Ver Logs do Job que Falhou

Execute no Cloud Shell:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=30 --format="table(timestamp,severity,textPayload)"
```

Isso mostra o erro exato do job.

---

### Passo 2: Aplicar Migrations (Comando Corrigido)

Copie e cole **TODO** este comando no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando migrations..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-500 --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migrations aplicadas!"
    gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true
else
    echo "❌ Job falhou. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20
    exit 1
fi
```

---

### Passo 3: Fazer Deploy do Serviço (Corrigido)

O problema do deploy foi que usamos `--update-env-vars` incorretamente. Use este comando:

```bash
gcloud run deploy monpec \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated
```

---

## 🎯 Comando Completo (Tudo de Uma Vez)

Se preferir fazer tudo de uma vez, copie e cole este comando completo:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 PASSO 1: Aplicando migrations"
echo "============================================================"
echo ""

gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-500 --region=$REGION --wait

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Job falhou. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20 --format="table(timestamp,severity,textPayload)"
    echo ""
    echo "💡 Verifique os logs acima para entender o erro"
    gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true
    exit 1
fi

gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔄 PASSO 2: Fazendo deploy do serviço"
echo "============================================================"
echo ""

gcloud run deploy $SERVICE_NAME \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated

echo ""
echo "============================================================"
echo "✅ CONCLUÍDO!"
echo "============================================================"
echo ""
echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
```

---

## 🔍 Se Ainda Houver Problemas

### Ver Logs Detalhados do Job:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=50
```

### Ver Logs do Serviço:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=30
```

### Verificar se Cloud SQL está rodando:

```bash
gcloud sql instances describe monpec-db
```

---

## 📝 Notas Importantes

1. **Timeout aumentado**: O job agora tem `--task-timeout=900` (15 minutos) para migrations grandes
2. **Deploy corrigido**: Usamos `gcloud run deploy` em vez de `update` com `--to-latest` (que não existe)
3. **Migrations primeiro**: Sempre aplicar migrations ANTES de fazer deploy do serviço
