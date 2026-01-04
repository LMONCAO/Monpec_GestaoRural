# 🔧 Solução: Migration 0036 Falhando

## 🚨 Problema

A migration `0036_ajusteorcamentocompra_orcamentocompramensal_and_more` está falhando porque a tabela `gestao_rural_orcamentocompramensal` já existe no banco.

**Erro:**
```
psycopg2.errors.DuplicateTable: relation "gestao_rural_orcamentocompramensal" already exists
```

## ✅ Solução

Marcar a migration 0036 como fake (assim como fizemos com 0034 e 0035).

### Comando Completo

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando migrations (marcando 0034, 0035 e 0036 como fake)..."
gcloud run jobs delete aplicar-mig-com-fakes --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-mig-com-fakes \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Marcando 0035 como fake...');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');print('Marcando 0036 como fake...');call_command('migrate','gestao_rural','0036_ajusteorcamentocompra_orcamentocompramensal_and_more','--fake');print('Aplicando migrations restantes...');call_command('migrate','--noinput');print('✅ Concluído!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-mig-com-fakes --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "📋 Verificando estado final..."
    gcloud run jobs delete verificar-final --region=$REGION --quiet 2>/dev/null || true
    
    gcloud run jobs create verificar-final \
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
    
    gcloud run jobs execute verificar-final --region=$REGION --wait
    
    PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
    echo ""
    echo "   Migrations pendentes: $PENDENTES"
    
    gcloud run jobs delete verificar-final --region=$REGION --quiet 2>/dev/null || true
else
    echo ""
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-mig-com-fakes" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30
fi

gcloud run jobs delete aplicar-mig-com-fakes --region=$REGION --quiet 2>/dev/null || true
```

## 📝 O que o comando faz

1. **Marca 0034 como fake** (ContaFinanceira já existe)
2. **Marca 0035 como fake** (PlanoAssinatura já existe)
3. **Marca 0036 como fake** (OrcamentoCompraMensal já existe)
4. **Aplica todas as migrations restantes**
5. **Verifica quantas migrations ainda estão pendentes**

## ⚠️ Importante

Se outras migrations também falharem com "table already exists", repita o processo:
1. Veja qual migration está falhando
2. Marque como fake
3. Continue aplicando as restantes

Execute o comando acima e me avise o resultado!


