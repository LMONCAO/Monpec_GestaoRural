# ⚡ Solução Rápida para Erro 500

## 🎯 O Problema

Há **57 migrations não aplicadas** no banco de dados. Isso causa o erro 500.

## ✅ Solução em 2 Passos

### Passo 1: Aplicar Migrations

Copie e cole este comando no Google Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando 57 migrations..."
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migrations aplicadas!"
else
    echo "❌ Erro. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations" --limit=20
    exit 1
fi

gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true
```

### Passo 2: Fazer Deploy do Serviço

Após as migrations serem aplicadas, execute:

```bash
gcloud run deploy monpec \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --allow-unauthenticated
```

---

## 🎯 Comando Completo (Tudo de Uma Vez)

Se preferir fazer tudo de uma vez:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando migrations..."
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "🔄 Fazendo deploy..."
    gcloud run deploy monpec \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --memory=2Gi \
      --cpu=2 \
      --timeout=300 \
      --allow-unauthenticated \
      --quiet
    
    echo ""
    echo "✅ Pronto! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
else
    echo "❌ Erro ao aplicar migrations. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations" --limit=30
fi

gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true
```

---

## 📝 Notas Importantes

1. ⏱️ **Tempo**: Aplicar 57 migrations pode levar 3-5 minutos
2. 🔒 **Permissões**: O diálogo de permissões do Cloud Hub não está relacionado ao erro 500
3. ✅ **Ordem**: Sempre aplique migrations ANTES de fazer deploy
4. 🔍 **Logs**: Se houver erro, os logs serão exibidos automaticamente

---

## ❓ Se Ainda Houver Erro

Verifique os logs detalhados:

```bash
# Logs do job
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations" --limit=50

# Logs do serviço
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=30
```
