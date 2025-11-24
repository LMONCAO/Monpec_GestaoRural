# 🚀 Deploy com Correção do ALLOWED_HOSTS

## ✅ Correção Aplicada

Corrigi o `settings_gcp.py` para permitir hosts do Cloud Run. Agora você precisa fazer push para o GitHub e fazer um novo deploy.

---

## 📋 Passo a Passo

### 1. Fazer Push para o GitHub (Local)

No seu computador local, execute:

```powershell
# Navegar para a pasta do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Adicionar alterações
git add sistema_rural/settings_gcp.py

# Commit
git commit -m "Corrigir ALLOWED_HOSTS para Cloud Run"

# Push
git push origin master
```

**OU** use o script PowerShell:

```powershell
.\fazer_push_github_com_token.ps1
```

---

### 2. Atualizar no Cloud Shell

No Cloud Shell, execute:

```bash
cd ~/Monpec_GestaoRural
git pull origin master || git pull origin main
```

---

### 3. Fazer Novo Build e Deploy

```bash
cd ~/Monpec_GestaoRural

# Build da imagem
echo "🔨 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy
echo "🚀 Fazendo deploy..."
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

- Push para GitHub: **1 minuto**
- Build: **10-15 minutos**
- Deploy: **2-3 minutos**

**Total: ~15-20 minutos**

---

## ✅ Depois do Deploy

1. Verifique se o site está funcionando:
   ```bash
   gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
   ```

2. Acesse a URL no navegador

3. Verifique a meta tag:
   ```bash
   curl -s https://[URL_DO_SERVICO] | grep -i "google-site-verification"
   ```

---

## 🔒 Nota de Segurança

A correção atual permite todos os hosts (`ALLOWED_HOSTS = ['*']`) apenas para Cloud Run. Isso é temporário para resolver o erro.

**Para produção, considere:**
- Adicionar o host específico via variável de ambiente `CLOUD_RUN_HOST`
- Ou usar uma verificação mais restritiva que permite apenas hosts `.a.run.app`

---

**Última atualização:** Novembro 2025














