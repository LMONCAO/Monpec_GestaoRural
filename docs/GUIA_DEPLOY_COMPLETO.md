# 🚀 Guia Completo de Deploy - Google Cloud Run

## Data: Janeiro 2026

---

## 📋 Pré-requisitos

### 1. Ferramentas Necessárias
- Google Cloud SDK instalado e configurado
- Acesso ao projeto Google Cloud
- Permissões: Cloud Run Admin, Cloud SQL Admin, Storage Admin

### 2. Variáveis de Ambiente Necessárias
Configure no Cloud Run ou via Secret Manager:

```bash
# Django
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
DEBUG=False
SECRET_KEY=<sua-secret-key>

# Banco de Dados
CLOUD_SQL_CONNECTION_NAME=<PROJECT_ID>:<REGION>:<INSTANCE_NAME>
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=<senha-do-banco>

# URLs
SITE_URL=https://monpec.com.br
STRIPE_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/
STRIPE_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/

# Mercado Pago (se usar)
MERCADOPAGO_ACCESS_TOKEN=<token>
MERCADOPAGO_PUBLIC_KEY=<public-key>
```

---

## 🔧 Passo 1: Aplicar Migrations no Cloud SQL

### Opção A: Via Cloud Run Job (Recomendado)

```bash
# Criar job para migrations
gcloud run jobs create migrate-db \
  --image gcr.io/PROJECT_ID/monpec:latest \
  --region us-central1 \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=senha \
  --set-env-vars SECRET_KEY=temp-key \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --command python \
  --args manage.py,migrate \
  --memory 512Mi \
  --timeout 600

# Executar job
gcloud run jobs execute migrate-db --region us-central1
```

### Opção B: Via Cloud SQL Proxy (Local)

```bash
# Instalar Cloud SQL Proxy
# https://cloud.google.com/sql/docs/postgres/connect-admin-proxy

# Conectar ao banco
./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432

# Em outro terminal, aplicar migrations
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
export CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=senha
python manage.py migrate
```

---

## 🏗️ Passo 2: Build e Deploy

### Opção A: Deploy Automático (Cloud Build)

```bash
# Fazer commit das mudanças
git add .
git commit -m "Preparar para deploy"
git push

# Trigger Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### Opção B: Deploy Manual

```bash
# 1. Build da imagem
docker build -t gcr.io/PROJECT_ID/monpec:latest .

# 2. Push para Container Registry
docker push gcr.io/PROJECT_ID/monpec:latest

# 3. Deploy no Cloud Run
gcloud run deploy monpec \
  --image gcr.io/PROJECT_ID/monpec:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=senha \
  --set-env-vars SECRET_KEY=secret-key \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --port 8080
```

---

## ✅ Passo 3: Verificar Deploy

### 1. Verificar Status do Serviço
```bash
gcloud run services describe monpec --region us-central1
```

### 2. Verificar Logs
```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### 3. Testar Site
```bash
# Obter URL do serviço
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Testar
curl https://monpec.com.br
```

---

## 🔍 Troubleshooting

### Erro: "Service Unavailable"
- Verificar se migrations foram aplicadas
- Verificar variáveis de ambiente
- Verificar logs do Cloud Run

### Erro: "Database connection failed"
- Verificar CLOUD_SQL_CONNECTION_NAME
- Verificar credenciais do banco
- Verificar se Cloud SQL Proxy está configurado

### Erro: "Static files not found"
- Verificar se collectstatic foi executado
- Verificar configuração do WhiteNoise
- Verificar STATIC_ROOT

---

## 📝 Checklist Final

- [ ] Migrations aplicadas no Cloud SQL
- [ ] Variáveis de ambiente configuradas
- [ ] Build da imagem Docker
- [ ] Deploy no Cloud Run
- [ ] Site acessível
- [ ] Logs sem erros críticos
- [ ] Funcionalidades principais testadas

---

**Última atualização**: Janeiro 2026
**Versão**: 1.0


