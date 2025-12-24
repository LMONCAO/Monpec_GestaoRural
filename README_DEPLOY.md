# 🚀 Deploy MonPEC - Google Cloud Platform

Sistema completo de deploy profissional para o MonPEC no Google Cloud Run.

## 📦 Arquivos Criados

### Arquivos Principais
- **`Dockerfile.prod`** - Imagem Docker otimizada para produção
- **`cloudbuild-config.yaml`** - Configuração de build e deploy automatizado
- **`.dockerignore`** - Arquivos ignorados no build Docker
- **`deploy-completo.sh`** - Script completo que faz tudo automaticamente ⭐
- **`deploy.sh`** - Script básico de deploy
- **`configurar-variaveis-ambiente.sh`** - Configurar variáveis de ambiente
- **`executar-migracoes.sh`** - Executar migrações do Django
- **`criar-superusuario.sh`** - Criar superusuário

### Documentação
- **`DEPLOY_GCP_COMPLETO.md`** - Guia completo e detalhado
- **`DEPLOY_RAPIDO.md`** - Guia rápido de 5 passos
- **`README_DEPLOY.md`** - Este arquivo

## ⚡ Deploy Rápido (Recomendado)

### Opção 1: Script Completo (Faz TUDO)

```bash
chmod +x deploy-completo.sh
./deploy-completo.sh
```

Este script:
- ✅ Habilita todas as APIs necessárias
- ✅ Cria Cloud SQL (se não existir)
- ✅ Faz build e deploy da aplicação
- ✅ Configura todas as variáveis de ambiente
- ✅ Conecta Cloud Run ao Cloud SQL
- ✅ Aplica migrações automaticamente
- ✅ Fornece URL final e próximos passos

### Opção 2: Passo a Passo Manual

```bash
# 1. Deploy
chmod +x deploy.sh
./deploy.sh

# 2. Configurar variáveis
chmod +x configurar-variaveis-ambiente.sh
./configurar-variaveis-ambiente.sh

# 3. Migrações
chmod +x executar-migracoes.sh
./executar-migracoes.sh
```

## 📋 Pré-requisitos

1. **Google Cloud SDK** instalado
   ```bash
   # Verificar instalação
   gcloud --version
   ```

2. **Autenticação**
   ```bash
   gcloud auth login
   gcloud config set project SEU_PROJECT_ID
   ```

3. **Credenciais Mercado Pago**
   - Access Token
   - Public Key

## 🗄️ Banco de Dados

O script `deploy-completo.sh` cria automaticamente o Cloud SQL. Se preferir criar manualmente:

```bash
# Criar instância
gcloud sql instances create monpec-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=SUA_SENHA

# Criar banco e usuário
gcloud sql databases create monpec_db --instance=monpec-db
gcloud sql users create monpec_user \
  --instance=monpec-db \
  --password=SUA_SENHA
```

## ⚙️ Variáveis de Ambiente Necessárias

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `SECRET_KEY` | Chave secreta do Django | ✅ Sim |
| `DB_NAME` | Nome do banco de dados | ✅ Sim |
| `DB_USER` | Usuário do banco | ✅ Sim |
| `DB_PASSWORD` | Senha do banco | ✅ Sim |
| `CLOUD_SQL_CONNECTION_NAME` | Connection name do Cloud SQL | ✅ Sim |
| `MERCADOPAGO_ACCESS_TOKEN` | Token do Mercado Pago | ✅ Sim |
| `MERCADOPAGO_PUBLIC_KEY` | Public key do Mercado Pago | ✅ Sim |
| `SITE_URL` | URL do site | ⚠️ Recomendado |
| `DEBUG` | Modo debug (False em produção) | ⚠️ Recomendado |

## 🔄 Atualizar Aplicação

Após fazer alterações no código:

```bash
./deploy-completo.sh
```

Ou apenas rebuild:

```bash
gcloud builds submit --config cloudbuild-config.yaml
```

## 🐛 Troubleshooting

### Erro 502 Bad Gateway
```bash
# Ver logs
gcloud run services logs tail monpec --region=us-central1

# Verificar status
gcloud run services describe monpec --region=us-central1
```

### Erro de Conexão com Banco
```bash
# Verificar connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"

# Verificar se Cloud Run tem acesso
gcloud run services describe monpec --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Migrações Falhando
```bash
# Executar manualmente
./executar-migracoes.sh

# Ou via Cloud Shell
gcloud run jobs execute migrate-monpec --region=us-central1
```

## 📊 Monitoramento

### Ver Logs em Tempo Real
```bash
gcloud run services logs tail monpec --region=us-central1
```

### Ver Métricas
Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec/metrics

### Ver Logs no Console
Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec/logs

## 🌐 Configurar Domínio Personalizado

```bash
# Criar mapeamento
gcloud run domain-mappings create \
  --service=monpec \
  --domain=monpec.com.br \
  --region=us-central1

# Para www
gcloud run domain-mappings create \
  --service=monpec \
  --domain=www.monpec.com.br \
  --region=us-central1
```

Depois configure os registros DNS conforme instruções fornecidas.

## 💰 Custos Estimados

- **Cloud Run:** Gratuito até 2M requisições/mês
- **Cloud SQL (db-f1-micro):** ~$7-10/mês
- **Cloud Build:** 120 minutos/dia grátis
- **Container Registry:** 0.5 GB grátis

**Total:** ~$10-20/mês para uso básico

## 📚 Documentação Adicional

- **Guia Completo:** `DEPLOY_GCP_COMPLETO.md`
- **Guia Rápido:** `DEPLOY_RAPIDO.md`
- **Configuração Mercado Pago:** `docs/CONFIGURACAO_MERCADOPAGO.md`

## ✅ Checklist Final

Após o deploy, verifique:

- [ ] Serviço está rodando (status: Ready)
- [ ] URL acessível
- [ ] Migrações aplicadas
- [ ] Superusuário criado
- [ ] Admin acessível (/admin)
- [ ] Arquivos estáticos carregando
- [ ] Integração Mercado Pago funcionando
- [ ] Logs sem erros críticos

## 🆘 Suporte

1. Verifique os logs primeiro
2. Consulte `DEPLOY_GCP_COMPLETO.md` para detalhes
3. Verifique status no console do Google Cloud
4. Consulte documentação oficial do Google Cloud

---

**Criado:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Pronto para produção


