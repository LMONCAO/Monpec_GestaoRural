# Fluxo Completo de Assinatura e Liberação de Acesso

## 📋 Visão Geral

O sistema implementa um fluxo completo de assinatura com controle de data de liberação:

1. **Usuário clica em "Assinar agora"** → Redirecionado para Mercado Pago
2. **Usuário paga no Mercado Pago** → Pagamento processado
3. **Webhook recebe confirmação** → Sistema valida pagamento
4. **Acesso liberado** → Mas apenas a partir de **01/02/2026**

## 🔄 Fluxo Detalhado

### 1. Início do Checkout

**Arquivo:** `templates/gestao_rural/assinaturas_dashboard.html`

- Usuário clica em "Assinar agora"
- JavaScript faz requisição POST para `/assinaturas/plano/<slug>/checkout/`
- View `iniciar_checkout` cria sessão no Mercado Pago
- Usuário é **redirecionado para o checkout do Mercado Pago**

### 2. Pagamento no Mercado Pago

- Usuário completa o pagamento (cartão, PIX, boleto)
- Mercado Pago processa o pagamento
- Usuário é redirecionado de volta para `/assinaturas/sucesso/`

### 3. Validação via Webhook

**Arquivo:** `gestao_rural/views_assinaturas.py` → `mercadopago_webhook`

- Mercado Pago envia notificação para `/assinaturas/webhook/mercadopago/`
- Sistema processa o evento
- Se pagamento aprovado:
  - Status da assinatura → `ATIVA`
  - **Data de liberação → `01/02/2026`**
  - Workspace provisionado
  - E-mail enviado ao usuário

### 4. Controle de Acesso

**Arquivo:** `gestao_rural/middleware_liberacao_acesso.py`

- Middleware verifica cada requisição
- Se usuário tem assinatura:
  - Verifica se `data_liberacao` chegou
  - Se não chegou → Redireciona para página de assinaturas com mensagem
  - Se chegou → Permite acesso normal

## 📅 Data de Liberação

**Data fixa:** `01/02/2026`

Esta data é definida automaticamente quando:
- Pagamento é confirmado via webhook
- Assinatura é ativada

**Onde é definida:**
- `gestao_rural/services/payments/mercadopago_gateway.py` → `_processar_pagamento()`
- `gestao_rural/services/payments/mercadopago_gateway.py` → `_processar_assinatura()`
- `gestao_rural/views_assinaturas.py` → `mercadopago_webhook()`

## 🔒 Controle de Acesso

### Middleware de Liberação

O middleware `LiberacaoAcessoMiddleware` verifica:

1. **URLs públicas** → Sempre permitidas (login, logout, assinaturas, etc.)
2. **Superusuários/Staff** → Sempre têm acesso
3. **Usuários sem assinatura** → Redirecionados para página de assinaturas
4. **Usuários com assinatura** → Verifica `data_liberacao`

### Propriedade `acesso_liberado`

No modelo `AssinaturaCliente`:

```python
@property
def acesso_liberado(self) -> bool:
    if not self.data_liberacao:
        return self.status == self.Status.ATIVA
    
    hoje = timezone.now().date()
    return self.status == self.Status.ATIVA and hoje >= self.data_liberacao
```

## 📧 Notificações

Quando o pagamento é confirmado, o usuário recebe um e-mail informando:
- Pagamento confirmado
- Data de liberação: 01/02/2026
- Quando o acesso estará disponível

## 🧪 Testando o Fluxo

### 1. Testar Checkout

```bash
# Acessar página de assinaturas
http://localhost:8000/assinaturas/

# Clicar em "Assinar agora"
# Deve redirecionar para Mercado Pago
```

### 2. Testar Webhook (Simulação)

```python
# No shell do Django
from gestao_rural.models import AssinaturaCliente
from datetime import date

assinatura = AssinaturaCliente.objects.get(usuario__username='demo')
assinatura.status = AssinaturaCliente.Status.ATIVA
assinatura.data_liberacao = date(2026, 2, 1)
assinatura.save()

# Verificar acesso
print(assinatura.acesso_liberado)  # False (se hoje < 01/02/2026)
```

### 3. Testar Middleware

- Fazer login com usuário que tem assinatura
- Se `data_liberacao` > hoje → Redirecionado para `/assinaturas/`
- Se `data_liberacao` <= hoje → Acesso permitido

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
MERCADOPAGO_ACCESS_TOKEN=seu_token
MERCADOPAGO_PUBLIC_KEY=sua_public_key
PAYMENT_GATEWAY_DEFAULT=mercadopago
```

### Webhook do Mercado Pago

Configure no painel do Mercado Pago:
- URL: `https://seudominio.com.br/assinaturas/webhook/mercadopago/`
- Eventos: `payment`, `subscription`, `preapproval`

## 📝 Alterar Data de Liberação

Para mudar a data de liberação, edite:

1. `gestao_rural/services/payments/mercadopago_gateway.py`
   - Linha ~248: `assinatura.data_liberacao = date(2026, 2, 1)`
   - Linha ~280: `assinatura.data_liberacao = date(2026, 2, 1)`

2. `gestao_rural/views_assinaturas.py`
   - Linha ~220: `assinatura.data_liberacao = date(2026, 2, 1)`

## ✅ Checklist

- [x] Redirecionamento para Mercado Pago funcionando
- [x] Webhook processando pagamentos
- [x] Data de liberação definida automaticamente
- [x] Middleware bloqueando acesso antes da data
- [x] Mensagens informativas para o usuário
- [x] E-mails de notificação

## 🎯 Resultado Final

1. ✅ Usuário clica em "Assinar agora" → Redirecionado para Mercado Pago
2. ✅ Usuário paga → Webhook valida pagamento
3. ✅ Sistema define `data_liberacao = 01/02/2026`
4. ✅ Middleware bloqueia acesso até 01/02/2026
5. ✅ Após 01/02/2026, acesso liberado automaticamente





























