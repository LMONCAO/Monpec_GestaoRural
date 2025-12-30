# ✅ Comandos Corretos para Cloud Shell (BASH)

## ⚠️ Problema Identificado

Você está no **Cloud Shell (bash)**, mas estava tentando executar comandos **PowerShell**!

## ✅ Solução: Comando Bash Correto

### Opção 1: Comando Único (Copiar e Colar)

Cole este comando **COMPLETO** no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural" && SERVICE_NAME="monpec" && REGION="us-central1" && DB_PASSWORD="L6171r12@@jjms" && SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" && echo "🔧 Configurando projeto..." && gcloud config set project $PROJECT_ID && echo "🔧 Corrigindo senha do banco..." && gcloud sql users set-password monpec_user --instance=monpec-db --password="$DB_PASSWORD" 2>/dev/null || echo "⚠️ Aviso" && echo "📦 Verificando requirements..." && (grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt) && echo "🔨 Buildando (5-10 min)..." && TIMESTAMP=$(date +%Y%m%d%H%M%S) && gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP && echo "🚀 Deployando (2-5 min)..." && gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" --memory=2Gi --cpu=2 --timeout=600 && echo "✅✅✅ CONCLUÍDO! ✅✅✅" && SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)") && echo "🔗 URL: $SERVICE_URL" && echo "📋 Login: admin / L6171r12@@"
```

### Opção 2: Passo a Passo

Execute um comando por vez:

```bash
# 1. Configurar variáveis
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# 2. Configurar projeto
gcloud config set project $PROJECT_ID

# 3. Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password="$DB_PASSWORD"

# 4. Build (5-10 minutos)
TIMESTAMP=$(date +%Y%m%d%H%M%S)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP

# 5. Deploy (2-5 minutos)
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:monpec-db" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600

# 6. Ver URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "URL: $SERVICE_URL"
```

## 📋 Diferenças: PowerShell vs Bash

| PowerShell | Bash (Cloud Shell) |
|------------|-------------------|
| `$VAR = "valor"` | `VAR="valor"` |
| `Write-Host` | `echo` |
| `` ` `` (backtick) | `\` (backslash) |
| `;` ou nova linha | `&&` ou `;` |

## ⏱️ Tempo Estimado

- **Build:** 5-10 minutos
- **Deploy:** 2-5 minutos
- **Total:** ~10-15 minutos

## ✅ Após o Deploy

1. Aguarde 1-2 minutos
2. Acesse a URL que aparecerá
3. Login: `admin` / `L6171r12@@`

## 🎯 Use o Comando Único!

É mais fácil - apenas copie e cole tudo de uma vez no Cloud Shell!


