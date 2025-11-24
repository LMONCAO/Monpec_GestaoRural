# 🚀 Deploy Rápido - Comando Corrigido para Cloud Shell

## ⚠️ Problema
O script ainda está usando a sintaxe antiga. Use este comando **direto no Cloud Shell**:

---

## ✅ Comando Completo (Copiar e Colar)

```bash
cd ~/Monpec_GestaoRural && \
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)") && \
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && \
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## 📋 Passo a Passo (Se Preferir)

1. **Navegar para a pasta:**
```bash
cd ~/Monpec_GestaoRural
```

2. **Obter connection name:**
```bash
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
```

3. **Gerar SECRET_KEY:**
```bash
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

4. **Executar deploy (sintaxe correta):**
```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## 🔑 Diferença Importante

**❌ ERRADO (com quebras de linha):**
```bash
--set-env-vars \
    DEBUG=False,\
    DB_NAME=monpec_db,\
    ...
```

**✅ CORRETO (uma única string):**
```bash
--set-env-vars "DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,..."
```

---

## ⏱️ Tempo Estimado
- Deploy: **2-3 minutos**

---

## ✅ Depois do Deploy

1. **Obter URL do serviço:**
```bash
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

2. **Verificar meta tag:**
   - Acesse a URL no navegador
   - Pressione **Ctrl+U** para ver código-fonte
   - Procure por: `google-site-verification`

3. **Testar arquivo HTML:**
   - Acesse: `https://[URL]/google40933139f3b0d469.html`
   - Deve aparecer: `google-site-verification: google40933139f3b0d469.html`

---

**Última atualização:** Novembro 2025













