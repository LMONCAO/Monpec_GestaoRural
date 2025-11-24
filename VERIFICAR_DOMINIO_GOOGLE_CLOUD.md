# 🔐 Verificar Domínio no Google Cloud - Passo a Passo

## ❌ Problema Atual

O erro mostra:
```
ERROR: The provided domain does not appear to be verified for the current account
```

Isso significa que o Google Cloud precisa verificar que você é o proprietário do domínio `monpec.com.br` antes de permitir o mapeamento.

---

## ✅ Solução: Verificar o Domínio Primeiro

### Método 1: Verificar via Google Search Console (Mais Fácil)

Você já verificou o domínio no Google Search Console usando a meta tag. Agora precisa verificar também no Google Cloud.

#### Passo 1: Acessar Verificação de Domínio

1. **Acesse:** https://console.cloud.google.com/domains
2. **Ou acesse:** https://console.cloud.google.com/apis/credentials/domainverification
3. Faça login se necessário
4. Certifique-se de que o projeto **monpec-sistema-rural** está selecionado

#### Passo 2: Adicionar Domínio para Verificação

1. Clique em **"Adicionar domínio"** ou **"Add Domain"**
2. Digite: **monpec.com.br**
3. Clique em **"Continuar"** ou **"Continue"**

#### Passo 3: Escolher Método de Verificação

O Google Cloud vai oferecer métodos de verificação. Escolha um:

**Opção A: Meta Tag (Recomendado - Mais Rápido)**
- O Google vai fornecer uma meta tag
- Adicione essa meta tag no `templates/base.html`
- Faça deploy
- Volte e verifique

**Opção B: Arquivo HTML**
- O Google vai fornecer um arquivo HTML
- Faça upload do arquivo para a raiz do site
- Volte e verifique

**Opção C: DNS TXT Record**
- O Google vai fornecer um registro TXT
- Adicione esse registro no Registro.br
- Volte e verifique

---

### Método 2: Verificar via Linha de Comando

No Cloud Shell, execute:

```bash
# Verificar domínio via meta tag (mais fácil)
gcloud domains verify monpec.com.br --web-resource
```

Isso vai gerar uma meta tag que você precisa adicionar no template.

---

## 🚀 Passo a Passo Completo (Método Meta Tag)

### 1. Obter Código de Verificação

No Cloud Shell:

```bash
gcloud domains verify monpec.com.br --web-resource
```

**Ou pela interface web:**
1. Acesse: https://console.cloud.google.com/apis/credentials/domainverification
2. Clique em "Adicionar domínio"
3. Digite: `monpec.com.br`
4. Escolha "Meta tag"
5. Copie o código fornecido

### 2. Adicionar Meta Tag no Template

O código será algo como:
```
google-site-verification: CODIGO_AQUI
```

**Atualize o arquivo `templates/base.html`:**

Encontre a linha:
```html
<meta name="google-site-verification" content="google40933139f3b0d469.html" />
```

**Substitua por:**
```html
<meta name="google-site-verification" content="CODIGO_AQUI" />
```

(Onde `CODIGO_AQUI` é o código fornecido pelo Google Cloud)

### 3. Fazer Deploy

```bash
# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
```

### 4. Verificar o Domínio

Após o deploy, volte ao Google Cloud Console e clique em **"Verificar"** ou execute:

```bash
gcloud domains verify monpec.com.br --web-resource --check
```

### 5. Mapear o Domínio no Cloud Run

Agora que o domínio está verificado, você pode mapeá-lo:

```bash
gcloud beta run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### 6. Obter os Registros DNS

```bash
gcloud beta run domain-mappings describe \
    --domain monpec.com.br \
    --region us-central1 \
    --format="value(status.resourceRecords)"
```

---

## 🔄 Método Alternativo: Usar DNS TXT Record

Se preferir usar DNS em vez de meta tag:

### 1. Obter Registro TXT

```bash
gcloud domains verify monpec.com.br --dns
```

Isso vai gerar um registro TXT que você precisa adicionar no Registro.br.

### 2. Adicionar no Registro.br

1. Acesse: https://registro.br/painel/
2. Vá em "Zona DNS"
3. Adicione um registro:
   - **Tipo:** TXT
   - **Nome:** @ (ou monpec.com.br)
   - **Valor:** [código fornecido pelo Google Cloud]
   - **TTL:** 3600

### 3. Aguardar Propagação

Aguarde 15 minutos - 2 horas.

### 4. Verificar

```bash
gcloud domains verify monpec.com.br --dns --check
```

---

## 📋 Checklist

### Verificação do Domínio:
- [ ] Acessou console de verificação de domínio
- [ ] Adicionou domínio `monpec.com.br`
- [ ] Escolheu método de verificação (meta tag ou DNS)
- [ ] Implementou a verificação (meta tag no template ou TXT no DNS)
- [ ] Fez deploy (se usou meta tag)
- [ ] Aguardou propagação (se usou DNS)
- [ ] Verificou o domínio com sucesso

### Mapeamento no Cloud Run:
- [ ] Domínio verificado no Google Cloud
- [ ] Mapeou domínio no Cloud Run
- [ ] Obteve registros DNS
- [ ] Adicionou registros DNS no Registro.br
- [ ] Aguardou propagação DNS
- [ ] Testou: https://monpec.com.br

---

## 🆘 Problemas Comuns

### Problema 1: "Domínio já verificado em outra conta"

**Solução:**
- Verifique se você está usando a conta correta do Google Cloud
- O domínio pode estar verificado em outra conta Google

### Problema 2: "Meta tag não encontrada"

**Solução:**
- Verifique se fez o deploy após adicionar a meta tag
- Verifique se a meta tag está no template correto (`templates/base.html`)
- Teste o site e veja o código-fonte (Ctrl+U) para confirmar que a meta tag está presente

### Problema 3: "Registro TXT não encontrado"

**Solução:**
- Aguarde mais tempo para propagação DNS (pode levar até 2 horas)
- Verifique se o registro TXT foi adicionado corretamente no Registro.br
- Use https://dnschecker.org para verificar propagação

---

## 🎯 Resumo Rápido

1. **Verificar domínio no Google Cloud:**
   - Acesse: https://console.cloud.google.com/apis/credentials/domainverification
   - Adicione `monpec.com.br`
   - Escolha método (meta tag ou DNS)
   - Implemente e verifique

2. **Mapear domínio no Cloud Run:**
   - Após verificação, mapeie o domínio
   - Obtenha registros DNS
   - Adicione no Registro.br

3. **Aguardar e testar:**
   - Aguarde propagação
   - Teste: https://monpec.com.br

---

**🚀 Comece verificando o domínio no Google Cloud primeiro!**












