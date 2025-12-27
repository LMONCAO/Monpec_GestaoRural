# ✅ PASSO A PASSO - CONFIGURAÇÃO DO MERCADO PAGO

## 🎯 O QUE JÁ FOI FEITO

✅ Credenciais adicionadas ao arquivo `.env`:
- Public Key: `APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3`
- Access Token: `APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940`

---

## 📋 O QUE VOCÊ PRECISA FAZER AGORA

### 1️⃣ REINICIAR O SERVIDOR DJANGO

**IMPORTANTE:** O servidor precisa ser reiniciado para carregar as novas configurações!

1. Vá no terminal onde o Django está rodando
2. Pressione `Ctrl+C` para parar o servidor
3. Inicie novamente:
   ```bash
   python manage.py runserver
   ```

---

### 2️⃣ CONFIGURAR WEBHOOK NO PAINEL DO MERCADO PAGO

Você já está na página de Webhooks! Siga estes passos:

#### Passo 2.1: Configurar URL do Webhook

Na seção **"URL de produção"**, adicione:

**Para Produção (recomendado):**
```
https://monpec.com.br/assinaturas/webhook/mercadopago/
```

**Para Teste Local (usando ngrok):**
```
https://seu-ngrok-url.ngrok.io/assinaturas/webhook/mercadopago/
```

#### Passo 2.2: Marcar Eventos Importantes

✅ **Marque estes eventos:**

**Na seção "Eventos recomendados":**
- ✅ **Pagamentos** (Payments) - **ESSENCIAL!**
- ✅ Alertas de fraude (opcional)
- ✅ Contestações (opcional)

**Na seção "Outros eventos":**
- ✅ **Planos e assinaturas** (Plans and subscriptions) - **ESSENCIAL!**

#### Passo 2.3: Salvar

Clique em **"Salvar"** ou **"Atualizar"** para salvar as configurações.

---

### 3️⃣ TESTAR

1. Acesse: `http://localhost:8000/assinaturas/`
2. Clique em **"Assinar Agora"** ou **"Aproveitar Oferta Agora"**
3. Você deve ser redirecionado para o Mercado Pago! 🎉

---

## ⚠️ IMPORTANTE SOBRE WEBHOOKS

### Webhook não funciona com localhost

O Mercado Pago **não consegue acessar** `http://localhost:8000`. 

**Soluções:**

1. **Para Produção:** Use `https://monpec.com.br/assinaturas/webhook/mercadopago/`

2. **Para Teste Local:** Use ngrok:
   ```bash
   # Instalar ngrok (se não tiver)
   # Baixe em: https://ngrok.com/download
   
   # Executar ngrok
   ngrok http 8000
   
   # Use a URL que aparecer (ex: https://abc123.ngrok.io)
   # Configure no webhook: https://abc123.ngrok.io/assinaturas/webhook/mercadopago/
   ```

---

## ✅ CHECKLIST RÁPIDO

- [x] Credenciais adicionadas ao `.env`
- [ ] **Servidor Django reiniciado** ⬅️ FAÇA ISSO AGORA!
- [ ] URL do webhook configurada no painel
- [ ] Eventos "Pagamentos" e "Planos e assinaturas" marcados
- [ ] Webhook salvo no painel
- [ ] Teste de checkout realizado

---

## 🚀 PRÓXIMOS PASSOS

1. **Reinicie o servidor Django** (Ctrl+C e depois `python manage.py runserver`)
2. **Configure o webhook** na página que você já está vendo
3. **Teste** clicando em "Assinar Agora"

---

## 📞 PRECISA DE AJUDA?

Se algo não funcionar:
1. Verifique o console do Django para erros
2. Verifique se o arquivo `.env` está na raiz do projeto
3. Verifique se reiniciou o servidor após criar o `.env`
4. Consulte o arquivo `CONFIGURAR_MERCADO_PAGO_COMPLETO.md` para mais detalhes

---

**🎉 Depois de configurar, o sistema estará funcionando completamente!**

