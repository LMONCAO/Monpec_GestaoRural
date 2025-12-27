# 🚀 Guia de Deploy para Produção - MONPEC

## ✅ Configurações Aplicadas

### 1. Credenciais do Mercado Pago
As credenciais do Mercado Pago foram configuradas no script de deploy:
- **Access Token**: Configurado
- **Public Key**: Configurado
- **URLs de Sucesso/Cancelamento**: Configuradas para `https://monpec.com.br`

### 2. Variáveis de Ambiente
O deploy configura automaticamente:
- `MERCADOPAGO_ACCESS_TOKEN`
- `MERCADOPAGO_PUBLIC_KEY`
- `MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/`
- `MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/`
- `PAYMENT_GATEWAY_DEFAULT=mercadopago`
- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- `DEBUG=False`

### 3. Webhook do Mercado Pago

**⚠️ IMPORTANTE: Configure o webhook no painel do Mercado Pago!**

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Vá em **Webhooks** ou **Notificações**
3. Adicione a URL:
   ```
   https://monpec.com.br/assinaturas/webhook/mercadopago/
   ```
4. Selecione os eventos:
   - `payment`
   - `subscription`
   - `preapproval`

## 📋 Como Executar o Deploy

### Opção 1: Script Simplificado (Recomendado)
```powershell
.\DEPLOY_AGORA_SIMPLES.ps1
```

### Opção 2: Script Completo
```powershell
.\DEPLOY_COMPLETO_CORRIGIDO.ps1
```

## 🔍 Verificações Pós-Deploy

### 1. Verificar URL do Serviço
```powershell
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

### 2. Testar Endpoint de Assinaturas
Acesse: `https://[URL_DO_SERVICO]/assinaturas/`

### 3. Verificar Logs
```powershell
gcloud run services logs read monpec --region us-central1 --limit 50
```

### 4. Testar Webhook (Opcional)
Use o ngrok para testar localmente:
```bash
ngrok http 8000
```
Depois configure temporariamente no Mercado Pago:
```
https://[seu-ngrok].ngrok.io/assinaturas/webhook/mercadopago/
```

## ⚠️ Checklist Final

- [ ] Deploy executado com sucesso
- [ ] URL do serviço obtida
- [ ] Webhook configurado no painel do Mercado Pago
- [ ] Teste de checkout realizado
- [ ] Verificação de email automático funcionando
- [ ] Senha padrão sendo definida corretamente

## 🔗 URLs Importantes

- **Dashboard de Assinaturas**: `https://monpec.com.br/assinaturas/`
- **Webhook**: `https://monpec.com.br/assinaturas/webhook/mercadopago/`
- **Sucesso**: `https://monpec.com.br/assinaturas/sucesso/`
- **Cancelado**: `https://monpec.com.br/assinaturas/cancelado/`

## 📞 Suporte

Se houver problemas:
1. Verifique os logs do Cloud Run
2. Confirme que as variáveis de ambiente estão configuradas
3. Verifique se o webhook está configurado no Mercado Pago
4. Teste com um pagamento de teste (cartão de teste do Mercado Pago)

