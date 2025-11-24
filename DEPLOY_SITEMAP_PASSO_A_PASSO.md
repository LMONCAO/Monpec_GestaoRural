# 🚀 Deploy do Sitemap - Passo a Passo

## ✅ Commit e Push Concluídos!

Os arquivos foram commitados e enviados para o GitHub:
- ✅ `gestao_rural/sitemaps.py` - Criado
- ✅ `sistema_rural/urls.py` - Atualizado
- ✅ `sistema_rural/settings.py` - Atualizado

---

## 📋 Próximo: Deploy no Cloud Shell

### Opção 1: Comando Único (Copiar e Colar)

Copie o conteúdo do arquivo `DEPLOY_SITEMAP_CLOUD_SHELL.txt` e cole no Cloud Shell.

### Opção 2: Passo a Passo

Execute no Cloud Shell:

```bash
# 1. Atualizar código
cd ~/Monpec_GestaoRural
git pull origin master

# 2. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# 3. Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 4. Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# 5. Deploy
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

## ✅ Depois do Deploy

### 1. Testar Sitemap

Acesse no navegador:
```
https://monpec-29862706245.us-central1.run.app/sitemap.xml
```

Você deve ver um XML com as URLs do site.

### 2. Atualizar no Google Search Console

1. **Acesse:** https://search.google.com/search-console
2. **Vá em:** Sitemaps
3. **Remova o sitemap antigo** (se houver erro)
4. **Adicione:** `sitemap.xml`
5. **Clique em:** "ENVIAR"

---

## ⏱️ Tempo Estimado

- Build: ~10-15 minutos
- Deploy: ~2-3 minutos
- **Total: ~15-20 minutos**

---

**Próximo passo:** Execute os comandos no Cloud Shell!














