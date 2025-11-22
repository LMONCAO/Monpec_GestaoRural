# 🎯 Guia Rápido: Configurar monpec.com.br no Registro.br

## ⚠️ IMPORTANTE: Faça Isso ANTES de Configurar no Registro.br!

### **PASSO 0: Mapear Domínio no Cloud Run PRIMEIRO**

1. Acesse: https://console.cloud.google.com/run
2. Selecione o serviço `monpec`
3. Clique na aba **"DOMÍNIOS CUSTOMIZADOS"**
4. Clique em **"ADICIONAR Mapeamento de Domínio"**
5. Digite: `monpec.com.br`
6. **ANOTE os registros DNS que aparecerem!** ⚠️

**Você receberá algo como:**
```
Tipo A:
Nome: @
Valor: [um IP fornecido pelo Google]

Tipo CNAME:
Nome: www
Valor: ghs.googlehosted.com
```

---

## 📋 Configurando no Registro.br

### **Situação 1: Você está vendo "ALTERAR SERVIDORES DNS"**

**⚠️ NÃO é isso que você precisa!**

Você precisa de uma seção para **"ADICIONAR REGISTROS DNS"** ou **"ZONA DNS"**.

**O que fazer:**

1. **Procure no menu lateral do Registro.br:**
   - Procure por: **"Zona DNS"**
   - Ou: **"Gerenciar DNS"**
   - Ou: **"DNS Hosting"**
   - Ou: **"Registros DNS"**

2. **Se não encontrar, ative o DNS Hosting do Registro.br:**
   - Na tela que você está vendo, clique no botão **"UTILIZAR DNS DO REGISTRO.BR"** (botão cinza)
   - Isso vai ativar o DNS Hosting
   - Depois você deve ver uma nova seção para adicionar registros DNS

### **Situação 2: Você encontrou a seção de "Zona DNS" ou "Registros DNS"**

**Agora você pode adicionar os registros!**

1. **Adicione o registro tipo A (do Cloud Run):**
   - Clique em **"Adicionar Registro"** ou **"+ Novo Registro"**
   - **Tipo:** A
   - **Nome/Host:** `@` (ou deixe em branco, dependendo da interface)
   - **Valor/Destino:** [IP fornecido pelo Google Cloud]
   - **TTL:** 3600
   - Salve

2. **Adicione o registro tipo CNAME (do Cloud Run):**
   - Clique em **"Adicionar Registro"** novamente
   - **Tipo:** CNAME
   - **Nome/Host:** `www`
   - **Valor/Destino:** `ghs.googlehosted.com` (ou o valor fornecido pelo Google)
   - **TTL:** 3600
   - Salve

3. **Adicione o registro tipo TXT (do Google Search Console):**
   - Clique em **"Adicionar Registro"** novamente
   - **Tipo:** TXT
   - **Nome/Host:** `@` (ou deixe em branco)
   - **Valor/Destino:** `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJI`
   - **TTL:** 3600
   - Salve

---

## 🔍 Onde Está a Seção de Registros DNS no Registro.br?

### **Método 1: Menu Lateral**

No painel do Registro.br, procure no menu lateral por:
- **DNS** → **Zona DNS**
- **DNS** → **Registros DNS**
- **Gerenciar** → **DNS**

### **Método 2: Ativar DNS Hosting**

Se você só vê "ALTERAR SERVIDORES DNS":

1. Clique em **"UTILIZAR DNS DO REGISTRO.BR"**
2. Aguarde alguns minutos
3. Atualize a página
4. Você deve ver uma nova seção **"Zona DNS"**

### **Método 3: Contatar Suporte**

Se você não conseguir encontrar:

- **Suporte Registro.br:** 0800 777 0001
- **Email:** suporte@registro.br
- **Peça:** "Preciso ativar o DNS Hosting e adicionar registros DNS tipo A, CNAME e TXT"

---

## ✅ Checklist Final

Antes de configurar:
- [ ] Mapeou o domínio no Cloud Run
- [ ] Anotou os registros DNS fornecidos pelo Google Cloud

No Registro.br:
- [ ] Encontrou ou ativou a seção "Zona DNS" / "Registros DNS"
- [ ] Adicionou registro **A** para @ com o IP do Google Cloud
- [ ] Adicionou registro **CNAME** para www
- [ ] Adicionou registro **TXT** para Google Search Console (opcional mas recomendado)
- [ ] Salvou todas as alterações

Após configurar:
- [ ] Aguardou 15 minutos - 2 horas
- [ ] Verificou propagação em: https://dnschecker.org
- [ ] Testou acesso: https://monpec.com.br

---

## 📞 Precisa de Ajuda?

Se não conseguir encontrar onde adicionar os registros DNS no Registro.br:

**Contate o suporte:** 0800 777 0001

**Peça para eles:**
- Ativar "DNS Hosting" ou "Zona DNS" para monpec.com.br
- Mostrar onde você pode adicionar registros tipo A, CNAME e TXT

**Eles vão te guiar!** 😊


