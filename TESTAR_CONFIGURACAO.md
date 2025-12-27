# ✅ TESTAR CONFIGURAÇÃO DO MERCADO PAGO

## 🎉 Configuração Concluída!

Você já configurou:
- ✅ Credenciais no arquivo `.env`
- ✅ Webhook no painel do Mercado Pago
- ✅ Eventos "Pagamentos" e "Planos e assinaturas" marcados

---

## 📋 PRÓXIMOS PASSOS

### 1️⃣ REINICIAR O SERVIDOR DJANGO

**IMPORTANTE:** O servidor precisa ser reiniciado para carregar as credenciais do `.env`!

1. Vá no terminal onde o Django está rodando
2. Pressione `Ctrl+C` para parar
3. Inicie novamente:
   ```bash
   python manage.py runserver
   ```

---

### 2️⃣ TESTAR O CHECKOUT

1. Acesse: `http://localhost:8000/assinaturas/`
2. Clique em **"Assinar Agora"** ou **"Aproveitar Oferta Agora"**
3. Você deve ser redirecionado para o Mercado Pago! 🎉

**Se funcionar:**
- ✅ Você verá a página de pagamento do Mercado Pago
- ✅ Pode testar com cartão de teste (veja abaixo)

**Se não funcionar:**
- Verifique o console do Django para erros
- Verifique se reiniciou o servidor
- Verifique se o arquivo `.env` está na raiz do projeto

---

### 3️⃣ TESTAR COM CARTÃO DE TESTE

Para testar sem usar dinheiro real, use estes cartões de teste:

**Cartão Aprovado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Data: Qualquer data futura (ex: `12/25`)
- Nome: Qualquer nome
- CPF: Qualquer CPF válido

**Cartão Recusado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Data: Qualquer data futura

---

### 4️⃣ VERIFICAR WEBHOOK (Após Pagamento)

Após um pagamento de teste:

1. No painel do Mercado Pago, vá em **"Webhooks"**
2. Você verá os eventos recebidos
3. No console do Django, você verá logs do webhook sendo processado

---

## 🔍 O QUE ESPERAR

### No Console do Django:

Quando clicar em "Assinar Agora", você deve ver:
```
✅ Criando preferência no Mercado Pago para plano...
✅ Preferência criada: id=..., url=...
```

Quando o pagamento for confirmado, você verá:
```
✅ Webhook recebido: payment
✅ Assinatura ativada para usuário...
✅ Email de confirmação enviado
```

### No Sistema:

Após pagamento confirmado:
1. Usuário é redirecionado para página de confirmação
2. Email é enviado com credenciais (Monpec2025@)
3. Assinatura fica ativa
4. Email e telefone são confirmados automaticamente

---

## ⚠️ SOBRE A "ASSINATURA SECRETA"

Você viu o campo "Assinatura secreta" no painel. Isso é opcional, mas recomendado para segurança:

**Para usar (opcional):**
1. Clique no ícone de "refresh" ao lado do campo
2. Copie a assinatura secreta gerada
3. Adicione no arquivo `.env`:
   ```env
   MERCADOPAGO_WEBHOOK_SECRET=sua_assinatura_secreta_aqui
   ```

**Se não configurar:**
- O sistema ainda funcionará
- Mas é menos seguro (qualquer um pode enviar webhooks falsos)

---

## ✅ CHECKLIST FINAL

- [x] Credenciais no `.env`
- [x] Webhook configurado
- [x] Eventos marcados
- [ ] **Servidor Django reiniciado** ⬅️ FAÇA ISSO AGORA!
- [ ] Teste de checkout realizado
- [ ] Teste com cartão de teste realizado

---

## 🚀 PRONTO PARA TESTAR!

1. **Reinicie o servidor Django**
2. **Acesse** `http://localhost:8000/assinaturas/`
3. **Clique** em "Assinar Agora"
4. **Teste** com cartão de teste

**Tudo deve funcionar perfeitamente agora!** 🎉

