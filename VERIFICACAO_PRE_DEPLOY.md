# ✅ VERIFICAÇÃO PRÉ-DEPLOY - Checklist Completo

## 🔍 Verificações Realizadas

### ✅ **1. Configurações Django**
- [x] `STATIC_ROOT` adicionado em `settings.py`
- [x] `MEDIA_ROOT` e `MEDIA_URL` configurados
- [x] `settings_gcp.py` configurado corretamente
- [x] WhiteNoise configurado para servir arquivos estáticos
- [x] Middleware customizado para Cloud Run hosts

### ✅ **2. Dockerfile**
- [x] Python 3.11 configurado
- [x] Dependências do sistema instaladas (PostgreSQL client)
- [x] `collectstatic` configurado com settings correto
- [x] Gunicorn configurado
- [x] Usuário não-root criado (segurança)

### ✅ **3. Banco de Dados**
- [x] Configuração Cloud SQL via Unix Socket
- [x] Variáveis de ambiente para conexão
- [x] Fallback para conexão via IP

### ✅ **4. Segurança**
- [x] `DEBUG=False` em produção
- [x] `SECRET_KEY` via variável de ambiente
- [x] `ALLOWED_HOSTS` configurado
- [x] `CSRF_TRUSTED_ORIGINS` configurado
- [x] SSL/HTTPS forçado
- [x] Headers de segurança configurados

### ✅ **5. Arquivos Estáticos**
- [x] WhiteNoise configurado
- [x] `collectstatic` no Dockerfile
- [x] Fallback para Cloud Storage (opcional)

### ✅ **6. Dependências**
- [x] `requirements_producao.txt` completo
- [x] Gunicorn incluído
- [x] WhiteNoise incluído
- [x] psycopg2-binary para PostgreSQL

---

## ⚠️ **Ajustes Necessários no Deploy**

### **1. Variável CLOUD_RUN_HOST**
Ao fazer o deploy, você precisará adicionar a URL completa do Cloud Run:

```bash
# Após o deploy, obter a URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
# Exemplo: https://monpec-xxxxx-uc.a.run.app

# Extrair apenas o host (sem https://)
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')

# Atualizar variável de ambiente
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST
```

### **2. SECRET_KEY**
Certifique-se de gerar uma SECRET_KEY segura:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### **3. Migrações**
Execute as migrações após o deploy:

```bash
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances CONNECTION_NAME \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,... \
    --command python \
    --args manage.py,migrate
```

---

## 🧪 **Testes Locais (Antes do Deploy)**

### **1. Testar Dockerfile Localmente**

```bash
# Build local
docker build -t monpec-test .

# Rodar localmente
docker run -p 8080:8080 \
    -e DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
    -e DEBUG=False \
    -e SECRET_KEY=test-key \
    monpec-test
```

### **2. Verificar Collectstatic**

```bash
# Testar collectstatic
python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp
```

### **3. Verificar Imports**

```bash
# Verificar se todos os imports funcionam
python manage.py check --settings=sistema_rural.settings_gcp
```

---

## 📋 **Checklist Final Antes do Deploy**

- [ ] Todas as dependências em `requirements_producao.txt`
- [ ] `SECRET_KEY` gerada e segura
- [ ] Banco de dados Cloud SQL criado
- [ ] Connection name do Cloud SQL anotado
- [ ] `CLOUD_RUN_HOST` será configurado após primeiro deploy
- [ ] Migrações testadas localmente
- [ ] Arquivos estáticos coletados corretamente
- [ ] `.dockerignore` configurado (já criado)

---

## 🚀 **Pronto para Deploy!**

Todos os ajustes foram feitos. Você pode seguir o passo a passo em:
- `GUIA_DEPLOY_GOOGLE_CLOUD_PASSO_A_PASSO.md`
- `INICIO_RAPIDO_GOOGLE_CLOUD.md`






