# 🌐 Verificar Domínio monpec.com.br - Via Console Web

## ⚠️ Problema

O comando `gcloud domains verify` não tem a flag `--web-resource`. A forma mais fácil é usar o **Console Web**.

---

## ✅ Solução: Verificar via Console Web

### Passo 1: Acessar a Página de Domínios

1. **Acesse:** https://console.cloud.google.com/run/domains
2. Ou navegue: **Cloud Run** → **Domains** (no menu lateral)

### Passo 2: Verificar Novo Domínio

1. **Clique em:** "Verify a new domain" ou "Verificar novo domínio"
2. **Digite:** `monpec.com.br`
3. **Clique em:** "Continue" ou "Continuar"

### Passo 3: Escolher Método de Verificação

Você terá 2 opções:

#### Opção A: Meta Tag HTML (Recomendado - Mais Fácil)

1. **Selecione:** "HTML tag" ou "Meta tag"
2. **Copie a meta tag** que aparecer, algo como:
   ```html
   <meta name="google-site-verification" content="CODIGO_AQUI" />
   ```
3. **Adicione ao template** `templates/base.html` (dentro do `<head>`)
4. **Faça deploy** novamente
5. **Volte ao console** e clique em "Verify" ou "Verificar"

#### Opção B: DNS TXT Record

1. **Selecione:** "DNS record" ou "Registro DNS"
2. **Copie o registro TXT** que aparecer
3. **Adicione no DNS** do seu provedor (Registro.br, etc.)
4. **Aguarde propagação** (pode levar algumas horas)
5. **Volte ao console** e clique em "Verify" ou "Verificar"

---

## 📋 Passo a Passo Completo (Meta Tag)

### 1. Obter Meta Tag no Console

1. Acesse: https://console.cloud.google.com/run/domains
2. Clique em "Verify a new domain"
3. Digite: `monpec.com.br`
4. Escolha: "HTML tag"
5. **Copie o código** da meta tag

### 2. Adicionar ao Template

**Arquivo:** `templates/base.html`

**Localização:** Dentro do `<head>`, após a linha 11

**Adicione:**

```html
<!-- Google Cloud Domain Verification -->
<meta name="google-site-verification" content="CODIGO_COPIADO_AQUI" />
```

### 3. Fazer Deploy

```bash
# No seu computador local
git add templates/base.html
git commit -m "Adicionar meta tag verificação domínio Cloud Run"
git push origin master

# No Cloud Shell
cd ~/Monpec_GestaoRural
git pull origin master
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10
```

### 4. Verificar no Console

1. **Aguarde 2-3 minutos** após o deploy
2. **Volte para:** https://console.cloud.google.com/run/domains
3. **Clique em:** "Verify" ou "Verificar" ao lado de `monpec.com.br`
4. Se estiver correto, você verá ✅ "Verified" ou "Verificado"

### 5. Mapear Domínio

Depois de verificado, execute no Cloud Shell:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

### 6. Configurar DNS

O comando acima vai retornar instruções de DNS. Configure no seu provedor de domínio.

---

## 🔗 Links Úteis

- **Console de Domínios:** https://console.cloud.google.com/run/domains
- **Documentação:** https://cloud.google.com/run/docs/mapping-custom-domains

---

## ⚡ Resumo Rápido

1. ✅ Acesse: https://console.cloud.google.com/run/domains
2. ✅ Clique em "Verify a new domain"
3. ✅ Digite `monpec.com.br`
4. ✅ Escolha "HTML tag"
5. ✅ Copie a meta tag
6. ✅ Adicione ao `templates/base.html`
7. ✅ Faça deploy
8. ✅ Volte ao console e clique em "Verify"
9. ✅ Depois mapeie o domínio

---

**Próximo passo:** Acesse o Console Web e siga os passos acima!













