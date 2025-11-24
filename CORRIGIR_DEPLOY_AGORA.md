# 🔧 Corrigir Deploy - Erro de Variáveis de Ambiente

## ❌ Problema Identificado

O erro ocorreu porque as variáveis de ambiente foram passadas com quebras de linha no comando `gcloud run deploy`. A sintaxe correta requer uma única string separada por vírgulas.

**Erro:**
```
ERROR: (gcloud.run.deploy) unrecognized arguments:
DEBUG=False,
DB_NAME=monpec_db,
...
```

## ✅ Solução

O script `deploy_completo_cloud_shell.sh` foi corrigido! Agora você pode executar novamente.

---

## 🚀 Executar Deploy Corrigido no Cloud Shell

### **Opção 1: Atualizar Script e Executar**

1. No Cloud Shell, atualize o script:
```bash
cd ~/Monpec_GestaoRural
git pull origin master || git pull origin main
```

2. Execute o deploy:
```bash
chmod +x deploy_completo_cloud_shell.sh
./deploy_completo_cloud_shell.sh
```

---

### **Opção 2: Comando Manual (Rápido)**

Se preferir executar manualmente, use este comando corrigido:

```bash
cd ~/Monpec_GestaoRural

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy com sintaxe correta
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

## 📋 O que mudou?

**Antes (errado):**
```bash
--set-env-vars \
    DEBUG=False,\
    DB_NAME=monpec_db,\
    ...
```

**Depois (correto):**
```bash
--set-env-vars "DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,..."
```

Todas as variáveis agora estão em **uma única string** dentro de aspas, separadas por vírgulas.

---

## ⏱️ Tempo Estimado

- Deploy: **2-3 minutos**

---

## ✅ Depois do Deploy

1. Verifique a URL do serviço:
```bash
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

2. Teste a meta tag:
   - Acesse a URL do serviço
   - Pressione **Ctrl+U** para ver o código-fonte
   - Procure por: `google-site-verification`

3. Teste o arquivo HTML:
   - Acesse: `https://[URL_DO_SERVICO]/google40933139f3b0d469.html`
   - Deve aparecer: `google-site-verification: google40933139f3b0d469.html`

---

**Última atualização:** Novembro 2025













