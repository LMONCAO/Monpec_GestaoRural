# Configuração dos Botões de Pagamento - Mercado Pago

## Como Funciona

Os botões **"Aproveitar Oferta Agora"** e **"Assinar Agora"** já estão configurados para redirecionar automaticamente para o Mercado Pago e processar o pagamento.

## Fluxo de Pagamento

1. **Usuário clica no botão** → JavaScript captura o clique
2. **Requisição ao backend** → Cria sessão de checkout no Mercado Pago
3. **Redirecionamento** → Usuário é enviado para a página de pagamento do Mercado Pago
4. **Pagamento** → Usuário insere dados do cartão no Mercado Pago
5. **Retorno** → Após pagamento, usuário retorna para o sistema

## Configuração Necessária

### 1. Configurar Credenciais do Mercado Pago

Adicione as seguintes variáveis no arquivo `.env`:

```env
# Credenciais do Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu_access_token_aqui
MERCADOPAGO_PUBLIC_KEY=sua_public_key_aqui

# URLs de retorno (opcional - já configuradas por padrão)
MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/

# Gateway padrão
PAYMENT_GATEWAY_DEFAULT=mercadopago
```

### 2. Obter Credenciais do Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers
2. Faça login na sua conta
3. Vá em **"Suas integrações"**
4. Crie uma nova aplicação ou use uma existente
5. Copie o **Access Token** e a **Public Key**

**Para Testes:**
- Use as credenciais de **teste** (sandbox)
- Cartões de teste: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/additional-content/test-cards

### 3. Configurar Webhook (Opcional mas Recomendado)

O webhook permite que o Mercado Pago notifique o sistema quando um pagamento for confirmado.

1. No painel do Mercado Pago, configure a URL do webhook:
   ```
   https://seudominio.com/assinaturas/webhook/mercadopago/
   ```

2. Configure a variável no `.env`:
   ```env
   MERCADOPAGO_WEBHOOK_SECRET=seu_webhook_secret_aqui
   ```

## Como Testar

### 1. Verificar Configuração

Acesse a página de assinaturas:
```
http://localhost:8000/assinaturas/
```

Se as credenciais estiverem configuradas, o alerta amarelo não aparecerá e os botões estarão habilitados.

### 2. Testar o Fluxo

1. Clique em **"Aproveitar Oferta Agora"** ou **"Assinar Agora"**
2. O botão mostrará "Processando..."
3. Você será redirecionado para a página do Mercado Pago
4. Use um cartão de teste para completar o pagamento
5. Após o pagamento, você será redirecionado de volta para o sistema

### 3. Cartões de Teste

**Cartão Aprovado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Nome: Qualquer nome
- Data: Qualquer data futura

**Cartão Recusado:**
- Número: `5031 4332 1540 6352`
- CVV: `123`

## Estrutura do Código

### Frontend (JavaScript)

O JavaScript já está configurado no template `assinaturas_dashboard.html`:

```javascript
// Captura cliques em botões com classe 'iniciar-checkout'
buttons.forEach((btn) => {
    btn.addEventListener('click', async () => {
        // Envia requisição POST para o backend
        const response = await fetch(checkoutUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        });
        
        // Redireciona para URL do Mercado Pago
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        }
    });
});
```

### Backend (Django)

A view `iniciar_checkout` em `gestao_rural/views_assinaturas.py`:

1. Valida o usuário e o plano
2. Cria/atualiza a assinatura
3. Chama o gateway do Mercado Pago
4. Retorna a URL de checkout

### Gateway (Mercado Pago)

O gateway em `gestao_rural/services/payments/mercadopago_gateway.py`:

1. Cria um plano de assinatura (se não existir)
2. Cria uma preferência de pagamento
3. Retorna a URL do checkout

## Troubleshooting

### Botões Desabilitados

**Problema:** Botões aparecem desabilitados (cinza)

**Solução:** 
- Verifique se `MERCADOPAGO_PUBLIC_KEY` está configurado no `.env`
- Reinicie o servidor Django após adicionar as variáveis

### Erro ao Clicar no Botão

**Problema:** Mensagem de erro ao clicar

**Soluções:**
1. Verifique se `MERCADOPAGO_ACCESS_TOKEN` está configurado
2. Verifique os logs do servidor para mais detalhes
3. Confirme que o plano existe no banco de dados

### Não Redireciona para Mercado Pago

**Problema:** Botão processa mas não redireciona

**Soluções:**
1. Abra o console do navegador (F12) e verifique erros
2. Verifique se a resposta do backend contém `checkout_url`
3. Verifique se as credenciais do Mercado Pago estão corretas

### Pagamento Não é Confirmado

**Problema:** Pagamento feito mas não aparece como confirmado

**Soluções:**
1. Configure o webhook do Mercado Pago
2. Verifique se a URL do webhook está acessível publicamente
3. Verifique os logs do webhook em `gestao_rural/views_assinaturas.py`

## Próximos Passos

1. ✅ Configurar credenciais no `.env`
2. ✅ Testar com cartões de teste
3. ✅ Configurar webhook para produção
4. ✅ Testar fluxo completo em produção

## Suporte

Para mais informações sobre a API do Mercado Pago:
- Documentação: https://www.mercadopago.com.br/developers/pt/docs
- Suporte: https://www.mercadopago.com.br/developers/pt/support





























