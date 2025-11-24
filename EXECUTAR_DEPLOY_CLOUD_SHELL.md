# 🚀 Executar Deploy Corrigido no Cloud Shell

## ⚠️ Situação Atual

O site está mostrando "Service Unavailable". Isso significa que:
- O deploy ainda não foi feito com as correções
- Ou há outro problema que precisa ser verificado

---

## ✅ Solução: Executar Script Completo

### **Opção 1: Usar Script Automatizado (Recomendado)**

1. **No Cloud Shell, execute:**

```bash
cd ~/Monpec_GestaoRural

# Baixar o script atualizado (se ainda não tiver)
# Ou criar o arquivo deploy_completo_corrigido.sh

# Dar permissão de execução
chmod +x deploy_completo_corrigido.sh

# Executar
./deploy_completo_corrigido.sh
```

---

### **Opção 2: Comandos Manuais (Passo a Passo)**

Se preferir executar manualmente:

#### 1. Atualizar código:
```bash
cd ~/Monpec_GestaoRural
git pull origin master
```

#### 2. Build:
```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

#### 3. Deploy:
```bash
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

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

## ⏱️ Tempo Estimado

- Atualizar código: **1 minuto**
- Build: **10-15 minutos**
- Deploy: **2-3 minutos**

**Total: ~15-20 minutos**

---

## 🔍 Se Ainda Houver Erro

Após o deploy, se o site ainda não funcionar:

### 1. Verificar Logs:
```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### 2. Verificar Status do Serviço:
```bash
gcloud run services describe monpec --region us-central1
```

### 3. Verificar Variáveis de Ambiente:
```bash
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

---

## ✅ Depois do Deploy Bem-Sucedido

1. **Testar o site:**
   - Acesse a URL retornada pelo deploy
   - Deve carregar normalmente (não mais "Service Unavailable")

2. **Verificar meta tag:**
   ```bash
   curl -s https://[URL_DO_SERVICO] | grep -i "google-site-verification"
   ```

3. **Testar arquivo HTML:**
   ```bash
   curl -s https://[URL_DO_SERVICO]/google40933139f3b0d469.html
   ```

4. **Verificar no Google Search Console:**
   - Adicionar propriedade com a URL do Cloud Run
   - Verificar usando meta tag ou arquivo HTML

---

**Última atualização:** Novembro 2025













