# 🔧 Solução Completa Automática

## ⚡ Execute Este Comando Único

Copie e cole TODO este comando no Google Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔍 Diagnosticando e corrigindo..."
echo ""

# Ver logs
REVISION=$(gcloud run revisions list --service=monpec --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)
if [ -n "$REVISION" ]; then
    echo "📋 Logs da revisão $REVISION:"
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=$REVISION" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -10
    echo ""
fi

# Verificar migrations
echo "📊 Verificando migrations..."
gcloud run jobs delete verificar-mig --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-mig \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,showmigrations,--list" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute verificar-mig --region=$REGION --wait

PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-mig" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
echo "   Migrations pendentes: $PENDENTES"

gcloud run jobs delete verificar-mig --region=$REGION --quiet 2>/dev/null || true

# Aplicar migrations se houver pendentes
if [ "$PENDENTES" -gt 0 ]; then
    echo ""
    echo "🔧 Aplicando migrations..."
    gcloud run jobs delete aplicar-mig-final --region=$REGION --quiet 2>/dev/null || true
    
    gcloud run jobs create aplicar-mig-final \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');call_command('migrate','--noinput')" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2 \
      --task-timeout=900
    
    gcloud run jobs execute aplicar-mig-final --region=$REGION --wait
    gcloud run jobs delete aplicar-mig-final --region=$REGION --quiet 2>/dev/null || true
fi

# Deploy
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
echo "✅ Concluído! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
```

Este script:
1. ✅ Verifica os logs da última revisão
2. ✅ Verifica quantas migrations estão pendentes
3. ✅ Aplica migrations se necessário
4. ✅ Faz deploy do serviço

Execute e me envie a saída completa.


