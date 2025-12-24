# 🚀 Guia Rápido de Deploy - MONPEC

## Deploy Automático (Recomendado)

### Windows:
Execute o arquivo:
```
DEPLOY_AGORA.bat
```

### Linux/Mac:
```bash
./deploy.sh monpec-sistema-rural us-central1
```

## Deploy Manual

### 1. Build da Imagem Docker

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec --timeout=30m
```

### 2. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
```

## ⚙️ Configurações Pós-Deploy

### 1. Configurar Variáveis de Ambiente

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "SECRET_KEY=sua-chave-secreta-forte,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=sua-senha-forte"
```

### 2. Conectar ao Cloud SQL (se usar banco de dados)

```bash
gcloud run services update monpec \
    --region us-central1 \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db
```

### 3. Executar Migrações

```bash
# Criar job de migração
gcloud run jobs create monpec-migrate \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
    --command python \
    --args manage.py,migrate

# Executar migração
gcloud run jobs execute monpec-migrate --region us-central1 --wait
```

### 4. Criar Usuário Admin

```powershell
.\criar_admin_cloud_run.ps1 monpec-sistema-rural us-central1
```

### 5. Configurar Domínio Personalizado

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

gcloud run domain-mappings create \
    --service monpec \
    --domain www.monpec.com.br \
    --region us-central1
```

Depois, configure os registros DNS conforme mostrado pelo comando acima.

## 📋 Verificar Status

```bash
# Ver URL do serviço
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

# Ver logs
gcloud run services logs read monpec --region us-central1 --follow
```

## 🔧 Troubleshooting

### Erro: Dockerfile não encontrado
- Certifique-se de estar no diretório raiz do projeto
- Verifique se o Dockerfile existe: `dir Dockerfile`

### Erro: Permissão negada
- Verifique se está autenticado: `gcloud auth list`
- Verifique se tem permissões no projeto: `gcloud projects get-iam-policy monpec-sistema-rural`

### Erro: API não habilitada
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```



















