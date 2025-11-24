# 🔐 Obter Meta Tag de Verificação do Domínio

## 📋 Passo a Passo

### 1. Obter Meta Tag no Cloud Shell

Execute este comando:

```bash
gcloud domains verify monpec.com.br --web-resource
```

Isso vai retornar algo como:

```html
<meta name="google-site-verification" content="CODIGO_VERIFICACAO_AQUI" />
```

**Copie o código de verificação!**

---

### 2. Adicionar ao Template

Você precisa adicionar essa meta tag no template base. Já existe uma meta tag do Google Search Console, mas você precisa adicionar uma **nova** para verificação do Cloud Run.

**Arquivo:** `templates/base.html`

**Localização:** Dentro do `<head>`, após a meta tag existente (linha 11)

**Adicione:**

```html
<!-- Google Cloud Domain Verification -->
<meta name="google-site-verification" content="CODIGO_VERIFICACAO_AQUI" />
```

---

### 3. Fazer Deploy Novamente

Depois de adicionar a meta tag:

```bash
# No seu computador local
git add templates/base.html
git commit -m "Adicionar meta tag verificação domínio Cloud Run"
git push origin master

# No Cloud Shell
cd ~/Monpec_GestaoRural
git pull origin master
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10
```

---

### 4. Verificar Domínio

Após o deploy (aguarde alguns minutos para o site atualizar), execute:

```bash
gcloud domains verify monpec.com.br --web-resource
```

Se estiver correto, você verá uma mensagem de sucesso.

---

### 5. Verificar Status

```bash
# Listar domínios verificados
gcloud domains list-user-verified
```

Você deve ver `monpec.com.br` na lista.

---

### 6. Mapear Domínio

Depois de verificado, mapeie o domínio:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

---

## 🚀 Comando Rápido para Obter Meta Tag

Execute no Cloud Shell:

```bash
echo "Execute este comando para obter a meta tag:" && echo "" && echo "gcloud domains verify monpec.com.br --web-resource" && echo "" && echo "Depois copie o código e adicione ao template base.html"
```

---

**Próximo passo:** Execute `gcloud domains verify monpec.com.br --web-resource` no Cloud Shell!














