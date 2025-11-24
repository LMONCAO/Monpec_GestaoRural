# 🌐 Configurar Domínio monpec.com.br no Cloud Run

## ✅ Status Atual

- ✅ Serviço Cloud Run funcionando
- ✅ URL atual: https://monpec-29862706245.us-central1.run.app
- 🎯 Objetivo: Configurar monpec.com.br

---

## 📋 Passo a Passo

### 1. Verificar Domínio no Google Cloud

Execute no Cloud Shell:

```bash
# Verificar se o domínio já está verificado
gcloud domains list-user-verified

# Se não estiver, adicionar domínio
gcloud domains verify monpec.com.br
```

---

### 2. Mapear Domínio no Cloud Run

Execute no Cloud Shell:

```bash
# Mapear domínio para o serviço
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

# Para www também (opcional)
gcloud run domain-mappings create \
    --service monpec \
    --domain www.monpec.com.br \
    --region us-central1
```

**Isso vai retornar informações de DNS que você precisa configurar!**

---

### 3. Configurar DNS no Provedor do Domínio

Após executar o comando acima, você receberá instruções de DNS. Geralmente são:

#### Para monpec.com.br:
- **Tipo:** A
- **Nome:** @ ou monpec.com.br
- **Valor:** IP fornecido pelo Google

#### Para www.monpec.com.br:
- **Tipo:** CNAME
- **Nome:** www
- **Valor:** ghs.googlehosted.com

**OU use os valores exatos que o comando retornar!**

---

### 4. Verificar Configuração DNS

Execute no Cloud Shell:

```bash
# Verificar status do mapeamento
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Verificar DNS
dig monpec.com.br
```

---

### 5. Aguardar Propagação DNS

- ⏳ Pode levar de **15 minutos a 48 horas**
- 🔍 Verifique com: `dig monpec.com.br` ou `nslookup monpec.com.br`

---

### 6. Verificar ALLOWED_HOSTS

O arquivo `settings_gcp.py` já deve ter `monpec.com.br` configurado. Vamos verificar:

```bash
# No Cloud Shell, verificar se está configurado
cd ~/Monpec_GestaoRural
grep -n "monpec.com.br" sistema_rural/settings_gcp.py
```

Se não estiver, precisamos atualizar e fazer novo deploy.

---

## 🚀 Comandos Rápidos (Copiar e Colar)

### Opção 1: Comando Completo

```bash
cd ~/Monpec_GestaoRural && gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1 && gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1 && gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### Opção 2: Passo a Passo

```bash
# 1. Verificar domínio
gcloud domains list-user-verified

# 2. Mapear domínio principal
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1

# 3. Mapear www (opcional)
gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1

# 4. Ver status
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

---

## ⚠️ Importante

1. **Você precisa ter acesso ao DNS do domínio** (onde o domínio está registrado)
2. **Propagação DNS pode levar até 48 horas**
3. **O domínio precisa estar verificado no Google Cloud** (se não estiver, o comando vai orientar)

---

## 🔍 Verificar se Está Funcionando

Após configurar o DNS e aguardar propagação:

```bash
# Testar acesso
curl -I https://monpec.com.br

# Ver certificado SSL
openssl ssl_client -connect monpec.com.br:443 -showcerts
```

---

## 📝 Notas

- O Google Cloud gera automaticamente o certificado SSL (HTTPS)
- Não é necessário configurar SSL manualmente
- O domínio `www.monpec.com.br` é opcional, mas recomendado

---

**Próximo passo:** Execute os comandos no Cloud Shell e siga as instruções de DNS que aparecerem!













