# 🔧 Problemas Identificados e Soluções

## ❌ Problemas Encontrados:

### 1. Erro de Região
- **Problema**: Comandos usando `us-centrall` (errado) em vez de `us-central1` (correto)
- **Solução**: Todos os scripts foram corrigidos para usar `us-central1`

### 2. Migração Falhou
- **Problema**: Job de migração executou mas falhou: "0 / 1 complete...failed"
- **Causa Provável**: Variáveis de ambiente do banco de dados não configuradas no job
- **Solução**: Scripts criados para configurar variáveis e executar migração

### 3. Domínio www.monpec.com.br
- **Status**: ✅ Criado com sucesso
- **Ação Necessária**: Configurar DNS CNAME: `www` → `ghs.googlehosted.com.`

## ✅ Soluções Disponíveis:

### 1. Diagnosticar Problema da Migração
```bash
chmod +x DIAGNOSTICAR_MIGRACAO.sh
./DIAGNOSTICAR_MIGRACAO.sh
```

### 2. Corrigir e Executar Migração (Automático)
```bash
chmod +x CORRIGIR_MIGRACAO.sh
./CORRIGIR_MIGRACAO.sh
```

### 3. Executar Migração (Manual - Recomendado)
```bash
chmod +x EXECUTAR_MIGRACAO_SIMPLES.sh
./EXECUTAR_MIGRACAO_SIMPLES.sh
```

Este script pedirá as informações do banco de dados e executará a migração.

## 📋 Passo a Passo Completo:

### 1. Configurar Variáveis de Ambiente do Serviço
```bash
gcloud run services update monpec --region us-central1 \
  --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940,MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3,SECRET_KEY=SUA_SECRET_KEY,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME"
```

### 2. Executar Migração
```bash
# Opção A: Script automático
./EXECUTAR_MIGRACAO_SIMPLES.sh

# Opção B: Manual
gcloud run jobs update migrate-monpec --region us-central1 \
  --update-env-vars "DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

### 3. Configurar DNS
No painel do seu provedor de domínio, adicione:
- **Nome**: `www`
- **Tipo**: `CNAME`
- **Valor**: `ghs.googlehosted.com.`

### 4. Verificar Tudo
```bash
chmod +x VERIFICAR_TUDO.sh
./VERIFICAR_TUDO.sh
```

## 🎯 Ordem Recomendada de Execução:

1. ✅ **Configurar variáveis do serviço** (passo 1 acima)
2. ✅ **Executar migração** (passo 2 acima)
3. ✅ **Configurar DNS** (passo 3 acima)
4. ✅ **Verificar tudo** (passo 4 acima)
5. ✅ **Testar sistema**: https://www.monpec.com.br

## 📞 Se Ainda Houver Problemas:

### Ver logs detalhados:
```bash
# Logs do serviço
gcloud run services logs read monpec --region us-central1 --limit 100

# Logs do job de migração
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-monpec" --limit 50 --format="table(timestamp,severity,textPayload)"
```

### Verificar status do job:
```bash
gcloud run jobs executions list --job migrate-monpec --region us-central1 --limit 5
```





















