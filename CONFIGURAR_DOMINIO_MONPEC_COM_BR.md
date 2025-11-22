# 🌐 Configurar Domínio monpec.com.br no Google Cloud Run

Este guia mostra como fazer o site aparecer como `monpec.com.br` ao invés de `https://monpec-29862706245.us-central1.run.app/`.

---

## 📋 Pré-requisitos

- ✅ Serviço Cloud Run já deployado e funcionando
- ✅ Domínio `monpec.com.br` registrado e sob seu controle
- ✅ Acesso ao painel do provedor de DNS (Registro.br, GoDaddy, etc.)
- ✅ Google Cloud SDK instalado e configurado

---

## 🚀 Passo 1: Verificar o Serviço Cloud Run

Primeiro, vamos verificar se o serviço está rodando:

```bash
# Listar serviços Cloud Run
gcloud run services list --region us-central1

# Verificar detalhes do serviço
gcloud run services describe monpec --region us-central1
```

**Anote a URL atual do serviço** (exemplo: `https://monpec-29862706245.us-central1.run.app`)

---

## 🔧 Passo 2: Criar Mapeamento de Domínio

Execute o comando para criar o mapeamento do domínio:

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

**Resultado esperado:**
```
Waiting for domain mapping to be created...done.
Domain mapping created. Please update your DNS records:
  Domain: monpec.com.br
  Resource records:
    Name: monpec.com.br
    Type: CNAME
    Data: ghs.googlehosted.com
```

**⚠️ IMPORTANTE:** Anote o valor `ghs.googlehosted.com` - você precisará dele no próximo passo!

---

## 🌍 Passo 3: Configurar DNS no Provedor

Agora você precisa configurar os registros DNS no seu provedor de domínio.

### **Opção A: Registro.br (domínios .br)**

1. Acesse o painel do [Registro.br](https://registro.br)
2. Faça login com suas credenciais
3. Selecione o domínio `monpec.com.br`
4. Vá em **"DNS"** ou **"Zona DNS"**
5. Adicione os seguintes registros:

#### **Registro Principal (monpec.com.br):**
- **Tipo:** `CNAME`
- **Nome:** `@` (ou deixe em branco, dependendo do painel)
- **Valor:** `ghs.googlehosted.com`
- **TTL:** `3600` (ou padrão)

#### **Registro para www (www.monpec.com.br):**
- **Tipo:** `CNAME`
- **Nome:** `www`
- **Valor:** `ghs.googlehosted.com`
- **TTL:** `3600` (ou padrão)

### **Opção B: GoDaddy, Namecheap, ou outros provedores**

1. Acesse o painel do seu provedor
2. Vá em **"DNS Management"** ou **"Gerenciar DNS"**
3. Adicione os mesmos registros CNAME acima

### **Opção C: Cloud DNS (Google Cloud)**

Se você estiver usando Cloud DNS do Google:

```bash
# Criar zona DNS (se ainda não tiver)
gcloud dns managed-zones create monpec-zone \
    --dns-name=monpec.com.br \
    --description="Zona DNS para monpec.com.br"

# Adicionar registro CNAME
gcloud dns record-sets create monpec.com.br. \
    --zone=monpec-zone \
    --type=CNAME \
    --rrdatas=ghs.googlehosted.com. \
    --ttl=3600

# Adicionar registro CNAME para www
gcloud dns record-sets create www.monpec.com.br. \
    --zone=monpec-zone \
    --type=CNAME \
    --rrdatas=ghs.googlehosted.com. \
    --ttl=3600
```

---

## ⏳ Passo 4: Aguardar Propagação DNS

Após configurar o DNS, você precisa aguardar a propagação:

- **Tempo estimado:** 1-48 horas
- **Tempo típico:** 1-2 horas
- **Verificação:** Use ferramentas como:
  - [whatsmydns.net](https://www.whatsmydns.net/#CNAME/monpec.com.br)
  - [dnschecker.org](https://dnschecker.org/#CNAME/monpec.com.br)

**Verificar propagação via terminal:**
```bash
# Verificar registro CNAME
dig monpec.com.br CNAME

# Ou usando nslookup
nslookup -type=CNAME monpec.com.br
```

---

## ✅ Passo 5: Verificar Status do Mapeamento

Após a propagação DNS, verifique o status do mapeamento:

```bash
# Ver status do mapeamento
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Listar todos os mapeamentos
gcloud run domain-mappings list --region us-central1
```

**Status esperado:** `ACTIVE` (quando estiver funcionando)

---

## 🔍 Passo 6: Verificar Configurações Django

Certifique-se de que o Django está configurado para aceitar o domínio. O arquivo `sistema_rural/settings_gcp.py` já deve ter:

```python
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    # ... outros hosts
]

CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    # ... outras origens
]
```

**✅ Isso já está configurado no seu projeto!**

---

## 🧪 Passo 7: Testar o Domínio

Após a propagação DNS, teste o acesso:

1. **Acesse `https://monpec.com.br`** no navegador
2. **Acesse `https://www.monpec.com.br`** no navegador
3. Verifique se o site carrega corretamente
4. Verifique se não há erros de SSL/HTTPS

---

## 🔒 Passo 8: Configurar SSL/HTTPS (Automático)

O Google Cloud Run **configura SSL automaticamente** quando você mapeia um domínio personalizado. Não é necessário configurar certificados manualmente.

O SSL será ativado automaticamente após:
- ✅ DNS propagado corretamente
- ✅ Mapeamento de domínio ativo
- ⏳ Aguardar alguns minutos para o certificado ser emitido

---

## 🆘 Troubleshooting

### **Problema: Domínio não está funcionando**

**Solução 1: Verificar DNS**
```bash
# Verificar se o CNAME está correto
dig monpec.com.br CNAME

# Deve retornar: ghs.googlehosted.com
```

**Solução 2: Verificar status do mapeamento**
```bash
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

**Solução 3: Verificar logs**
```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### **Problema: Erro 404 ou "Site não encontrado"**

**Solução:** Verificar se o serviço Cloud Run está ativo:
```bash
gcloud run services describe monpec --region us-central1
```

### **Problema: Erro de SSL/HTTPS**

**Solução:** Aguardar alguns minutos. O Google Cloud leva alguns minutos para emitir o certificado SSL após a propagação DNS.

### **Problema: Erro "DisallowedHost" no Django**

**Solução:** Verificar se `monpec.com.br` está em `ALLOWED_HOSTS`:
```bash
# Atualizar variáveis de ambiente se necessário
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars ALLOWED_HOSTS=monpec.com.br,www.monpec.com.br
```

**Nota:** O Django já está configurado corretamente no `settings_gcp.py`, então isso não deve ser necessário.

---

## 📝 Resumo dos Comandos

```bash
# 1. Criar mapeamento de domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

# 2. Verificar status
gcloud run domain-mappings describe monpec.com.br --region us-central1

# 3. Listar mapeamentos
gcloud run domain-mappings list --region us-central1

# 4. Verificar DNS
dig monpec.com.br CNAME
```

---

## ✅ Checklist Final

- [ ] Mapeamento de domínio criado no Cloud Run
- [ ] Registro CNAME configurado no provedor DNS
- [ ] DNS propagado (verificado com dig/nslookup)
- [ ] Status do mapeamento: ACTIVE
- [ ] Site acessível via `https://monpec.com.br`
- [ ] Site acessível via `https://www.monpec.com.br`
- [ ] SSL/HTTPS funcionando
- [ ] Sem erros no Django (verificar logs)

---

## 🎯 Próximos Passos

Após configurar o domínio:

1. **Atualizar URLs internas** (se necessário)
2. **Configurar redirecionamento** de www para não-www (ou vice-versa)
3. **Atualizar configurações de email** (se usar domínio para envio)
4. **Atualizar links** em documentação e marketing

---

**Última atualização:** Dezembro 2025

