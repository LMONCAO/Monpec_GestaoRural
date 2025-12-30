# ⚡ Resumo: PowerShell vs Cloud Shell

## ⚠️ Você está no PowerShell do Windows

Os comandos que forneci são para **bash** (Cloud Shell), não para PowerShell.

## ✅ Solução Rápida

### Opção 1: Usar Cloud Shell (Mais Fácil)

1. Acesse: https://console.cloud.google.com/
2. Clique no ícone **>_** (Cloud Shell) no topo
3. Cole e execute os comandos bash que forneci

### Opção 2: Executar Script PowerShell

Execute este arquivo que criei:

```powershell
.\DEPLOY_POWERSHELL.ps1
```

### Opção 3: Comandos PowerShell (Um por Vez)

```powershell
# Configurar
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"

# Configurar projeto
gcloud config set project $PROJECT_ID

# Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD

# Build e Deploy
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP" --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" --set-env-vars $ENV_VARS --memory=2Gi --cpu=2 --timeout=600
```

## 🎯 Recomendação

**Use o Cloud Shell!** É mais fácil e os comandos funcionam perfeitamente.

Acesse: https://console.cloud.google.com/ → Clique em **>_** (Cloud Shell)


