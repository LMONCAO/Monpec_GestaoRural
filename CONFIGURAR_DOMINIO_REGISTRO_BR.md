# 🌐 Configurar monpec.com.br no Registro.br para Google Cloud Run

## ⚠️ IMPORTANTE: Diferença entre Servidores DNS e Registros DNS

### **Duas opções no Registro.br:**

1. **ALTERAR SERVIDORES DNS** (o que você está vendo agora)
   - Você troca os servidores DNS do Registro.br por outros servidores
   - **NÃO é isso que você precisa para o Cloud Run!**

2. **REGISTROS DNS** (Zona DNS)
   - Você mantém os servidores DNS do Registro.br
   - Adiciona registros A, CNAME, TXT, etc.
   - **É ISSO que você precisa para o Cloud Run!**

---

## ✅ Passo a Passo Correto para Cloud Run

### **PASSO 1: Mapear Domínio no Cloud Run PRIMEIRO** ⚠️ IMPORTANTE

**Você DEVE fazer isso ANTES de configurar qualquer coisa no Registro.br!**

1. Acesse: https://console.cloud.google.com/run
2. Selecione o serviço `monpec`
3. Clique na aba **"DOMÍNIOS CUSTOMIZADOS"** ou **"Custom Domains"**
4. Clique em **"ADICIONAR Mapeamento de Domínio"**
5. Digite: `monpec.com.br`
6. Clique em **"CONTINUAR"**

**⚠️ O Google Cloud vai mostrar os registros DNS que você precisa adicionar.**
**Anote TODOS esses registros!**

---

### **PASSO 2: Configurar Registros DNS no Registro.br**

Agora que você tem os registros DNS do Google Cloud:

1. **No painel do Registro.br, você tem duas opções:**

#### **Opção A: Usar a Zona DNS do Registro.br (RECOMENDADO)**

1. No painel do Registro.br, procure por:
   - **"Zona DNS"**
   - **"Gerenciar DNS"**
   - **"Registros DNS"**
   - **"DNS Hosting"**

2. Se você não encontrar essa opção, você pode:
   - **Usar os servidores DNS do Registro.br** (opção "UTILIZAR DNS DO REGISTRO.BR")
   - Depois procurar pela seção de "Zona DNS" para adicionar registros

3. Adicione os registros que o Google Cloud forneceu:
   - Geralmente são registros do tipo **A** ou **CNAME**
   - Adicione EXATAMENTE como o Google Cloud indicou

#### **Opção B: Delegar para Cloud DNS do Google**

Se o Registro.br não permitir adicionar registros DNS facilmente:

1. No Google Cloud Console, vá para **Cloud DNS**
2. Crie uma zona DNS para `monpec.com.br`
3. Configure os registros na zona do Cloud DNS
4. No Registro.br, altere os servidores DNS para os servidores que o Cloud DNS fornecer

**⚠️ Esta opção é mais complexa e normalmente não é necessária.**

---

## 🔍 Como Encontrar a Seção de Registros DNS no Registro.br

### **Método 1: Verificar se já tem DNS Hosting ativado**

1. No painel do Registro.br, procure por:
   - Menu lateral: **"DNS"** ou **"Zona DNS"**
   - Se houver, você pode adicionar registros diretamente

### **Método 2: Ativar DNS Hosting do Registro.br**

Se você estiver vendo apenas a opção de "ALTERAR SERVIDORES DNS":

1. Clique em **"UTILIZAR DNS DO REGISTRO.BR"** (botão cinza)
2. Isso vai ativar o DNS Hosting do Registro.br
3. Depois você deve ver uma nova seção para **"Zona DNS"** ou **"Registros DNS"**
4. Nessa seção, você pode adicionar:
   - Registros tipo **A**
   - Registros tipo **CNAME**
   - Registros tipo **TXT** (para verificação do Google Search Console)

---

## 📋 Exemplo de Registros DNS que Você Precisa Adicionar

**⚠️ IMPORTANTE: Use os valores EXATOS que o Google Cloud fornecer!**

Exemplo (seus valores serão diferentes):

```
Tipo: A
Nome: @ (ou monpec.com.br)
Valor: 151.101.1.195 (IP fornecido pelo Google Cloud)
TTL: 3600

Tipo: CNAME
Nome: www
Valor: ghs.googlehosted.com
TTL: 3600
```

---

## 🔍 Sobre o Registro TXT do Google Search Console

**A imagem mostra um registro TXT do Google Search Console:**

```
google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJI
```

### **Isso é diferente do Cloud Run!**

- **Cloud Run:** Precisa de registros **A** e **CNAME**
- **Google Search Console:** Precisa de um registro **TXT** (para verificação)

### **Você pode adicionar ambos:**

1. Adicione os registros **A** e **CNAME** para o Cloud Run
2. Adicione também o registro **TXT** para o Google Search Console

**Como adicionar o TXT no Registro.br:**

1. Na seção de "Zona DNS" ou "Registros DNS"
2. Adicione um novo registro:
   - **Tipo:** TXT
   - **Nome:** @ (ou monpec.com.br)
   - **Valor:** `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJI`
   - **TTL:** 3600

---

## ✅ Checklist Completo

### **Antes de começar no Registro.br:**

- [ ] Mapeou o domínio no Cloud Run primeiro
- [ ] Anotou TODOS os registros DNS fornecidos pelo Google Cloud
- [ ] Tem acesso ao painel do Registro.br

### **No Registro.br:**

- [ ] Encontrou ou ativou a seção "Zona DNS" / "Registros DNS"
- [ ] Adicionou o registro **A** (ou **AAAA** se fornecido) para o domínio principal
- [ ] Adicionou o registro **CNAME** para www (se fornecido)
- [ ] Adicionou o registro **TXT** para Google Search Console (opcional, mas recomendado)
- [ ] Salvou todas as alterações

### **Após configurar:**

- [ ] Aguardou 15 minutos - 2 horas para propagação DNS
- [ ] Verificou propagação em: https://dnschecker.org
- [ ] Testou acesso em: https://monpec.com.br
- [ ] Verificou SSL/HTTPS (pode levar até 24 horas)

---

## 🆘 Não Encontra a Seção de Registros DNS?

### **Contate o Suporte do Registro.br:**

- **Telefone:** 0800 777 0001
- **Email:** suporte@registro.br
- **Chat:** Disponível no site do Registro.br

**Peça para eles:**
- Ativar o "DNS Hosting" ou "Zona DNS" para seu domínio
- Mostrar onde adicionar registros tipo A, CNAME e TXT

---

## 📞 Comandos Úteis para Verificar

```powershell
# Verificar mapeamento no Cloud Run
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Verificar propagação DNS
nslookup monpec.com.br
nslookup www.monpec.com.br

# Verificar registro TXT
nslookup -type=TXT monpec.com.br
```

---

## ✅ Resultado Esperado

Após configurar tudo corretamente:

- ✅ `https://monpec.com.br` → Acessa seu site no Cloud Run
- ✅ `https://www.monpec.com.br` → Acessa seu site no Cloud Run
- ✅ SSL/HTTPS funciona automaticamente
- ✅ Google Search Console verificado (se adicionou o TXT)

---

## 🎯 Resumo Rápido

1. **PRIMEIRO:** Mapeie o domínio no Cloud Run e anote os registros DNS
2. **SEGUNDO:** No Registro.br, encontre/ative a seção "Zona DNS"
3. **TERCEIRO:** Adicione os registros A e CNAME fornecidos pelo Cloud Run
4. **OPCIONAL:** Adicione o registro TXT para Google Search Console
5. **QUARTO:** Aguarde a propagação DNS (15 min - 2 horas)
6. **QUINTO:** Teste o acesso e aguarde o SSL (até 24 horas)

---

**⚠️ IMPORTANTE:** Não altere os servidores DNS se você não tiver uma zona DNS configurada em outro lugar. Use o DNS Hosting do próprio Registro.br e adicione os registros lá!


