# 🔍 Configurar Verificação Google Search Console via DNS

Este guia mostra como verificar o domínio `monpec.com.br` no Google Search Console usando registro TXT no DNS.

---

## 📋 Pré-requisitos

- ✅ Domínio `monpec.com.br` registrado no Registro.br
- ✅ Acesso ao painel do Registro.br
- ✅ Código de verificação do Google Search Console: `vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk`

---

## 🚀 Passo a Passo

### **Passo 1: Acessar o Painel do Registro.br**

1. Acesse: https://registro.br
2. Faça login com suas credenciais
3. Vá em **"Meus Domínios"** ou **"Painel"**
4. Selecione o domínio `monpec.com.br`

### **Passo 2: Acessar Configurações DNS**

1. No painel do domínio, procure por:
   - **"DNS"** ou
   - **"Zona DNS"** ou
   - **"Gerenciar DNS"** ou
   - **"Configurações DNS"**

2. Clique para abrir as configurações DNS

### **Passo 3: Adicionar Registro TXT**

1. Procure por um botão ou link para **"Adicionar Registro"** ou **"Novo Registro"**
2. Selecione o tipo: **TXT**
3. Preencha os campos:

   **Configuração:**
   - **Tipo:** `TXT`
   - **Nome:** `@` (ou deixe em branco, ou `monpec.com.br` - depende do painel)
   - **Valor:** `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk`
   - **TTL:** `3600` (ou padrão)

4. Clique em **"Salvar"** ou **"Adicionar"**

### **Passo 4: Verificar no Google Search Console**

1. Acesse: https://search.google.com/search-console
2. Vá em **"Verificação de propriedade"**
3. Selecione o método: **"Registro TXT do DNS"**
4. Clique em **"Verificar"**

---

## ⚠️ Importante

### **Diferença entre CNAME e TXT:**

- **CNAME (Endereço do site):** `ghs.googlehosted.com`
  - Usado para mapear o domínio para o Google Cloud Run
  - Configurado em "Endereço do site"

- **TXT (Verificação):** `google-site-verification=...`
  - Usado apenas para verificar propriedade no Google Search Console
  - Configurado em "DNS" / "Zona DNS" como registro TXT separado

### **Ambos são necessários:**
- ✅ CNAME para o site funcionar
- ✅ TXT para verificar no Google Search Console

---

## 🔍 Verificar se está Configurado

### **Via Terminal (Windows):**

```powershell
# Verificar registro TXT
nslookup -type=TXT monpec.com.br
```

**Resultado esperado:**
```
monpec.com.br
        text = "google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk"
```

### **Via Navegador:**

1. Acesse: https://mxtoolbox.com/TXTLookup.aspx
2. Digite: `monpec.com.br`
3. Clique em **"TXT Lookup"**
4. Verifique se aparece o registro de verificação

---

## ⏳ Tempo de Propagação

- **Tempo típico:** 1-2 horas
- **Máximo:** até 48 horas
- **Verificação:** Use o comando `nslookup` acima para verificar

---

## 📝 Resumo dos Registros DNS Necessários

Para o domínio `monpec.com.br` funcionar completamente, você precisa de:

### **1. CNAME para o Site:**
- **Localização:** Campo "Endereço do site" no Registro.br
- **Tipo:** CNAME
- **Valor:** `ghs.googlehosted.com`
- **Finalidade:** Fazer o domínio apontar para o Google Cloud Run

### **2. TXT para Verificação:**
- **Localização:** Seção "DNS" / "Zona DNS" no Registro.br
- **Tipo:** TXT
- **Nome:** `@` (ou monpec.com.br)
- **Valor:** `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk`
- **Finalidade:** Verificar propriedade no Google Search Console

---

## 🆘 Troubleshooting

### **Problema: Registro TXT não aparece**

**Solução:**
1. Verifique se salvou corretamente no Registro.br
2. Aguarde a propagação DNS (1-2 horas)
3. Verifique com: `nslookup -type=TXT monpec.com.br`

### **Problema: Google não verifica**

**Solução:**
1. Certifique-se de que o valor está exatamente como fornecido
2. Não adicione espaços extras
3. Verifique se o nome do registro está correto (`@` ou `monpec.com.br`)

### **Problema: Não encontro onde adicionar TXT**

**Solução:**
- No Registro.br, procure por "DNS" ou "Zona DNS"
- Se não encontrar, entre em contato com o suporte do Registro.br
- Alternativa: Use apenas a meta tag no HTML (já configurada)

---

## ✅ Checklist

- [ ] Acessei o painel do Registro.br
- [ ] Encontrei a seção "DNS" ou "Zona DNS"
- [ ] Adicionei registro TXT com o valor correto
- [ ] Salvei a configuração
- [ ] Aguardei propagação (1-2 horas)
- [ ] Verifiquei com `nslookup -type=TXT monpec.com.br`
- [ ] Verifiquei no Google Search Console

---

**Última atualização:** Dezembro 2025

