# ⚠️ IMPORTANTE: Comandos para PowerShell

## 🔍 Problema Identificado

Você está executando comandos **bash** no **PowerShell do Windows**, e isso causa erros porque:
- PowerShell não interpreta variáveis bash (`$VARIAVEL`)
- Comandos com `&&` não funcionam da mesma forma
- Sintaxe é diferente

## ✅ Soluções

### Opção 1: Usar Cloud Shell (Recomendado)

**O Cloud Shell é baseado em bash e funciona perfeitamente com os comandos que forneci.**

1. Acesse: https://console.cloud.google.com/
2. Clique no ícone **>_** no canto superior direito (Cloud Shell)
3. Cole e execute os comandos bash que forneci

### Opção 2: Usar Script PowerShell

Execute o script `DEPLOY_POWERSHELL.ps1` que criei:

```powershell
.\DEPLOY_POWERSHELL.ps1
```

### Opção 3: Comandos PowerShell Separados

Execute um comando por vez no PowerShell:

```powershell
# 1. Configurar variáveis
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"

# 2. Configurar projeto
gcloud config set project $PROJECT_ID

# 3. Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD

# 4. Gerar timestamp
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

# 5. Build
gcloud builds submit --tag $IMAGE_TAG

# 6. Deploy
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
    --set-env-vars $ENV_VARS `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600

# 7. Ver URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Write-Host "URL: $SERVICE_URL"
```

## 🎯 Recomendação

**Use o Cloud Shell!** É mais fácil e os comandos bash funcionam perfeitamente lá.

1. Acesse: https://console.cloud.google.com/
2. Abra o Cloud Shell (ícone >_)
3. Execute os comandos bash que forneci anteriormente

## 📝 Diferenças PowerShell vs Bash

| Bash (Cloud Shell) | PowerShell |
|-------------------|------------|
| `$VARIAVEL` | `$VARIAVEL` (mesmo) |
| `&&` | `;` ou nova linha |
| `$(date +%Y%m%d)` | `Get-Date -Format "yyyyMMdd"` |
| `echo "texto"` | `Write-Host "texto"` |


