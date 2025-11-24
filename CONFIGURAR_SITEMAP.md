# 📋 Sitemap Configurado

## ✅ O que foi feito

1. ✅ Criado arquivo `gestao_rural/sitemaps.py` com configuração de sitemap
2. ✅ Adicionada rota `/sitemap.xml` no `urls.py`
3. ✅ Configurado sitemap para páginas estáticas

---

## 🚀 Próximos Passos

### 1. Fazer Deploy

```bash
# No seu computador local
git add gestao_rural/sitemaps.py sistema_rural/urls.py
git commit -m "Adicionar sitemap.xml"
git push origin master

# No Cloud Shell
cd ~/Monpec_GestaoRural
git pull origin master
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10
```

### 2. Testar Sitemap

Após o deploy, acesse:
```
https://monpec-29862706245.us-central1.run.app/sitemap.xml
```

Você deve ver um XML com as URLs do site.

### 3. Atualizar no Google Search Console

1. **Acesse:** https://search.google.com/search-console
2. **Vá em:** Sitemaps
3. **Remova o sitemap antigo** (se houver erro)
4. **Adicione:** `sitemap.xml`
5. **Clique em:** "ENVIAR"

---

## 📝 Personalizar Sitemap

Para adicionar mais páginas ao sitemap, edite `gestao_rural/sitemaps.py`:

```python
def items(self):
    return [
        'landing_page',
        'outra_pagina',  # Adicione aqui
    ]
```

---

**Após o deploy, o sitemap estará disponível em `/sitemap.xml`!** ✅














