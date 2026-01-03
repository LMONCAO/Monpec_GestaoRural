# 🔍 Verificar Status do Serviço

## ⚠️ "Service Unavailable" Ainda Aparece

Isso pode significar:
1. O deploy ainda não terminou completamente
2. O serviço está crashando ao iniciar
3. Há um erro na aplicação

## ✅ Verificar Status

Execute no **PowerShell**:

```powershell
# 1. Ver status do serviço
gcloud run services describe monpec --region=us-central1

# 2. Ver logs de erro
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=20 --format="table(timestamp,severity,textPayload)"

# 3. Ver últimos logs gerais
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=30 --format="value(textPayload)" | Select-Object -Last 20
```

## 🔧 Solução: Verificar e Corrigir

### Passo 1: Verificar se o Serviço Existe

```powershell
gcloud run services list --region=us-central1
```

### Passo 2: Ver Logs de Erro

```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=10
```

### Passo 3: Verificar URL Correta

```powershell
$SERVICE_URL = gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
Write-Host "URL do serviço: $SERVICE_URL"
```

## 🚀 Redeploy Completo (Se Necessário)

Se o serviço não estiver funcionando, execute o script novamente:

```powershell
.\DEPLOY_POWERSHELL.ps1
```

OU execute os comandos manualmente:

```powershell
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"

# Verificar senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD

# Configurar projeto
gcloud config set project $PROJECT_ID

# Build
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

# Deploy
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME `
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP" `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
    --set-env-vars $ENV_VARS `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --min-instances=1

# Ver URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Write-Host "URL: $SERVICE_URL"
```

## 🔍 Diagnóstico Rápido

Execute este comando para ver o que está acontecendo:

```powershell
Write-Host "=== STATUS DO SERVIÇO ===" -ForegroundColor Cyan
gcloud run services describe monpec --region=us-central1 --format="yaml(status.conditions,status.url)"

Write-Host "`n=== ÚLTIMOS LOGS DE ERRO ===" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=5 --format="table(timestamp,severity,textPayload)"
```

## 📝 Checklist

- [ ] Serviço existe? `gcloud run services list --region=us-central1`
- [ ] Serviço está rodando? Ver status
- [ ] Há erros nos logs? Verificar logs acima
- [ ] URL está correta? Verificar URL do serviço
- [ ] Aguardou tempo suficiente? Aguarde 2-3 minutos após deploy


