# 🔧 Diagnóstico e Correção do Erro 503 - monpec.com.br

## ⚠️ IMPORTANTE: Sistema no Google Cloud Run

O sistema está rodando no **Google Cloud Run**, não em uma VM tradicional. Comandos `systemctl` não funcionam no Cloud Shell porque não é um ambiente systemd.

## O que é o erro 503?

O erro **"The service you requested is not available yet. Please try again in 30 seconds"** é um erro **503 Service Unavailable**, que no Cloud Run geralmente indica que:

1. ⚠️ **Problema de faturamento** - Pagamento não processado (mais comum!)
2. ⚠️ O serviço Cloud Run não está rodando ou foi suspenso
3. ⚠️ O domínio não está mapeado corretamente
4. ⚠️ Há erros na aplicação que impedem o serviço de iniciar
5. ⚠️ O serviço está em processo de deploy/atualização

## 🚀 Solução Rápida (Cloud Run)

### ⚠️ PRIORIDADE 1: Verificar Faturamento

O aviso no console indica problema de pagamento. **Isso é a causa mais comum do erro 503!**

1. **Acesse o console de faturamento:**
   ```
   https://console.cloud.google.com/billing
   ```

2. **Verifique e atualize as informações de pagamento**

3. **Aguarde 5-10 minutos** após atualizar

### Opção 1: Script de Diagnóstico (Cloud Shell)

No **Cloud Shell** do Google Cloud Console, execute:

```bash
bash CORRIGIR_503_CLOUD_RUN.sh
```

Este script irá:
- Verificar status do serviço Cloud Run
- Verificar mapeamento do domínio
- Testar conectividade
- Verificar logs de erro
- Identificar problemas de faturamento

### Opção 2: Verificação Rápida

Para verificação rápida no Cloud Shell:

```bash
bash VERIFICAR_STATUS_CLOUD_RUN.sh
```

### Opção 3: Comandos Manuais (Cloud Shell)

```bash
# 1. Verificar projeto
gcloud config set project monpec-sistema-rural

# 2. Verificar status do serviço
gcloud run services describe monpec --region us-central1

# 3. Verificar domínio
gcloud run domain-mappings describe monpec.com.br --region us-central1

# 4. Ver logs recentes
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit 20

# 5. Testar URL do serviço
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
curl -I $SERVICE_URL
```

## 🔍 Diagnóstico Manual (Cloud Run)

### 1. Verificar Status do Serviço Cloud Run

```bash
gcloud run services describe monpec --region us-central1
```

### 2. Verificar URL e Testar Conectividade

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')

# Testar
curl -I $SERVICE_URL
```

### 3. Verificar Mapeamento do Domínio

```bash
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### 4. Verificar Logs de Erro

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit 50 --format "table(timestamp,severity,textPayload)"
```

### 5. Verificar Revisões Ativas

```bash
gcloud run revisions list --service monpec --region us-central1
```

### 6. Verificar Faturamento

```bash
gcloud beta billing projects describe monpec-sistema-rural --format 'value(billingAccountName)'
```

## 🔧 Correções Comuns (Cloud Run)

### Problema 1: Faturamento não processado ⚠️ MAIS COMUM!

**Solução:**
1. Acesse: https://console.cloud.google.com/billing
2. Atualize informações de pagamento
3. Aguarde 5-10 minutos
4. Verifique novamente

### Problema 2: Serviço não está rodando

```bash
# Verificar status
gcloud run services describe monpec --region us-central1

# Se necessário, fazer novo deploy
bash deploy_cloud_shell.sh
```

### Problema 3: Domínio não mapeado

```bash
# Mapear domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### Problema 4: Erros na aplicação

```bash
# Ver logs detalhados
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit 100

# Se necessário, atualizar serviço
gcloud run services update monpec --region us-central1
```

### Problema 5: Revisão com erro

```bash
# Listar revisões
gcloud run revisions list --service monpec --region us-central1

# Fazer novo deploy para criar nova revisão
bash deploy_cloud_shell.sh
```

## 📋 Comandos Úteis (Cloud Run)

```bash
# Ver status completo do serviço
gcloud run services describe monpec --region us-central1

# Ver logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"

# Atualizar serviço (força nova revisão)
gcloud run services update monpec --region us-central1

# Verificar domínio
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Testar URL do serviço
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
curl -I $SERVICE_URL

# Verificar faturamento
gcloud beta billing projects describe monpec-sistema-rural
```

## 🆘 Se Nada Funcionar (Cloud Run)

1. **Verificar faturamento (PRIORIDADE!):**
   - Acesse: https://console.cloud.google.com/billing
   - Atualize informações de pagamento
   - Aguarde alguns minutos

2. **Verificar se o serviço existe:**
   ```bash
   gcloud run services list --region us-central1
   ```

3. **Fazer novo deploy completo:**
   ```bash
   bash deploy_cloud_shell.sh
   ```

4. **Verificar logs detalhados:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit 100 --format json
   ```

5. **Verificar configuração do domínio:**
   ```bash
   gcloud run domain-mappings describe monpec.com.br --region us-central1 --format yaml
   ```

6. **Verificar DNS do domínio:**
   ```bash
   nslookup monpec.com.br
   dig monpec.com.br
   ```

## 📞 Contato

Se o problema persistir, verifique:
- Logs do sistema: `journalctl -u monpec -n 100`
- Logs do Nginx: `tail -100 /var/log/nginx/error.log`
- Status dos serviços: `systemctl status monpec nginx`

