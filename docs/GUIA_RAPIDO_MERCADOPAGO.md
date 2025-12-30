# 🚀 Guia Rápido - Configuração Mercado Pago

## 📋 Informações da Sua Aplicação

- **User ID:** `2581972940`
- **Número da Aplicação:** `7331944463149248`
- **Tipo de Integração:** Assinaturas

## ⚡ Configuração Rápida (5 minutos)

### 1. Obter Credenciais

1. No painel do Mercado Pago, clique em **"Ver Credenciais"**
2. Você verá duas seções:
   - **Credenciais de Teste** (para desenvolvimento)
   - **Credenciais de Produção** (para quando estiver pronto)

### 2. Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env` na raiz do projeto:

```bash
# Gateway padrão
PAYMENT_GATEWAY_DEFAULT=mercadopago

# Credenciais de TESTE (use estas primeiro!)
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxxxxxxx-xxxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxxxxxxx-xxxxxxxxxxxxx

# URLs de retorno (ajuste para seu ambiente)
MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/

# Site URL (para webhooks)
SITE_URL=http://localhost:8000
```

**⚠️ IMPORTANTE:**
- Use credenciais de **TESTE** durante desenvolvimento
- Troque para **PRODUÇÃO** apenas quando for lançar

### 3. Instalar Dependências

```bash
pip install mercadopago>=2.2.0
```

Ou instale todas as dependências:

```bash
pip install -r requirements.txt
```

### 4. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Configurar Webhook (Opcional para testes locais)

Para testes locais, você pode usar o ngrok ou configurar depois:

1. No painel do Mercado Pago, vá em **"Webhooks"**
2. Adicione a URL: `https://seudominio.com.br/assinaturas/webhook/mercadopago/`
3. Selecione os eventos:
   - ✅ `payment`
   - ✅ `subscription`
   - ✅ `preapproval`

**Para testes locais com ngrok:**
```bash
ngrok http 8000
# Use a URL do ngrok: https://xxxxx.ngrok.io/assinaturas/webhook/mercadopago/
```

## 🧪 Testar a Integração

### Passo 1: Criar Contas de Teste

No painel do Mercado Pago:
1. Vá em **"Contas de teste"**
2. Crie uma conta **Vendedor** (se ainda não tiver)
3. Crie uma conta **Comprador** (para testar pagamentos)

### Passo 2: Usar Cartões de Teste

Para testar pagamentos, use estes cartões:

**Cartão Aprovado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Validade: Qualquer data futura (ex: `11/25`)
- Nome: Qualquer nome

**Cartão Recusado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Validade: Qualquer data futura

### Passo 3: Testar no Sistema

1. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

2. Acesse: `http://localhost:8000/assinaturas/`

3. Selecione um plano e clique em "Assinar"

4. Você será redirecionado para o checkout do Mercado Pago

5. Use um cartão de teste para completar o pagamento

6. Verifique se a assinatura foi criada corretamente

## 🔍 Verificar se Está Funcionando

### Checklist:

- [ ] Credenciais configuradas no `.env`
- [ ] Dependências instaladas (`mercadopago`)
- [ ] Migrações executadas
- [ ] Servidor rodando
- [ ] Página de assinaturas acessível
- [ ] Checkout do Mercado Pago aparece
- [ ] Pagamento de teste funciona
- [ ] Assinatura criada no banco de dados

### Verificar no Banco de Dados:

```python
# No shell do Django
python manage.py shell

from gestao_rural.models import AssinaturaCliente

# Ver assinaturas
assinaturas = AssinaturaCliente.objects.all()
for a in assinaturas:
    print(f"{a.usuario} - {a.status} - Gateway: {a.gateway_pagamento}")
```

## 🐛 Troubleshooting

### Erro: "MERCADOPAGO_ACCESS_TOKEN não configurado"

**Solução:**
- Verifique se o `.env` está na raiz do projeto
- Verifique se as variáveis estão escritas corretamente
- Reinicie o servidor após alterar o `.env`

### Erro: "Erro ao criar checkout"

**Solução:**
- Verifique se o Access Token está correto
- Certifique-se de estar usando credenciais de TESTE em desenvolvimento
- Verifique os logs do servidor para mais detalhes

### Webhook não funciona

**Solução:**
- Para testes locais, use ngrok
- Verifique se a URL está acessível publicamente
- Verifique se os eventos estão configurados no painel

### Assinatura não atualiza após pagamento

**Solução:**
- Verifique se o webhook está configurado
- Verifique os logs do servidor
- Teste manualmente o webhook (veja documentação do Mercado Pago)

## 📚 Próximos Passos

1. ✅ **Testar em ambiente de desenvolvimento**
2. ⏭️ **Configurar webhook em produção**
3. ⏭️ **Trocar para credenciais de produção**
4. ⏭️ **Configurar planos de assinatura**
5. ⏭️ **Testar fluxo completo**

## 🔗 Links Úteis

- **Painel de Desenvolvedores:** https://www.mercadopago.com.br/developers/panel/app/7331944463149248
- **Documentação de Assinaturas:** https://www.mercadopago.com.br/developers/pt/docs/subscriptions
- **Cartões de Teste:** https://www.mercadopago.com.br/developers/pt/docs/checkout-api/testing
- **Webhooks:** https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks

## 💡 Dicas

1. **Sempre teste primeiro** com credenciais de teste
2. **Use ngrok** para testar webhooks localmente
3. **Monitore os logs** do servidor durante testes
4. **Verifique o painel** do Mercado Pago para ver os pagamentos
5. **Documente** qualquer problema encontrado

---

**Pronto para começar!** 🎉

Se tiver dúvidas, consulte `docs/CONFIGURACAO_MERCADOPAGO.md` para mais detalhes.





























