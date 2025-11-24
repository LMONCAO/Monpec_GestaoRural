# 🔐 Verificar Domínio monpec.com.br no Google Cloud

## ⚠️ Erro Atual

```
ERROR: The provided domain does not appear to be verified for the current account
```

O domínio precisa ser **verificado** antes de poder ser mapeado.

---

## 📋 Passo a Passo para Verificar

### Opção 1: Via Console Web (Recomendado)

1. **Acesse:** https://console.cloud.google.com/run/domains
2. **Clique em:** "Verify a new domain"
3. **Digite:** `monpec.com.br`
4. **Escolha o método de verificação:**
   - **Método 1: Meta tag HTML** (mais fácil)
     - Adicione a meta tag no `<head>` do seu site
     - Ou crie um arquivo HTML específico
   - **Método 2: DNS TXT record** (se tiver acesso ao DNS)
     - Adicione um registro TXT no DNS

5. **Siga as instruções** que aparecerem na tela

---

### Opção 2: Via Cloud Shell

```bash
# Verificar domínio via meta tag
gcloud domains verify monpec.com.br --web-resource
```

Isso vai retornar uma meta tag que você precisa adicionar ao seu site.

---

## 🚀 Solução Rápida: Adicionar Meta Tag

### 1. Obter Meta Tag

Execute no Cloud Shell:

```bash
gcloud domains verify monpec.com.br --web-resource
```

Isso vai retornar algo como:
```html
<meta name="google-site-verification" content="CODIGO_AQUI" />
```

### 2. Adicionar ao Site

Você precisa adicionar essa meta tag no template base do Django.

**Arquivo:** `templates/base.html` ou `templates/base_identidade_visual.html`

Adicione no `<head>`:

```html
<meta name="google-site-verification" content="CODIGO_AQUI" />
```

### 3. Fazer Deploy Novamente

Depois de adicionar a meta tag, faça push e deploy:

```bash
# No seu computador local
git add templates/base.html
git commit -m "Adicionar meta tag verificação Google"
git push origin master

# No Cloud Shell
cd ~/Monpec_GestaoRural
git pull origin master
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated
```

### 4. Verificar Domínio

Após o deploy, execute:

```bash
gcloud domains verify monpec.com.br --web-resource
```

---

## 🔍 Verificar Status

```bash
# Listar domínios verificados
gcloud domains list-user-verified

# Verificar status específico
gcloud domains verify monpec.com.br --web-resource
```

---

## 📝 Alternativa: Usar DNS TXT Record

Se você tem acesso ao DNS do domínio:

1. Execute: `gcloud domains verify monpec.com.br --dns-resource`
2. Isso retornará um registro TXT
3. Adicione esse registro TXT no DNS do seu provedor
4. Aguarde propagação (pode levar algumas horas)
5. Execute: `gcloud domains verify monpec.com.br --dns-resource` novamente

---

## ✅ Depois de Verificar

Após verificar o domínio, você pode mapear:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
```

---

**Próximo passo:** Execute `gcloud domains verify monpec.com.br --web-resource` para obter a meta tag!














