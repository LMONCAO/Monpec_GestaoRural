# Guia de Deploy - MONPEC no Google Cloud

## Pré-requisitos

1. **Google Cloud SDK instalado**
   - Download: https://cloud.google.com/sdk/docs/install
   - Verificar: `gcloud --version`

2. **Docker instalado**
   - Download: https://www.docker.com/products/docker-desktop
   - Verificar: `docker --version`

3. **Autenticação no Google Cloud**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **Projeto Google Cloud configurado**
   ```bash
   gcloud config set project SEU_PROJECT_ID
   ```

## Configuração Inicial

### 1. Habilitar APIs necessárias

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### 2. Configurar variáveis de ambiente

No Google Cloud Console ou via gcloud CLI, configure as seguintes variáveis de ambiente no Cloud Run:

**Obrigatórias:**
- `SECRET_KEY` - Chave secreta do Django (gere uma nova para produção)
- `MERCADOPAGO_ACCESS_TOKEN` - Token de acesso do Mercado Pago (PRODUÇÃO)
- `MERCADOPAGO_PUBLIC_KEY` - Chave pública do Mercado Pago (PRODUÇÃO)
- `DB_NAME` - Nome do banco de dados
- `DB_USER` - Usuário do banco de dados
- `DB_PASSWORD` - Senha do banco de dados
- `DB_HOST` - Host do Cloud SQL

**Opcionais:**
- `DEBUG=False` - Desabilitar debug em produção
- `SITE_URL=https://monpec.com.br` - URL do site
- `MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/`
- `MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/`

## Deploy

### Opção 1: Script Automatizado (Recomendado)

**Windows:**
```bash
DEPLOY_MONPEC.bat
```

**PowerShell:**
```powershell
.\DEPLOY_MONPEC.ps1
```

### Opção 2: Deploy Manual

#### 1. Build da imagem Docker

```bash
docker build -t gcr.io/SEU_PROJECT_ID/monpec:latest .
```

#### 2. Push para Container Registry

```bash
docker push gcr.io/SEU_PROJECT_ID/monpec:latest
```

#### 3. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/SEU_PROJECT_ID/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080
```

### Opção 3: Cloud Build (CI/CD)

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Configurar Domínio Personalizado

### 1. Via Console

1. Acesse: https://console.cloud.google.com/run
2. Selecione o serviço `monpec`
3. Vá em **"DOMAIN MAPPING"**
4. Clique em **"ADD MAPPING"**
5. Adicione:
   - `monpec.com.br`
   - `www.monpec.com.br`

### 2. Via CLI

```bash
# Mapear domínio principal
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

# Mapear www
gcloud run domain-mappings create \
    --service monpec \
    --domain www.monpec.com.br \
    --region us-central1
```

### 3. Configurar DNS

Após criar o mapeamento, o Google Cloud fornecerá registros DNS. Configure no seu provedor de domínio:

**Registros CNAME:**
- `monpec.com.br` → `ghs.googlehosted.com`
- `www.monpec.com.br` → `ghs.googlehosted.com`

Ou use os registros específicos fornecidos pelo Google Cloud.

## Configurar Variáveis de Ambiente

### Via Console

1. Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec
2. Clique em **"EDIT & DEPLOY NEW REVISION"**
3. Vá em **"VARIABLES & SECRETS"**
4. Adicione todas as variáveis necessárias

### Via CLI

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=APP_USR-...,MERCADOPAGO_PUBLIC_KEY=APP_USR-...,SECRET_KEY=..."
```

## Aplicar Migrações

Após o deploy, execute as migrações:

```bash
gcloud run jobs create migrate-monpec \
    --image gcr.io/SEU_PROJECT_ID/monpec:latest \
    --region us-central1 \
    --command python \
    --args "manage.py,migrate" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

gcloud run jobs execute migrate-monpec --region us-central1
```

## Verificar Deploy

1. Acesse: https://monpec.com.br
2. Verifique se a página carrega corretamente
3. Teste o login
4. Teste os botões de pagamento

## Troubleshooting

### Ver logs

```bash
gcloud run services logs read monpec --region us-central1
```

### Verificar variáveis de ambiente

```bash
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

### Reiniciar serviço

```bash
gcloud run services update monpec --region us-central1 --update-env-vars "RESTART=$(date +%s)"
```

## Próximos Passos

1. ✅ Configurar domínio personalizado
2. ✅ Configurar variáveis de ambiente
3. ✅ Aplicar migrações
4. ✅ Testar sistema em produção
5. ✅ Configurar backup automático do banco de dados
6. ✅ Configurar monitoramento e alertas































