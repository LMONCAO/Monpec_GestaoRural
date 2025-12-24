# Guia Completo de Deploy no Google Cloud Platform

Este guia fornece instruções passo a passo para fazer o deploy do sistema MonPEC no Google Cloud Platform usando Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud** com projeto criado
2. **Google Cloud SDK (gcloud)** instalado
3. **Docker** instalado (opcional, para testes locais)
4. **Credenciais do Mercado Pago** (Access Token e Public Key)
5. **Domínio personalizado** (opcional, mas recomendado)

## 🚀 Deploy Rápido

### Opção 1: Deploy Automatizado (Recomendado)

```bash
# Dar permissão de execução ao script
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

O script irá:
- Verificar e habilitar APIs necessárias
- Fazer build da imagem Docker
- Fazer deploy no Cloud Run
- Fornecer próximos passos

### Opção 2: Deploy Manual

```bash
# 1. Configurar projeto
gcloud config set project SEU_PROJECT_ID

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com

# 3. Build e Deploy
gcloud builds submit --config cloudbuild.yaml
```

## 🗄️ Configuração do Banco de Dados (Cloud SQL)

### Criar Instância PostgreSQL

```bash
gcloud sql instances create monpec-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=SUA_SENHA_ROOT_AQUI
```

**Nota:** Para produção, use um tier maior (ex: `db-n1-standard-1`)

### Criar Banco de Dados e Usuário

```bash
# Conectar à instância
gcloud sql connect monpec-db --user=postgres

# No PostgreSQL, execute:
CREATE DATABASE monpec_db;
CREATE USER monpec_user WITH PASSWORD 'SUA_SENHA_AQUI';
GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;
\q
```

### Obter Connection Name

```bash
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

O formato será: `PROJECT_ID:REGION:INSTANCE_NAME`

## ⚙️ Configuração de Variáveis de Ambiente

Configure todas as variáveis de ambiente necessárias no Cloud Run:

```bash
gcloud run services update monpec \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --set-env-vars="SECRET_KEY=SUA_SECRET_KEY_DJANGO_AQUI" \
  --set-env-vars="DEBUG=False" \
  --set-env-vars="DB_NAME=monpec_db" \
  --set-env-vars="DB_USER=monpec_user" \
  --set-env-vars="DB_PASSWORD=SUA_SENHA_DB_AQUI" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:monpec-db" \
  --set-env-vars="MERCADOPAGO_ACCESS_TOKEN=SEU_ACCESS_TOKEN" \
  --set-env-vars="MERCADOPAGO_PUBLIC_KEY=SUA_PUBLIC_KEY" \
  --set-env-vars="MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/" \
  --set-env-vars="MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
  --set-env-vars="SITE_URL=https://monpec.com.br" \
  --set-env-vars="PAYMENT_GATEWAY_DEFAULT=mercadopago"
```

### Gerar SECRET_KEY do Django

```python
# Execute no Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou use:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🔐 Conectar Cloud Run ao Cloud SQL

```bash
gcloud run services update monpec \
  --region=us-central1 \
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db
```

## 📦 Aplicar Migrações

### Criar Job de Migração

```bash
gcloud run jobs create migrate-monpec \
  --image=gcr.io/PROJECT_ID/monpec:latest \
  --region=us-central1 \
  --command=python \
  --args=manage.py,migrate \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --set-env-vars="SECRET_KEY=SUA_SECRET_KEY" \
  --set-env-vars="DB_NAME=monpec_db" \
  --set-env-vars="DB_USER=monpec_user" \
  --set-env-vars="DB_PASSWORD=SUA_SENHA" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:monpec-db" \
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db
```

### Executar Migração

```bash
gcloud run jobs execute migrate-monpec --region=us-central1
```

## 👤 Criar Superusuário

### Criar Job para Superusuário

```bash
gcloud run jobs create create-superuser \
  --image=gcr.io/PROJECT_ID/monpec:latest \
  --region=us-central1 \
  --command=python \
  --args=manage.py,createsuperuser \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --set-env-vars="SECRET_KEY=SUA_SECRET_KEY" \
  --set-env-vars="DB_NAME=monpec_db" \
  --set-env-vars="DB_USER=monpec_user" \
  --set-env-vars="DB_PASSWORD=SUA_SENHA" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:monpec-db" \
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db \
  --interactive
```

### Executar Criação de Superusuário

```bash
gcloud run jobs execute create-superuser --region=us-central1
```

**Nota:** Para criar superusuário de forma não-interativa, use um script Python customizado.

## 🌐 Configurar Domínio Personalizado

### 1. Verificar Propriedade do Domínio

```bash
gcloud run domain-mappings create \
  --service=monpec \
  --domain=monpec.com.br \
  --region=us-central1
```

### 2. Configurar DNS

Após criar o mapeamento, você receberá registros DNS. Configure no seu provedor de domínio:

- Tipo: `A` ou `AAAA`
- Nome: `@` ou `monpec.com.br`
- Valor: IP fornecido pelo Google

Para www:

```bash
gcloud run domain-mappings create \
  --service=monpec \
  --domain=www.monpec.com.br \
  --region=us-central1
```

## 📊 Monitoramento e Logs

### Ver Logs em Tempo Real

```bash
gcloud run services logs tail monpec --region=us-central1
```

### Ver Logs no Console

Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec/logs

## 🔄 Atualizar Aplicação

Para atualizar a aplicação após fazer alterações:

```bash
# Opção 1: Usar script
./deploy.sh

# Opção 2: Build manual
gcloud builds submit --config cloudbuild.yaml
```

## 🛠️ Troubleshooting

### Erro: "502 Bad Gateway"

- Verifique se o serviço está rodando: `gcloud run services describe monpec --region=us-central1`
- Verifique os logs: `gcloud run services logs read monpec --region=us-central1`
- Verifique se as variáveis de ambiente estão configuradas corretamente

### Erro: "503 Service Unavailable"

- Verifique se há instâncias mínimas configuradas
- Verifique se o Cloud SQL está acessível
- Verifique os limites de quota do projeto

### Erro de Conexão com Banco de Dados

- Verifique se o Cloud SQL está na mesma região
- Verifique se o Cloud Run tem permissão para acessar o Cloud SQL
- Verifique se `CLOUD_SQL_CONNECTION_NAME` está correto
- Verifique se o usuário e senha estão corretos

### Arquivos Estáticos Não Carregam

- Verifique se o `collectstatic` foi executado
- Verifique se o WhiteNoise está configurado corretamente
- Verifique se `STATIC_ROOT` está configurado

### Erro de Migração

- Execute as migrações manualmente via Cloud Run Job
- Verifique se o banco de dados existe e o usuário tem permissões
- Verifique os logs do job de migração

## 📝 Checklist de Deploy

- [ ] Projeto Google Cloud criado
- [ ] APIs habilitadas
- [ ] Cloud SQL PostgreSQL criado
- [ ] Banco de dados e usuário criados
- [ ] Imagem Docker buildada e deployada
- [ ] Variáveis de ambiente configuradas
- [ ] Cloud Run conectado ao Cloud SQL
- [ ] Migrações aplicadas
- [ ] Superusuário criado
- [ ] Domínio personalizado configurado (opcional)
- [ ] DNS configurado (se usando domínio)
- [ ] Testes realizados
- [ ] Logs monitorados

## 💰 Estimativa de Custos

### Cloud Run
- **Gratuito:** 2 milhões de requisições/mês
- **Pago:** ~$0.40 por milhão de requisições após o limite

### Cloud SQL (db-f1-micro)
- **Gratuito:** Não há tier gratuito permanente
- **Pago:** ~$7-10/mês para db-f1-micro

### Cloud Build
- **Gratuito:** 120 minutos/dia
- **Pago:** ~$0.003 por minuto após o limite

### Container Registry
- **Gratuito:** 0.5 GB de armazenamento
- **Pago:** ~$0.026 por GB/mês após o limite

**Total estimado:** ~$10-20/mês para uso básico

## 🔒 Segurança

1. **Nunca commite** arquivos `.env` ou credenciais
2. Use **Secret Manager** para credenciais sensíveis
3. Configure **HTTPS** obrigatório
4. Use **IAM** para controlar acesso
5. Ative **Cloud Armor** para proteção DDoS (opcional)

## 📚 Recursos Adicionais

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Documentação Cloud SQL](https://cloud.google.com/sql/docs)
- [Documentação Cloud Build](https://cloud.google.com/build/docs)
- [Django no Cloud Run](https://cloud.google.com/python/django/run)

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs do Cloud Run
2. Verifique os logs do Cloud Build
3. Consulte a documentação oficial
4. Verifique o status do serviço no console

---

**Última atualização:** 2025-01-27
