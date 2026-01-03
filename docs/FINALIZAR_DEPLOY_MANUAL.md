


# 🚀 FINALIZAR DEPLOY MANUAL

## ✅ Status Atual

**Reset concluído com sucesso!**

- ✅ Serviço Cloud Run excluído
- ✅ Todos os Jobs Cloud Run excluídos (15 jobs)
- ✅ Instância Cloud SQL antiga excluída
- ✅ Imagens Docker excluídas
- ✅ Nova instância Cloud SQL criada
- ✅ Banco de dados criado (monpec_db)
- ✅ Usuário criado (monpec_user)

**Connection Name:** `monpec-sistema-rural:us-central1:monpec-db`

---

## 📋 Próximos Passos para Finalizar o Deploy

### **1. Build da Imagem Docker**

Execute no PowerShell, **no diretório do projeto**:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec --timeout=600s
```

⏱️ **Tempo estimado:** 5-10 minutos

---

### **2. Deploy no Cloud Run**

Após o build concluir, execute:

```powershell
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$CONNECTION_NAME = "monpec-sistema-rural:us-central1:monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "Monpec2025!SenhaSegura"
$SECRET_KEY = "django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

$ENV_VARS = "DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,PORT=8080"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 2 `
    --timeout 600 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080
```

---

### **3. Aplicar Migrações**

```powershell
$JOB_NAME = "migrate-monpec"

gcloud run jobs create $JOB_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --set-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 1 `
    --max-retries 3 `
    --task-timeout 600 `
    --command python `
    --args "manage.py,migrate,--noinput"

gcloud run jobs execute $JOB_NAME --region $REGION --wait
```

---

### **4. Coletar Arquivos Estáticos**

```powershell
$STATIC_JOB_NAME = "collectstatic-monpec"

gcloud run jobs create $STATIC_JOB_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --set-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 1 `
    --max-retries 3 `
    --task-timeout 600 `
    --command python `
    --args "manage.py,collectstatic,--noinput"

gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
```

---

### **5. Configurar Domínio (Opcional)**

```powershell
gcloud run domain-mappings create --service $SERVICE_NAME --domain monpec.com.br --region $REGION
gcloud run domain-mappings create --service $SERVICE_NAME --domain www.monpec.com.br --region $REGION
```

---

## 🎯 Script Completo (Alternativa)

Se preferir, você pode executar o script completo:

```powershell
.\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1
```

---

## ✅ Verificação Final

Após o deploy, verifique:

1. **Status do serviço:**
   ```powershell
   gcloud run services describe monpec --region us-central1
   ```

2. **URL do serviço:**
   ```powershell
   gcloud run services describe monpec --region us-central1 --format="value(status.url)"
   ```

3. **Acessar o sistema:**
   - Use a URL retornada acima
   - Ou configure o domínio se aplicou o passo 5

---

**Última atualização:** 26/12/2025






