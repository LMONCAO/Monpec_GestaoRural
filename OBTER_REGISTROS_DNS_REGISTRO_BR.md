# 📋 Como Obter os Registros DNS para o Registro.br

## 🎯 Objetivo
Configurar `monpec.com.br` para apontar para `https://monpec-29862706245.us-central1.run.app/`

---

## ✅ Método 1: Via Console Web do Google Cloud (RECOMENDADO)

### Passo 1: Acessar o Console do Google Cloud

1. Acesse: **https://console.cloud.google.com/run**
2. Faça login com sua conta: `l.moncaosilva@gmail.com`
3. Selecione o projeto: **monpec-sistema-rural**

### Passo 2: Encontrar o Serviço monpec

1. Na lista de serviços, clique no serviço **"monpec"**
2. Você verá a página de detalhes do serviço

### Passo 3: Adicionar Domínio Customizado

1. No topo da página, procure pela aba **"DOMÍNIOS CUSTOMIZADOS"** ou **"Custom Domains"**
2. Clique nessa aba
3. Clique no botão **"ADICIONAR Mapeamento de Domínio"** ou **"Add Mapping"**
4. Digite: **monpec.com.br**
5. Clique em **"CONTINUAR"** ou **"Continue"**

### Passo 4: Obter os Registros DNS ⚠️ IMPORTANTE

Após clicar em "CONTINUAR", o Google Cloud vai mostrar uma tela com os **REGISTROS DNS** que você precisa adicionar no Registro.br.

**📝 ANOTE TODOS OS REGISTROS QUE APARECEREM!**

**Exemplo do que você verá:**

```
Registro A:
Nome: @
Valor: 151.101.1.195
Tipo: A
TTL: 3600

Registro CNAME:
Nome: www
Valor: ghs.googlehosted.com
Tipo: CNAME
TTL: 3600
```

**⚠️ IMPORTANTE:** Os valores reais serão DIFERENTES! Use os valores EXATOS que aparecerem na tela!

---

## 📋 Método 2: Via Linha de Comando (Alternativo)

Se você preferir usar a linha de comando, primeiro precisa verificar o domínio:

### Passo 1: Verificar Propriedade do Domínio

```powershell
gcloud domains verify monpec.com.br --web-resource
```

Isso vai gerar um registro TXT que você precisa adicionar no Registro.br primeiro.

### Passo 2: Adicionar Registro TXT no Registro.br

1. Acesse o painel do Registro.br
2. Vá em "Zona DNS" ou "Registros DNS"
3. Adicione o registro TXT fornecido pelo comando acima
4. Aguarde alguns minutos

### Passo 3: Mapear o Domínio

```powershell
gcloud beta run domain-mappings create `
    --service monpec `
    --domain monpec.com.br `
    --region us-central1
```

### Passo 4: Obter os Registros DNS

```powershell
gcloud beta run domain-mappings describe `
    --domain monpec.com.br `
    --region us-central1 `
    --format="value(status.resourceRecords)"
```

---

## 🌐 Configurar no Registro.br

### Passo 1: Acessar o Painel

1. Acesse: **https://registro.br/painel/**
2. Faça login na sua conta
3. Selecione o domínio **monpec.com.br**

### Passo 2: Encontrar a Seção de DNS

Procure por uma dessas opções no menu:
- **"DNS"** → **"Zona DNS"**
- **"DNS"** → **"Registros DNS"**
- **"Gerenciar"** → **"DNS"**

**Se você NÃO encontrar essa seção:**

1. Procure por um botão: **"UTILIZAR DNS DO REGISTRO.BR"** ou **"Ativar DNS Hosting"**
2. Clique nesse botão
3. Aguarde alguns minutos
4. Atualize a página (F5)
5. Agora deve aparecer a seção "Zona DNS"

### Passo 3: Adicionar os Registros DNS

Use os valores EXATOS que o Google Cloud forneceu no Passo 4 do Método 1.

**Exemplo (use seus valores reais):**

#### Registro A (para monpec.com.br):

1. Clique em **"Adicionar Registro"** ou **"+ Novo Registro"**
2. Preencha:
   - **Tipo:** A
   - **Nome:** @ (ou monpec.com.br, dependendo da interface)
   - **Valor:** [IP fornecido pelo Google Cloud]
   - **TTL:** 3600
3. Salve

#### Registro CNAME (para www.monpec.com.br):

1. Clique em **"Adicionar Registro"** novamente
2. Preencha:
   - **Tipo:** CNAME
   - **Nome:** www
   - **Valor:** [valor fornecido pelo Google Cloud, geralmente ghs.googlehosted.com]
   - **TTL:** 3600
3. Salve

### Passo 4: Verificar se Foi Salvo

1. Verifique se os registros aparecem na lista
2. Confirme que os valores estão corretos
3. Se algo estiver errado, clique em **"Editar"** ou **"Modificar"**

---

## ⏰ Aguardar Propagação DNS

Após adicionar os registros DNS:

1. **Aguarde de 15 minutos a 2 horas**
   - Geralmente leva menos de 1 hora
   - Pode levar até 48 horas em casos raros

2. **Verificar propagação:**
   - Acesse: **https://dnschecker.org**
   - Digite: **monpec.com.br**
   - Selecione: Tipo **A**
   - Clique em **"Search"**
   - Verifique se o IP correto aparece em vários servidores DNS

---

## ✅ Testar o Acesso

1. Aguarde pelo menos **15 minutos** após adicionar os registros
2. Abra seu navegador
3. Acesse: **https://monpec.com.br**
4. Verifique se o site carrega

**Se funcionar:**
- ✅ Pronto! Seu domínio está configurado!
- ⏳ O SSL (cadeado verde) pode demorar até 24 horas para aparecer

**Se não funcionar:**
- Aguarde mais um pouco (pode levar até 2 horas)
- Verifique se os registros DNS foram salvos corretamente no Registro.br
- Confira se os valores estão exatamente como o Google Cloud forneceu

---

## 🆘 Problemas Comuns

### Problema 1: "Não encontro a seção Zona DNS no Registro.br"

**Solução:**
- Ligue para o suporte do Registro.br: **0800 777 0001**
- Peça para ativar o "DNS Hosting" ou "Zona DNS" para monpec.com.br
- Eles vão te ajudar a encontrar onde adicionar os registros

### Problema 2: "Adicionei os registros mas ainda não funciona"

**Verifique:**
1. ✅ Os valores estão EXATAMENTE como o Google Cloud forneceu?
2. ✅ Os registros foram salvos corretamente no Registro.br?
3. ✅ Aguardou pelo menos 15 minutos após salvar?
4. ✅ Verificou a propagação em https://dnschecker.org?

**Se tudo estiver correto:**
- Aguarde mais um pouco (pode levar até 2 horas)
- O SSL/HTTPS pode levar até 24 horas para aparecer

### Problema 3: "O Google Cloud pede verificação do domínio"

**Solução:**
- Siga o Método 1 (Console Web) - é mais fácil
- Ou siga o Método 2 para verificar o domínio primeiro
- A verificação geralmente é automática após adicionar os registros DNS

---

## 📞 Suporte

**Registro.br:**
- Telefone: **0800 777 0001**
- Email: suporte@registro.br
- Chat: Disponível no site do Registro.br

**Google Cloud:**
- Documentação: https://cloud.google.com/run/docs/mapping-custom-domains
- Suporte: Através do console do Google Cloud

---

## 🎯 Resumo Rápido

1. **Acesse o Console do Google Cloud** → Cloud Run → Serviço monpec
2. **Adicione domínio customizado** → monpec.com.br
3. **ANOTE os registros DNS** fornecidos pelo Google Cloud
4. **No Registro.br** → Zona DNS → Adicione os registros A e CNAME
5. **Aguarde propagação** (15 min - 2 horas)
6. **Teste o acesso** → https://monpec.com.br

---

**⚠️ LEMBRE-SE:** Use os valores EXATOS que o Google Cloud fornece quando você adiciona o domínio customizado. Não use valores genéricos ou de exemplo!












