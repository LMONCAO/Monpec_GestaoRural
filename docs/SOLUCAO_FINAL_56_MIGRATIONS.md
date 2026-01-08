# 🔧 Solução Final: 56 Migrations Não Aplicadas

## 🚨 Problema Identificado

Pelos logs:
- O container inicia o Gunicorn corretamente
- Mas há **56 migrations não aplicadas**
- O container sai (exit(0)) porque detecta migrations pendentes
- O TCP probe falha porque o container não está escutando na porta 8080

**Causa:** Quando marcamos a migration 0034 como fake, o Django "desaplicou" as migrations posteriores. Precisamos aplicar TODAS novamente.

## ✅ Solução

Aplicar todas as migrations, incluindo marcar a 0034 como fake primeiro.

### Comando Completo (Copiar e Colar)

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando todas as migrations..."
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-todas-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Aplicando todas as migrations...');call_command('migrate','--noinput');print('✅ Todas as migrations aplicadas!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-todas-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Todas as migrations aplicadas!"
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
    echo ""
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
fi

gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true
```

## 📝 O que o comando faz

1. **Marca a migration 0034 como fake** (sem executar, pois a tabela já existe)
2. **Aplica todas as migrations restantes** (as 56 pendentes)
3. **Faz deploy do serviço** após aplicar todas

## ⚠️ Importante

- O processo pode levar 3-5 minutos
- Não feche o Cloud Shell durante a execução
- Após aplicar, o serviço deve iniciar corretamente

## 🔍 Se Ainda Houver Problemas

Verifique os logs:

```bash
# Logs do job
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" --limit=50

# Logs do serviço
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=30
```
