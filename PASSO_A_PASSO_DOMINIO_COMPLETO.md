# 🌐 Configurar monpec.com.br - Passo a Passo Completo

## 📋 Resumo

1. Verificar domínio no Google Cloud (via Console Web)
2. Adicionar meta tag ao template
3. Fazer deploy
4. Mapear domínio no Cloud Run
5. Configurar DNS no provedor

---

## ✅ PASSO 1: Verificar Domínio (Console Web)

### 1.1 Acessar Console

**URL:** https://console.cloud.google.com/run/domains

### 1.2 Iniciar Verificação

1. Clique em **"Verify a new domain"**
2. Digite: `monpec.com.br`
3. Clique em **"Continue"**

### 1.3 Escolher Método

**Escolha:** "HTML tag" (meta tag)

### 1.4 Copiar Meta Tag

Você verá algo como:

```html
<meta name="google-site-verification" content="ABC123XYZ..." />
```

**Copie o código** (a parte dentro de `content="..."`)

---

## ✅ PASSO 2: Adicionar Meta Tag ao Template

### 2.1 Editar Template

**Arquivo:** `templates/base.html`

**Localização:** Dentro do `<head>`, após a linha 11 (depois da meta tag do Google Search Console)

### 2.2 Adicionar Código

```html
<!-- Google Cloud Domain Verification -->
<meta name="google-site-verification" content="CODIGO_COPIADO_AQUI" />
```

**Substitua** `CODIGO_COPIADO_AQUI` pelo código que você copiou.

---

## ✅ PASSO 3: Fazer Deploy

### 3.1 Commit e Push (Local)

```bash
git add templates/base.html
git commit -m "Adicionar meta tag verificação domínio Cloud Run"
git push origin master
```

### 3.2 Deploy (Cloud Shell)

```bash
cd ~/Monpec_GestaoRural
git pull origin master
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10
```

---

## ✅ PASSO 4: Verificar Domínio (Console Web)

### 4.1 Aguardar Deploy

Aguarde **2-3 minutos** após o deploy completar.

### 4.2 Verificar

1. Volte para: https://console.cloud.google.com/run/domains
2. Você deve ver `monpec.com.br` na lista
3. Clique em **"Verify"** ou **"Verificar"**
4. Se a meta tag estiver correta, você verá ✅ **"Verified"**

---

## ✅ PASSO 5: Mapear Domínio (Cloud Shell)

Depois de verificado, execute:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

---

## ✅ PASSO 6: Ver Instruções de DNS

Execute:

```bash
gcloud beta run domain-mappings describe monpec.com.br --region us-central1
```

Isso vai mostrar as instruções de DNS que você precisa configurar no seu provedor.

---

## ✅ PASSO 7: Configurar DNS

Configure os registros DNS no seu provedor (Registro.br, GoDaddy, etc.) conforme as instruções do passo 6.

---

## ✅ PASSO 8: Aguardar Propagação

- ⏳ Pode levar de **15 minutos a 48 horas**
- 🔍 Verifique com: `dig monpec.com.br` ou `nslookup monpec.com.br`

---

## ✅ PASSO 9: Testar

Após a propagação DNS, acesse:

- https://monpec.com.br
- https://www.monpec.com.br

---

## 🆘 Problemas Comuns

### Meta tag não funciona

- Verifique se está dentro do `<head>`
- Verifique se o código está correto (sem espaços extras)
- Aguarde alguns minutos após o deploy

### Domínio não verifica

- Certifique-se de que o deploy foi concluído
- Verifique se a meta tag está acessível no site
- Tente novamente após alguns minutos

### DNS não propaga

- Verifique se os registros estão corretos
- Aguarde até 48 horas
- Verifique com `dig` ou `nslookup`

---

**Tempo total estimado:** 30 minutos a 2 dias (dependendo da propagação DNS)













