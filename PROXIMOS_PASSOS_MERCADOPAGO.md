# ✅ Próximos Passos - Integração Mercado Pago

## 🎯 Status Atual

✅ **Código implementado e pronto!**
- Gateway Mercado Pago criado
- Views atualizadas
- Modelos atualizados
- URLs configuradas
- Documentação criada

## 🚀 Ações Imediatas (Faça Agora)

### 1. Instalar Dependência

```bash
pip install mercadopago>=2.2.0
```

### 2. Configurar Credenciais

Crie/edite o arquivo `.env` na raiz do projeto:

```bash
# Gateway padrão
PAYMENT_GATEWAY_DEFAULT=mercadopago

# Credenciais do Mercado Pago (obtenha no painel)
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxxxxxxx-xxxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxxxxxxx-xxxxxxxxxxxxx

# URLs (ajuste conforme necessário)
SITE_URL=http://localhost:8000
MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/
```

**📝 Onde obter as credenciais:**
1. Acesse: https://www.mercadopago.com.br/developers/panel/app/7331944463149248
2. Clique em **"Ver Credenciais"**
3. Copie o **Access Token** e **Public Key** (use as de TESTE primeiro!)

### 3. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Testar Configuração

```bash
python manage.py testar_mercadopago
```

Este comando vai verificar se:
- ✅ Credenciais estão configuradas
- ✅ Gateway pode ser criado
- ✅ Conexão com API funciona

## 🧪 Testar a Integração

### Passo 1: Iniciar Servidor

```bash
python manage.py runserver
```

### Passo 2: Acessar Página de Assinaturas

Abra no navegador:
```
http://localhost:8000/assinaturas/
```

### Passo 3: Testar Checkout

1. Selecione um plano
2. Clique em "Assinar"
3. Você será redirecionado para o Mercado Pago
4. Use um cartão de teste:
   - **Número:** `5031 4332 1540 6351`
   - **CVV:** `123`
   - **Validade:** Qualquer data futura (ex: `11/25`)

### Passo 4: Verificar Resultado

Após o pagamento, verifique:
- ✅ Assinatura criada no banco de dados
- ✅ Status atualizado corretamente
- ✅ Workspace provisionado (se aplicável)

## 🔧 Configurar Webhook (Opcional para testes)

Para receber notificações automáticas:

### Opção 1: Usar ngrok (testes locais)

```bash
# Instalar ngrok
# Windows: choco install ngrok
# Mac: brew install ngrok
# Linux: baixar de https://ngrok.com/

# Iniciar ngrok
ngrok http 8000

# Use a URL gerada (ex: https://xxxxx.ngrok.io)
```

No painel do Mercado Pago:
1. Vá em **"Webhooks"**
2. Adicione: `https://xxxxx.ngrok.io/assinaturas/webhook/mercadopago/`
3. Selecione eventos: `payment`, `subscription`, `preapproval`

### Opção 2: Configurar em produção

Quando estiver em produção:
1. Configure a URL: `https://seudominio.com.br/assinaturas/webhook/mercadopago/`
2. Certifique-se de que a URL está acessível publicamente

## 📋 Checklist Final

Antes de considerar completo:

- [ ] Dependência `mercadopago` instalada
- [ ] Credenciais configuradas no `.env`
- [ ] Migrações executadas
- [ ] Comando de teste passou (`testar_mercadopago`)
- [ ] Checkout funciona no navegador
- [ ] Pagamento de teste completo
- [ ] Assinatura criada no banco
- [ ] Webhook configurado (opcional)

## 🐛 Problemas Comuns

### "MERCADOPAGO_ACCESS_TOKEN não configurado"
- Verifique se o `.env` está na raiz do projeto
- Reinicie o servidor após alterar `.env`

### "Erro ao criar checkout"
- Verifique se o Access Token está correto
- Certifique-se de usar credenciais de TESTE em desenvolvimento

### Webhook não funciona
- Use ngrok para testes locais
- Verifique se a URL está acessível publicamente

## 📚 Documentação

- **Guia Rápido:** `docs/GUIA_RAPIDO_MERCADOPAGO.md`
- **Configuração Completa:** `docs/CONFIGURACAO_MERCADOPAGO.md`
- **Resumo Técnico:** `docs/RESUMO_INTEGRACAO_MERCADOPAGO.md`

## 🎉 Pronto!

Sua integração está implementada e pronta para uso. Siga os passos acima para configurar e testar!

**Dúvidas?** Consulte a documentação ou os logs do servidor.






















