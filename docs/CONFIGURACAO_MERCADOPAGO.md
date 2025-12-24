# Configuração do Mercado Pago

## Visão Geral

Este guia explica como configurar a integração com Mercado Pago no sistema de assinaturas.

## Pré-requisitos

1. Conta no Mercado Pago (https://www.mercadopago.com.br/)
2. Aplicação criada no Mercado Pago (para obter Access Token)
3. Python SDK do Mercado Pago instalado (`pip install mercadopago`)

## Passo 1: Criar Aplicação no Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Clique em "Criar aplicação"
3. Preencha os dados da aplicação
4. Após criar, você terá acesso ao:
   - **Access Token** (chave secreta)
   - **Public Key** (chave pública)

## Passo 2: Configurar Variáveis de Ambiente

Adicione as seguintes variáveis no seu arquivo `.env` ou nas variáveis de ambiente:

```bash
# Gateway padrão (mercadopago ou stripe)
PAYMENT_GATEWAY_DEFAULT=mercadopago

# Credenciais do Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxxxxxxxxxx-xxxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxxxxxxxxxx-xxxxxxxxxxxxx

# URLs de retorno (opcional, usa padrão se não configurado)
MERCADOPAGO_SUCCESS_URL=https://seudominio.com.br/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=https://seudominio.com.br/assinaturas/cancelado/
```

### Ambiente de Teste (Sandbox)

Para testes, use as credenciais de teste:

1. Acesse: https://www.mercadopago.com.br/developers/panel/credentials
2. Use as credenciais de **Teste**
3. Para testar pagamentos, use os cartões de teste:
   - Aprovado: 5031 4332 1540 6351 (CVV: 123)
   - Recusado: 5031 4332 1540 6351 (CVV: 123)

## Passo 3: Configurar Webhook

O Mercado Pago enviará notificações para o seu sistema quando houver eventos de pagamento.

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Selecione sua aplicação
3. Vá em "Webhooks"
4. Adicione a URL: `https://seudominio.com.br/assinaturas/webhook/mercadopago/`
5. Selecione os eventos:
   - `payment`
   - `subscription`
   - `preapproval`

## Passo 4: Executar Migrações

Após adicionar os novos campos no modelo, execute:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Passo 5: Configurar Planos

No admin do Django, configure os planos de assinatura:

1. Acesse: `/admin/gestao_rural/planoassinatura/`
2. Para cada plano:
   - Preencha o **Preço mensal de referência**
   - O sistema criará automaticamente o Preapproval no Mercado Pago na primeira compra
   - Ou configure manualmente o **Mercado Pago Preapproval ID** se já tiver criado

### Criar Plano Manualmente no Mercado Pago (Opcional)

Se preferir criar o plano manualmente:

1. Acesse a API do Mercado Pago
2. Crie um Preapproval (plano de assinatura)
3. Copie o ID gerado
4. Cole no campo **Mercado Pago Preapproval ID** do plano

## Passo 6: Testar Integração

### Teste de Checkout

1. Acesse a página de assinaturas
2. Selecione um plano
3. Clique em "Assinar"
4. Você será redirecionado para o checkout do Mercado Pago
5. Use um cartão de teste para completar o pagamento

### Teste de Webhook

O Mercado Pago enviará notificações automaticamente. Para testar manualmente:

1. Use a ferramenta de teste do Mercado Pago
2. Ou use o endpoint de notificação manual

## Estrutura de Dados

### AssinaturaCliente

Novos campos adicionados:
- `mercadopago_customer_id`: ID do cliente no Mercado Pago
- `mercadopago_subscription_id`: ID da assinatura no Mercado Pago
- `gateway_pagamento`: Gateway usado ('stripe', 'mercadopago', etc.)

### PlanoAssinatura

Novos campos adicionados:
- `mercadopago_preapproval_id`: ID do plano de assinatura no Mercado Pago
- `stripe_price_id`: Agora é opcional (não obrigatório se usar Mercado Pago)

## Fluxo de Pagamento

1. **Usuário seleciona plano** → View `iniciar_checkout`
2. **Sistema cria checkout** → Gateway cria sessão no Mercado Pago
3. **Usuário é redirecionado** → Checkout do Mercado Pago
4. **Usuário paga** → Mercado Pago processa pagamento
5. **Webhook recebe notificação** → Sistema atualiza assinatura
6. **Provisionamento** → Workspace é criado/atualizado

## Troubleshooting

### Erro: "MERCADOPAGO_ACCESS_TOKEN não configurado"

- Verifique se a variável de ambiente está definida
- Reinicie o servidor após definir a variável

### Erro: "Erro ao criar checkout"

- Verifique se o Access Token está correto
- Verifique se está usando credenciais de produção em produção
- Verifique os logs do Mercado Pago

### Webhook não está recebendo notificações

- Verifique se a URL está correta e acessível publicamente
- Verifique se o endpoint está configurado no Mercado Pago
- Verifique os logs do servidor

### Assinatura não está sendo atualizada

- Verifique se o webhook está processando corretamente
- Verifique se o `external_reference` está correto
- Verifique os logs de erro

## Suporte

Para mais informações:
- Documentação: https://www.mercadopago.com.br/developers/pt/docs
- Suporte: https://www.mercadopago.com.br/developers/pt/support



