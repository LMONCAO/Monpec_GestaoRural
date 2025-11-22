# 🔍 Verificar Deploy Após Erro

O build foi bem-sucedido, mas houve um erro no deploy. Vamos verificar se o serviço está funcionando.

---

## ✅ Build: SUCESSO

```
STATUS: SUCCESS
DURATION: 3M7S
IMAGES: gcr.io/monpec-sistema-rural/monpec
```

**Isso significa que a imagem Docker foi criada com sucesso!**

---

## ⚠️ Erro no Deploy

O erro foi: `unrecognized arguments` nos parâmetros do `--set-env-vars`.

**Mas apareceu uma URL:** `https://monpec-fzzfjppzva-uc.a.run.app`

---

## 🔍 Verificar se o Serviço Está Funcionando

### **1. Testar a URL no Navegador**

Acesse: `https://monpec-fzzfjppzva-uc.a.run.app`

- ✅ Se o site carregar: O deploy funcionou!
- ❌ Se der erro: Precisamos corrigir o deploy

---

### **2. Verificar Status no Cloud Shell**

Execute no Cloud Shell:

```bash
# Verificar status do serviço
gcloud run services describe monpec --region us-central1

# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 20
```

---

## 🔧 Se o Serviço Não Estiver Funcionando

### **Corrigir o Deploy com Comando Simples**

O problema foi com a formatação dos argumentos. Use este comando corrigido:

```bash
# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null || echo "")

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy corrigido (sem vírgulas problemáticas)
if [ -n "$CONNECTION_NAME" ]; then
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --add-cloudsql-instances $CONNECTION_NAME \
        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD='Monpec2025!',CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY="$SECRET_KEY" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
else
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY="$SECRET_KEY" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
fi
```

---

## ✅ Próximos Passos

1. **Testar a URL:** `https://monpec-fzzfjppzva-uc.a.run.app`
2. **Se funcionar:** Verificar meta tag e arquivo HTML
3. **Se não funcionar:** Executar o comando corrigido acima

---

**Primeiro, teste a URL no navegador para ver se está funcionando!**

