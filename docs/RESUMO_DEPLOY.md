# 📋 RESUMO DO DEPLOY - MONPEC

## ✅ O que foi configurado:

1. **Scripts de Deploy Criados:**
   - `DEPLOY_FINAL_COMPLETO.ps1` - Script completo com todas as funcionalidades
   - `DEPLOY_AGORA_SIMPLIFICADO.ps1` - Versão simplificada
   - `.gcloudignore` - Arquivo para ignorar arquivos desnecessários no build

2. **Configurações:**
   - ✅ Landing page atualizada (já está no código)
   - ✅ Formulário de demonstração funcionando (já está no código)
   - ✅ Credenciais Mercado Pago (serão lidas do arquivo `.env`)
   - ✅ Senha admin configurada: `L6171r12@@`
   - ✅ Script `criar_admin_producao.py` já existe e está configurado

## 🚀 Deploy em Execução

O build da imagem Docker está sendo executado agora. Este processo pode levar 5-15 minutos.

## 📝 Próximos Passos Após o Build:

### 1. Verificar se o build terminou:

```powershell
gcloud builds list --limit=5
```

### 2. Fazer o deploy no Cloud Run:

Após o build terminar, execute os comandos para fazer o deploy:

```powershell
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Ler credenciais do .env
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Adicionar Mercado Pago se estiver no .env
if (Test-Path ".env") {
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^MERCADOPAGO_ACCESS_TOKEN=(.+)$") {
            $envVars += "MERCADOPAGO_ACCESS_TOKEN=$($matches[1].Trim())"
        }
        if ($line -match "^MERCADOPAGO_PUBLIC_KEY=(.+)$") {
            $envVars += "MERCADOPAGO_PUBLIC_KEY=$($matches[1].Trim())"
        }
        if ($line -match "^SECRET_KEY=(.+)$") {
            $envVars += "SECRET_KEY=$($matches[1].Trim())"
        }
        if ($line -match "^DB_NAME=(.+)$") {
            $envVars += "DB_NAME=$($matches[1].Trim())"
        }
        if ($line -match "^DB_USER=(.+)$") {
            $envVars += "DB_USER=$($matches[1].Trim())"
        }
        if ($line -match "^DB_PASSWORD=(.+)$") {
            $envVars += "DB_PASSWORD=$($matches[1].Trim())"
        }
        if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") {
            $envVars += "CLOUD_SQL_CONNECTION_NAME=$($matches[1].Trim())"
        }
    }
    
    if ($envVars -contains "*MERCADOPAGO*") {
        $envVars += "PAYMENT_GATEWAY_DEFAULT=mercadopago"
        $envVars += "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/"
        $envVars += "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
    }
}

$envVarsString = $envVars -join ","

# Deploy
gcloud run deploy $SERVICE_NAME `
    --image $imageTag `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars $envVarsString `
    --memory 1Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080
```

### 3. Configurar Admin:

Após o deploy, execute o script `criar_admin_producao.py` para criar/atualizar o usuário admin com a senha `L6171r12@@`.

Você pode fazer isso via Cloud Shell ou Cloud SQL.

## 🔐 Credenciais:

- **Usuário Admin**: admin
- **Email**: admin@monpec.com.br  
- **Senha**: L6171r12@@

## ⚠️ Importante:

- Certifique-se de que o arquivo `.env` contém as credenciais do Mercado Pago
- Após o deploy, execute `criar_admin_producao.py` para ativar o login admin
- Verifique se todas as migrações foram executadas
