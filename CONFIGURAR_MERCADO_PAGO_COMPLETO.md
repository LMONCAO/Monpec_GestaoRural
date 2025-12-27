# 🔧 Configuração Completa do Mercado Pago

## 📋 Passo 1: Configurar Credenciais no Arquivo .env

### 1.1. Criar/Atualizar arquivo .env

Na raiz do projeto, crie ou edite o arquivo `.env` e adicione:

```env
# ==========================================
# CONFIGURAÇÕES DO MERCADO PAGO
# ==========================================

# Credenciais de PRODUÇÃO (que você copiou do painel)
MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940
MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3

# Webhook Secret (opcional, mas recomendado para segurança)
MERCADOPAGO_WEBHOOK_SECRET=

# URLs de retorno após pagamento
MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/

# Gateway de pagamento padrão
PAYMENT_GATEWAY_DEFAULT=mercadopago
```

### 1.2. Para Produção

Se estiver em produção, altere as URLs:

```env
MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/
```

---

## 📋 Passo 2: Configurar Webhook no Painel do Mercado Pago

### 2.1. Acessar Configuração de Webhooks

1. No painel do Mercado Pago Developers, vá em **"NOTIFICAÇÕES"** → **"Webhooks"**
2. Selecione a aba **"Modo de produção"**

### 2.2. Configurar URL do Webhook

**Para Desenvolvimento (localhost):**
```
http://localhost:8000/assinaturas/webhook/mercadopago/
```

⚠️ **Nota:** O Mercado Pago não consegue acessar localhost. Para testar webhooks em desenvolvimento, você precisa usar uma ferramenta como ngrok ou configurar apenas em produção.

**Para Produção:**
```
https://monpec.com.br/assinaturas/webhook/mercadopago/
```

### 2.3. Selecionar Eventos

Marque os seguintes eventos (importantes para o sistema):

✅ **Eventos Recomendados:**
- ✅ **Pagamentos** (Payments) - **ESSENCIAL**
- ✅ Alertas de fraude (Fraud alerts)
- ✅ Contestações (Disputes)

✅ **Outros Eventos:**
- ✅ **Planos e assinaturas** (Plans and subscriptions) - **ESSENCIAL**

### 2.4. Salvar Configuração

Clique em **"Salvar"** ou **"Atualizar"** para salvar as configurações.

---

## 📋 Passo 3: Reiniciar o Servidor Django

Após configurar o arquivo `.env`, **reinicie o servidor Django**:

1. Pare o servidor (Ctrl+C no terminal)
2. Inicie novamente:
   ```bash
   python manage.py runserver
   ```

---

## 📋 Passo 4: Testar a Configuração

### 4.1. Testar Checkout

1. Acesse: `http://localhost:8000/assinaturas/`
2. Clique em **"Assinar Agora"** ou **"Aproveitar Oferta Agora"**
3. Você deve ser redirecionado para a página de pagamento do Mercado Pago

### 4.2. Testar Webhook (Produção)

O webhook será chamado automaticamente quando:
- Um pagamento for aprovado
- Um pagamento mudar de status
- Uma assinatura for criada/atualizada

---

## 🔍 Verificar se Está Funcionando

### Verificar no Console do Django

Quando clicar em "Assinar Agora", você deve ver no console:
```
✅ Criando preferência no Mercado Pago para plano...
✅ Preferência criada: id=..., url=...
```

### Verificar no Painel do Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Vá em **"Suas integrações"** → Sua aplicação
3. Clique em **"Webhooks"**
4. Você verá os eventos recebidos

---

## ⚠️ Problemas Comuns

### Erro: "MERCADOPAGO_ACCESS_TOKEN não configurado"

**Solução:**
- Verifique se o arquivo `.env` está na raiz do projeto
- Verifique se o nome é exatamente `.env` (sem extensão)
- Reinicie o servidor Django após criar/modificar o arquivo

### Webhook não está sendo chamado

**Soluções:**
1. Verifique se a URL do webhook está correta no painel
2. Verifique se o servidor está acessível (não funciona com localhost)
3. Use ngrok para testar localmente:
   ```bash
   ngrok http 8000
   ```
   Depois use a URL do ngrok no webhook

### Erro: "Token inválido"

**Solução:**
- Verifique se copiou o token completo
- Certifique-se de que não há espaços extras
- Use o token de PRODUÇÃO (não o de teste)

---

## 📝 Resumo das Credenciais

**Public Key:**
```
APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3
```

**Access Token:**
```
APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940
```

**URL do Webhook (Produção):**
```
https://monpec.com.br/assinaturas/webhook/mercadopago/
```

---

## ✅ Checklist Final

- [ ] Arquivo `.env` criado na raiz do projeto
- [ ] `MERCADOPAGO_ACCESS_TOKEN` configurado
- [ ] `MERCADOPAGO_PUBLIC_KEY` configurado
- [ ] URLs de sucesso/cancelamento configuradas
- [ ] Webhook configurado no painel do Mercado Pago
- [ ] Eventos "Pagamentos" e "Planos e assinaturas" marcados
- [ ] Servidor Django reiniciado
- [ ] Teste de checkout realizado com sucesso

---

## 🎉 Pronto!

Após seguir todos os passos, o sistema estará configurado e funcionando. Quando um usuário clicar em "Assinar Agora", será redirecionado para o Mercado Pago e, após o pagamento, o webhook confirmará automaticamente a assinatura.

