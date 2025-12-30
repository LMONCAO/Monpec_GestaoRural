# 🔧 Como Configurar o Mercado Pago

## ⚠️ Problema

Se você está vendo o erro:
```
MERCADOPAGO_ACCESS_TOKEN não configurado
```

Isso significa que o token de acesso do Mercado Pago não está configurado no sistema.

## 📋 Passo a Passo

### 1. Obter o Access Token do Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Faça login na sua conta do Mercado Pago
3. Clique em "Suas integrações"
4. Crie uma nova aplicação ou selecione uma existente
5. Na seção "Credenciais de teste" ou "Credenciais de produção", copie o **Access Token**

### 2. Configurar no Projeto

#### Opção A: Criar arquivo `.env` (Recomendado)

1. Na raiz do projeto, crie um arquivo chamado `.env`
2. Adicione as seguintes linhas:

```env
# Configurações do Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu_access_token_aqui
MERCADOPAGO_PUBLIC_KEY=sua_public_key_aqui
MERCADOPAGO_WEBHOOK_SECRET=seu_webhook_secret_aqui

# URLs de retorno
MERCADOPAGO_SUCCESS_URL=http://localhost:8000/assinaturas/sucesso/
MERCADOPAGO_CANCEL_URL=http://localhost:8000/assinaturas/cancelado/

# Gateway padrão
PAYMENT_GATEWAY_DEFAULT=mercadopago
```

3. Substitua `seu_access_token_aqui` pelo token que você copiou
4. Salve o arquivo

#### Opção B: Configurar variáveis de ambiente do sistema

**Windows (PowerShell):**
```powershell
$env:MERCADOPAGO_ACCESS_TOKEN="seu_access_token_aqui"
$env:MERCADOPAGO_PUBLIC_KEY="sua_public_key_aqui"
```

**Linux/Mac:**
```bash
export MERCADOPAGO_ACCESS_TOKEN="seu_access_token_aqui"
export MERCADOPAGO_PUBLIC_KEY="sua_public_key_aqui"
```

### 3. Reiniciar o Servidor

Após configurar, **reinicie o servidor Django** para que as variáveis sejam carregadas:

```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente
python manage.py runserver
```

## 🧪 Testar

1. Acesse: http://localhost:8000/assinaturas/
2. Clique em "Assinar Agora" ou "Aproveitar Oferta Agora"
3. Se estiver configurado corretamente, você será redirecionado para a página de pagamento do Mercado Pago

## 📝 Notas Importantes

- **Token de Teste**: Use tokens de teste durante desenvolvimento
- **Token de Produção**: Use tokens de produção apenas em ambiente de produção
- **Segurança**: Nunca compartilhe seu Access Token ou commite o arquivo `.env` no Git
- **Webhook**: Configure a URL do webhook no painel do Mercado Pago:
  - URL: `http://seu-dominio.com/assinaturas/webhook/mercadopago/`

## ❓ Problemas Comuns

### Erro: "Token inválido"
- Verifique se copiou o token completo
- Certifique-se de que não há espaços extras
- Verifique se está usando o token correto (teste vs produção)

### Erro: "Não foi possível conectar"
- Verifique sua conexão com a internet
- Certifique-se de que o servidor Django está rodando
- Verifique se a URL está correta

### O arquivo .env não está sendo lido
- Certifique-se de que o arquivo está na raiz do projeto
- Verifique se o nome do arquivo é exatamente `.env` (sem extensão)
- Reinicie o servidor após criar/modificar o arquivo

## 🔗 Links Úteis

- [Painel de Desenvolvedores do Mercado Pago](https://www.mercadopago.com.br/developers/panel)
- [Documentação da API do Mercado Pago](https://www.mercadopago.com.br/developers/pt/docs)
- [Como obter credenciais](https://www.mercadopago.com.br/developers/pt/docs/your-integrations/credentials)








