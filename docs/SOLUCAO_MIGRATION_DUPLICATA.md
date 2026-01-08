# 🔧 Solução: Migration Duplicada

## 🚨 Problema Identificado

O erro mostra que:
- A migration `0034_financeiro_reestruturado` está tentando criar a tabela `gestao_rural_contafinanceira`
- Mas a tabela **já existe** no banco de dados
- Isso significa que a tabela foi criada, mas a migration não está registrada como aplicada

**Erro:**
```
django.db.utils.ProgrammingError: relation "gestao_rural_contafinanceira" already exists
```

## ✅ Solução

Precisamos marcar a migration como aplicada **sem executá-la** (usando `--fake`).

### Comando Rápido (Copiar e Colar)

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Corrigindo migration duplicada..."
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate gestao_rural 0034_financeiro_reestruturado --fake && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migration corrigida!"
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
    echo "❌ Erro. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=30
fi

gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
```

## 📝 O que o comando faz

1. **Marca a migration como aplicada** usando `--fake` (sem executar)
2. **Aplica as migrations restantes** normalmente
3. **Faz deploy do serviço** após corrigir

## ⚠️ Importante

- `--fake` marca a migration como aplicada sem executá-la
- Isso é seguro porque a tabela já existe
- As migrations restantes serão aplicadas normalmente

## 🔍 Se Ainda Houver Problemas

Verifique se há outras migrations com o mesmo problema:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=50
```

Se houver outras tabelas duplicadas, repita o processo para cada uma.
