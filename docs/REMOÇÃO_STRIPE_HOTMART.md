# Remoção de Stripe e Hotmart

## ✅ Concluído

Stripe e Hotmart foram removidos do projeto para evitar conflitos. O sistema agora usa **apenas Mercado Pago** como gateway de pagamento.

## 📋 O que foi removido

### 1. Configurações (settings.py)
- ❌ `STRIPE_SECRET_KEY`
- ❌ `STRIPE_PUBLISHABLE_KEY`
- ❌ `STRIPE_WEBHOOK_SECRET`
- ❌ `STRIPE_SUCCESS_URL`
- ❌ `STRIPE_CANCEL_URL`
- ❌ `STRIPE_ALERT_EMAILS`
- ❌ `HOTMART_CHECKOUT_URL`

### 2. Arquivos
- ❌ `gestao_rural/services/stripe_client.py` (arquivo antigo removido)

### 3. Código
- ❌ Import de `stripe_client` em `views_assinaturas.py`
- ❌ Função `stripe_webhook` (agora retorna erro informando que foi removido)
- ❌ Handlers do Stripe (`_handle_checkout_completed`, `_handle_subscription_event`, etc.)
- ❌ Registro do gateway Stripe no factory
- ❌ URL do webhook do Stripe (`/assinaturas/webhook/`)

### 4. Templates
- ❌ Referências ao Stripe em `assinaturas_dashboard.html`
- ❌ Links do Hotmart em `promo_whatsapp.html`

### 5. Admin
- ❌ Campos do Stripe no admin de `PlanoAssinatura`
- ❌ Campos do Stripe no admin de `AssinaturaCliente`
- ✅ Atualizado para mostrar campos do Mercado Pago

### 6. Serviços
- ❌ Referências a `STRIPE_ALERT_EMAILS` em `notificacoes.py`

## ✅ O que foi atualizado

### 1. Gateway Padrão
- ✅ `PAYMENT_GATEWAY_DEFAULT` agora é `'mercadopago'` por padrão

### 2. Views
- ✅ `assinaturas_dashboard` agora usa apenas Mercado Pago
- ✅ `iniciar_checkout` usa apenas Mercado Pago
- ✅ Webhook do Mercado Pago funcionando

### 3. Factory
- ✅ Removido registro do Stripe
- ✅ Apenas Mercado Pago registrado

### 4. Templates
- ✅ `assinaturas_dashboard.html` atualizado para Mercado Pago
- ✅ `promo_whatsapp.html` atualizado para usar página de assinaturas

### 5. Admin
- ✅ Campos do Mercado Pago adicionados
- ✅ Interface atualizada

## 🔄 Migrações Necessárias

Os campos do Stripe ainda existem no banco de dados (para não perder dados históricos), mas não são mais usados. Os novos campos do Mercado Pago foram adicionados.

**Execute as migrações:**
```bash
python manage.py makemigrations gestao_rural
python manage.py migrate gestao_rural
```

Ou use o arquivo:
```bash
APLICAR_MIGRACOES_MERCADOPAGO.bat
```

## 📝 Notas Importantes

1. **Dados Históricos**: Os campos do Stripe foram mantidos no modelo para não perder dados históricos, mas não são mais usados.

2. **Webhook do Stripe**: A URL `/assinaturas/webhook/` agora retorna um erro informando que o Stripe foi removido. Use apenas `/assinaturas/webhook/mercadopago/`.

3. **Gateway Único**: O sistema agora usa apenas Mercado Pago. Se precisar de outro gateway no futuro, use a estrutura modular criada em `gestao_rural/services/payments/`.

4. **Configuração**: Certifique-se de ter configurado:
   - `MERCADOPAGO_ACCESS_TOKEN`
   - `MERCADOPAGO_PUBLIC_KEY`
   - `PAYMENT_GATEWAY_DEFAULT=mercadopago`

## 🚀 Próximos Passos

1. ✅ Executar migrações
2. ✅ Configurar credenciais do Mercado Pago
3. ✅ Testar checkout
4. ✅ Configurar webhook do Mercado Pago

## 📚 Documentação Relacionada

- `docs/CONFIGURACAO_MERCADOPAGO.md` - Como configurar Mercado Pago
- `docs/GUIA_RAPIDO_MERCADOPAGO.md` - Guia rápido de configuração
- `PROXIMOS_PASSOS_MERCADOPAGO.md` - Próximos passos





























