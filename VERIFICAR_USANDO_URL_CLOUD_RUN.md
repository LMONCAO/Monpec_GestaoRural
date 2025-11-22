# ✅ Verificar Google Search Console usando URL do Cloud Run

## 🎯 Situação Atual

- ✅ Site funcionando: `https://monpec-29862706245.us-central1.run.app/`
- ❌ `monpec.com.br` ainda não funciona (DNS não propagou)
- ✅ Meta tag e arquivo HTML já estão no código (já no site)

---

## ✅ Solução: Verificar pela URL do Cloud Run

Você pode verificar o Google Search Console usando a URL do Cloud Run que **já está funcionando**!

### **Opção 1: Adicionar Propriedade com URL do Cloud Run**

1. Acesse: https://search.google.com/search-console
2. Clique em **"Adicionar propriedade"** ou o botão **"+"** no topo
3. Selecione: **"Prefixo de URL"**
4. Digite: `https://monpec-29862706245.us-central1.run.app`
5. Clique em **"Continuar"**
6. Escolha o método: **"Tag HTML"**
7. Clique em **"VERIFICAR"**

✅ **Pronto!** O Google vai verificar usando a URL do Cloud Run que já está funcionando!

---

### **Opção 2: Verificar com Arquivo HTML**

1. Acesse: https://search.google.com/search-console
2. Adicione a propriedade: `https://monpec-29862706245.us-central1.run.app`
3. Escolha o método: **"Arquivo HTML"**
4. Clique em **"VERIFICAR"**
5. O Google vai acessar: `https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html`

✅ **Pronto!** O arquivo já está configurado e funcionando!

---

## 🔍 Verificar se a Meta Tag Está no Site

Vamos verificar se a meta tag está realmente no site:

1. Acesse: https://monpec-29862706245.us-central1.run.app/
2. Pressione **Ctrl+U** (ou botão direito → "Ver código-fonte")
3. Procure por: `google-site-verification`
4. Deve aparecer: `<meta name="google-site-verification" content="vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk" />`

---

## 🔍 Verificar se o Arquivo HTML Está Funcionando

1. Acesse: https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
2. Deve aparecer: `google-site-verification: google40933139f3b0d469.html`

---

## 📋 Depois que o DNS Propagar

Quando `monpec.com.br` estiver funcionando:

1. Você pode adicionar uma **segunda propriedade** no Google Search Console:
   - `https://monpec.com.br`
2. Ou pode fazer **mudança de endereço** (se preferir)
3. As duas URLs vão funcionar!

---

## ✅ Resumo Rápido

**Para verificar AGORA (site já funciona):**
1. Google Search Console → Adicionar propriedade
2. URL: `https://monpec-29862706245.us-central1.run.app`
3. Método: **"Tag HTML"** ou **"Arquivo HTML"**
4. Clicar em **"VERIFICAR"**
5. ✅ **Pronto!**

**Depois (quando DNS propagar):**
- Adicionar também: `https://monpec.com.br`

---

## 🎯 Vantagens

- ✅ Verifica **agora** (não precisa esperar DNS)
- ✅ Meta tag e arquivo HTML já estão funcionando
- ✅ Depois pode adicionar `monpec.com.br` também
- ✅ Ambas as URLs vão funcionar no Google Search Console

---

**Última atualização:** Dezembro 2025

