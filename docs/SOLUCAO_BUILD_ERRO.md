# 🔧 Solução: Erro no Build

## ❌ Problema

O build está falhando porque o gcloud está tentando incluir arquivos do diretório `.cursor` que não existem mais.

## ✅ Solução: Usar Cloud Shell

O **Cloud Shell** não tem esse problema porque não tem acesso aos arquivos locais do Cursor.

### Execute no Cloud Shell:

1. **Acesse:** https://console.cloud.google.com/
2. **Abra o Cloud Shell** (ícone >_ no topo)
3. **Execute:**

```bash
# Fazer upload do código (se necessário)
# OU clone do repositório se estiver no Git

# Depois execute o deploy
bash deploy_completo_auditado.sh
```

## 🔄 Alternativa: Build Manual no Cloud Shell

Se preferir fazer manualmente no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# Configurar projeto
gcloud config set project $PROJECT_ID

# Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password="$DB_PASSWORD"

# Build
TIMESTAMP=$(date +%Y%m%d%H%M%S)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP

# Deploy
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:monpec-db" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600

# Ver URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "URL: $SERVICE_URL"
```

## 💡 Por que Cloud Shell?

- ✅ Não tem acesso a arquivos locais problemáticos
- ✅ Ambiente limpo e configurado
- ✅ Não precisa de .gcloudignore ou .dockerignore
- ✅ Mais rápido e confiável

---

**Recomendação: Use o Cloud Shell para fazer o build e deploy!** 🚀


