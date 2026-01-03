#!/bin/bash
# Aplicar migrações uma por uma para identificar qual está falhando

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando quais migrações ainda faltam..."

# Listar migrações pendentes
gcloud run jobs create list-pending-migrations \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,showmigrations,gestao_rural \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando verificação..."
LIST_OUTPUT=$(gcloud run jobs execute list-pending-migrations --region us-central1 --wait 2>&1)
echo "$LIST_OUTPUT" | grep -A 100 "gestao_rural" || echo "$LIST_OUTPUT" | tail -100
gcloud run jobs delete list-pending-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Tentando aplicar migrações uma por uma a partir de 0072..."

# Lista de migrações conhecidas após 0071
MIGRATIONS=(
  "0072_adicionar_campos_obrigatorios_nfe_produto"
  "0073_adicionar_campos_obrigatorios_nfe_item"
  "0074_merge_20251220_2030"
  "0075_adicionar_autorizacao_excedente_orcamento"
  "0076_adicionar_data_liberacao_assinatura"
  "0077_remove_arquivokml_importado_por_and_more"
  "0078_arquivokml_folhapagamento_funcionario_pastagem_and_more"
  "0079_assinaturacliente_data_liberacao"
  "0081_add_usuario_ativo"
)

for MIG in "${MIGRATIONS[@]}"; do
    echo ""
    echo "▶ Aplicando migração $MIG..."
    
    gcloud run jobs create apply-mig-$MIG \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args manage.py,migrate,gestao_rural,$MIG \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 600 \
      --memory 1Gi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    MIG_OUTPUT=$(gcloud run jobs execute apply-mig-$MIG --region us-central1 --wait 2>&1)
    echo "$MIG_OUTPUT" | tail -30
    
    if echo "$MIG_OUTPUT" | grep -q "failed\|ERROR"; then
        echo ""
        echo "❌ Erro na migração $MIG. Verificando logs..."
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-mig-$MIG AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -80
        gcloud run jobs delete apply-mig-$MIG --region us-central1 --quiet 2>&1 || true
        echo ""
        echo "⚠️ Parando aqui. Corrija o erro acima antes de continuar."
        exit 1
    fi
    
    gcloud run jobs delete apply-mig-$MIG --region us-central1 --quiet 2>&1 || true
    echo "✅ Migração $MIG aplicada com sucesso!"
done

echo ""
echo "▶ Aplicando todas as migrações restantes (caso haja alguma que não listamos)..."

gcloud run jobs create apply-all-remaining \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,--noinput \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 900 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

FINAL_OUTPUT=$(gcloud run jobs execute apply-all-remaining --region us-central1 --wait 2>&1)
echo "$FINAL_OUTPUT" | tail -50
gcloud run jobs delete apply-all-remaining --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TODAS AS MIGRAÇÕES CONCLUÍDAS! ✅✅✅"
echo ""
echo "🔐 O admin já foi criado anteriormente."
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








