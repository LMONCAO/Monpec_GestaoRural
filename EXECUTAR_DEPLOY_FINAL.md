# 🚀 EXECUTAR DEPLOY - Instruções Finais

## ✅ Status Atual

- ✅ **gcloud CLI**: Instalado e autenticado
- ✅ **Projeto**: monpec-sistema-rural (configurado)
- ✅ **APIs**: Habilitadas (Cloud Build, Cloud Run, SQL Admin)
- ✅ **Cloud SQL**: monpec-db configurado
- ✅ **Configurações**: Todas prontas

## 🚀 Executar Deploy (Escolha uma opção)

### Opção 1: Cloud Shell (RECOMENDADO - Mais fácil)

1. **Acesse o Cloud Shell:**
   - Vá para: https://console.cloud.google.com/cloudshell
   - Ou no console: Menu ☰ → Cloud Shell

2. **Faça upload dos arquivos:**
   ```bash
   # No Cloud Shell, faça upload do projeto
   # Use o botão de upload ou git clone
   ```

3. **Execute o deploy:**
   ```bash
   # Configurar projeto
   gcloud config set project monpec-sistema-rural
   
   # Build da imagem
   gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
   
   # Deploy no Cloud Run
   gcloud run deploy monpec \
       --image gcr.io/monpec-sistema-rural/monpec:latest \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated \
       --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
       --memory=1Gi \
       --cpu=2 \
       --timeout=300 \
       --max-instances=10 \
       --min-instances=1 \
       --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
   ```

### Opção 2: PowerShell Local (Se o build funcionar)

Execute no PowerShell:

```powershell
# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# Deploy
$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"

gcloud run deploy monpec `
    --image gcr.io/monpec-sistema-rural/monpec:latest `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars $envVars `
    --memory=1Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1 `
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```

## 📋 Após o Deploy

### 1. Aplicar Migrações

```bash
# Criar job de migração
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600

# Executar job
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

### 2. Obter URL do Serviço

```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

### 3. Configurar Domínio (Opcional)

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### 4. Verificar Logs

```bash
gcloud run services logs read monpec --region us-central1 --limit=50
```

## 🔍 Informações Importantes

- **Projeto**: monpec-sistema-rural
- **Serviço**: monpec
- **Região**: us-central1
- **Cloud SQL**: monpec-sistema-rural:us-central1:monpec-db
- **SECRET_KEY**: Já gerada e configurada
- **Banco de dados**: monpec_db (já existe)

## ⚠️ Se o Build Falhar

O build pode falhar no Windows devido a arquivos temporários. **Use o Cloud Shell** (Opção 1) que é mais confiável.

## ✅ Tudo Pronto!

Todos os arquivos e configurações estão prontos. Basta executar o deploy usando uma das opções acima!

---

**Última atualização**: 26/12/2025









