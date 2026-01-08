# 🚀 Deploy Rápido - Monpec Gestão Rural

## ⚡ Deploy em 3 Passos

### 1️⃣ Aplicar Migrations no Cloud SQL

```bash
# Opção A: Via Script (Recomendado)
chmod +x scripts/aplicar_migrations_cloud.sh
./scripts/aplicar_migrations_cloud.sh

# Opção B: Manual
gcloud run jobs create migrate-db \
  --image gcr.io/PROJECT_ID/monpec:latest \
  --region us-central1 \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --command python \
  --args manage.py,migrate \
  --memory 512Mi \
  --timeout 600

gcloud run jobs execute migrate-db --region us-central1 --wait
```

### 2️⃣ Fazer Deploy

```bash
# Opção A: Via Script (Recomendado)
chmod +x scripts/deploy_cloud_run.sh
./scripts/deploy_cloud_run.sh

# Opção B: Via Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Opção C: Manual
gcloud builds submit --tag gcr.io/PROJECT_ID/monpec:latest
gcloud run deploy monpec \
  --image gcr.io/PROJECT_ID/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --port 8080
```

### 3️⃣ Verificar

```bash
# Verificar status
gcloud run services describe monpec --region us-central1

# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Testar site
curl https://monpec.com.br
```

---

## 📋 Variáveis de Ambiente Necessárias

Configure no Cloud Run Console ou via gcloud:

```bash
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
DEBUG=False
SECRET_KEY=<sua-secret-key>
CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=<senha>
```

---

## ⚠️ Importante

1. **Aplicar migrations ANTES do deploy** - Use o script `aplicar_migrations_cloud.sh`
2. **Configurar variáveis de ambiente** - Todas as variáveis devem estar configuradas
3. **Verificar logs após deploy** - Sempre verifique os logs para erros

---

## 🆘 Problemas Comuns

### "Service Unavailable"
- Verificar se migrations foram aplicadas
- Verificar variáveis de ambiente
- Verificar logs

### "Database connection failed"
- Verificar CLOUD_SQL_CONNECTION_NAME
- Verificar credenciais
- Verificar se Cloud SQL Proxy está configurado

---

**Última atualização**: Janeiro 2026


