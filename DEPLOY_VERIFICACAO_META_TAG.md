# ✅ Atualizar Meta Tag e Fazer Deploy

## ✅ O Que Foi Feito

A meta tag de verificação do Google Search Console foi atualizada em `templates/base.html`:

**Antes:**
```html
<meta name="google-site-verification" content="vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk" />
```

**Agora:**
```html
<meta name="google-site-verification" content="google40933139f3b0d469.html" />
```

---

## 🚀 Próximo Passo: Fazer Deploy

Execute estes comandos no Cloud Shell:

### 1. Build da Imagem

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### 2. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
```

---

## 🔍 Após o Deploy

### 1. Testar a Meta Tag

1. **Acesse:** `https://monpec-29862706245.us-central1.run.app`
2. **Visualize o código-fonte** (Ctrl+U ou botão direito → "Ver código-fonte")
3. **Procure por:** `google-site-verification`
4. **Verifique se aparece:**
   ```html
   <meta name="google-site-verification" content="google40933139f3b0d469.html" />
   ```

### 2. Verificar no Google Search Console

1. **Aguarde 2-3 minutos** após o deploy
2. **Volte ao Google Search Console**
3. **Certifique-se de estar usando o método "Tag HTML"** (não arquivo HTML)
4. **Clique em "VERIFICAR"**
5. **Aguarde alguns segundos**

---

## ⚠️ Importante

### Método Correto no Google Search Console

Certifique-se de estar usando o método **"Tag HTML"** ou **"Meta tag"**, NÃO o método **"Arquivo HTML"**.

**Como verificar:**
1. No Google Search Console, veja qual método está selecionado
2. Se estiver "Arquivo HTML", clique em **"Outros métodos de verificação"**
3. Selecione **"Tag HTML"** ou **"Meta tag"**
4. Use o código: `google40933139f3b0d469.html`

---

## 🆘 Se Não Funcionar

### Verificar se a Meta Tag Está Presente

1. Acesse: `https://monpec-29862706245.us-central1.run.app`
2. Visualize o código-fonte (Ctrl+U)
3. Procure por `google-site-verification`
4. Se não encontrar, o deploy pode não ter incluído a atualização

### Verificar Logs

```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### Fazer Deploy Novamente

Se a meta tag não aparecer, faça o deploy novamente:

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --platform managed --allow-unauthenticated
```

---

## ✅ Checklist

Antes de verificar no Google Search Console:

- [ ] Meta tag atualizada em `templates/base.html`
- [ ] Deploy realizado com sucesso
- [ ] Aguardou 2-3 minutos após deploy
- [ ] Testou o site e verificou código-fonte
- [ ] Meta tag está presente no código-fonte
- [ ] No Google Search Console, está usando método "Tag HTML"
- [ ] Pronto para clicar em "VERIFICAR"

---

**🚀 Faça o deploy agora e depois verifique no Google Search Console usando o método "Tag HTML"!**












