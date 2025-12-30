# 🔧 Resolver Erro de Execução do PowerShell

## ❌ Problema: Script Não Executa

Se o script não está executando, pode ser por:

1. **Política de execução do PowerShell bloqueada**
2. **Erro de sintaxe no script**
3. **Caminho incorreto**

## ✅ Soluções

### Solução 1: Permitir Execução de Scripts

Execute no PowerShell **como Administrador**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois tente executar o script novamente:

```powershell
.\DEPLOY_COMPLETO_POWERSHELL.ps1
```

### Solução 2: Executar Diretamente

Se ainda não funcionar, execute os comandos diretamente:

```powershell
# 1. Configurar variáveis
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# 2. Configurar projeto
gcloud config set project $PROJECT_ID

# 3. Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD

# 4. Build
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

# 5. Deploy
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME `
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP" `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
    --set-env-vars $ENV_VARS `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600

# 6. Ver URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Write-Host "URL: $SERVICE_URL"
```

### Solução 3: Verificar Erros

Execute com verbose para ver erros:

```powershell
.\DEPLOY_COMPLETO_POWERSHELL.ps1 -Verbose
```

Ou execute linha por linha para identificar onde está o erro.

## 🔍 Verificar Política de Execução

```powershell
Get-ExecutionPolicy
```

Se retornar `Restricted`, você precisa alterar:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 Alternativa: Usar Cloud Shell

Se continuar com problemas no PowerShell, **use o Cloud Shell**:

1. Acesse: https://console.cloud.google.com/
2. Clique no ícone **>_** (Cloud Shell)
3. Execute os comandos bash que forneci anteriormente

O Cloud Shell não tem problemas de política de execução!


