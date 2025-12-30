# ⚠️ Corrigir "Service Unavailable"

## 🔍 Diagnóstico Rápido

Execute no **Cloud Shell** para ver o que está acontecendo:

```bash
# Ver status do serviço
gcloud run services describe monpec --region=us-central1

# Ver logs de erro
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
    --limit=10
```

## ✅ Solução: Redeploy Completo

Execute este comando completo no **Cloud Shell**:

```bash
PROJECT_ID="monpec-sistema-rural" && SERVICE_NAME="monpec" && REGION="us-central1" && DB_PASSWORD="L6171r12@@jjms" && echo "🔧 Verificando senha do banco..." && gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>/dev/null || echo "⚠️ Aviso" && gcloud config set project $PROJECT_ID && grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt && TIMESTAMP=$(date +%Y%m%d%H%M%S) && echo "🔨 Buildando..." && gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP && echo "🚀 Deployando..." && gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" --memory=2Gi --cpu=2 --timeout=600 && echo "✅✅✅ CONCLUÍDO! ✅✅✅" && SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)") && echo "🔗 URL: $SERVICE_URL"
```

## 📋 O que este comando faz:

1. ✅ Verifica/corrige senha do banco
2. ✅ Faz build da imagem
3. ✅ Faz deploy no Cloud Run
4. ✅ Configura recursos (2GB RAM, 2 CPUs, timeout 600s)
5. ✅ Mostra a URL do serviço

## ⏱️ Após o Deploy

1. **Aguarde 1-2 minutos** para o serviço inicializar
2. **Acesse a URL** que aparecerá no final
3. **Teste o login** com:
   - Username: `admin`
   - Senha: `L6171r12@@`

## 🐛 Se ainda não funcionar

Verifique os logs:

```bash
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
    --limit=30 \
    --format="value(textPayload)"
```


