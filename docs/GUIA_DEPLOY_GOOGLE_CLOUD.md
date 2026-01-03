# 🚀 Guia Completo de Deploy - Google Cloud Run - MONPEC

Este guia explica como fazer deploy completo do sistema MONPEC no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud** com projeto criado
2. **gcloud CLI** instalado e configurado
3. **Docker** instalado (opcional, para testes locais)
4. **Acesso ao projeto** com permissões de:
   - Cloud Run Admin
   - Cloud Build Editor
   - Service Account User

## 🔧 Configuração Inicial

### 1. Autenticação

```bash
# Login no Google Cloud
gcloud auth login

# Configurar projeto
gcloud config set project SEU_PROJECT_ID
```

### 2. Habilitar APIs Necessárias

As APIs serão habilitadas automaticamente pelo script, mas você pode habilitar manualmente:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

## 🚀 Deploy Automático (Recomendado)

### Para Linux/Mac/Cloud Shell:

```bash
# Dar permissão de execução
chmod +x DEPLOY_GOOGLE_CLOUD_COMPLETO.sh

# Executar deploy
./DEPLOY_GOOGLE_CLOUD_COMPLETO.sh
```

### Para Windows (PowerShell):

```powershell
# Executar deploy
.\DEPLOY_GOOGLE_CLOUD_COMPLETO.ps1
```

O script fará automaticamente:
- ✅ Verificação de autenticação
- ✅ Configuração do projeto
- ✅ Habilitação de APIs
- ✅ Build da imagem Docker
- ✅ Deploy no Cloud Run
- ✅ Configuração de variáveis de ambiente
- ✅ Execução de migrações

## 📝 Configuração Manual (Alternativa)

### 1. Build da Imagem

```bash
# Build usando Cloud Build
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/monpec:latest
```

### 2. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/SEU_PROJECT_ID/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,PYTHONUNBUFFERED=1"
```

### 3. Configurar Variáveis de Ambiente

Se você tiver variáveis de ambiente adicionais (banco de dados, chaves de API, etc.), crie um arquivo `.env.gcp`:

```bash
# .env.gcp
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=sua-senha-aqui
DB_HOST=/cloudsql/SEU_CONNECTION_NAME
CLOUD_SQL_CONNECTION_NAME=projeto:regiao:instancia
```

### 4. Executar Migrações

```bash
# Criar job temporário para migrações
gcloud run jobs create monpec-migrate \
    --image gcr.io/SEU_PROJECT_ID/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
    --command python \
    --args "manage.py,migrate,--noinput"

# Executar o job
gcloud run jobs execute monpec-migrate --region us-central1 --wait

# Deletar o job após uso
gcloud run jobs delete monpec-migrate --region us-central1
```

## 🗄️ Configuração do Banco de Dados (Cloud SQL)

### Criar Instância Cloud SQL

```bash
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=SUA_SENHA_ROOT
```

### Criar Banco e Usuário

```bash
# Criar banco de dados
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=SUA_SENHA_USUARIO
```

### Obter Connection Name

```bash
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

### Conectar Cloud Run ao Cloud SQL

```bash
gcloud run services update monpec \
    --region us-central1 \
    --add-cloudsql-instances SEU_CONNECTION_NAME \
    --set-env-vars "CLOUD_SQL_CONNECTION_NAME=SEU_CONNECTION_NAME,DB_HOST=/cloudsql/SEU_CONNECTION_NAME"
```

## 🌐 Configurar Domínio Personalizado

### 1. Mapear Domínio no Cloud Run

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### 2. Configurar DNS

Adicione os registros CNAME apontando para o Cloud Run conforme instruções do Google Cloud.

## 📊 Monitoramento e Logs

### Ver Logs

```bash
# Últimos 50 logs
gcloud run services logs read monpec --region us-central1 --limit=50

# Logs em tempo real
gcloud run services logs tail monpec --region us-central1
```

### Ver Status do Serviço

```bash
gcloud run services describe monpec --region us-central1
```

### Ver Métricas

Acesse o Console do Google Cloud: Cloud Run > monpec > Métricas

## 🔄 Atualizar Deploy

Para atualizar o sistema após fazer alterações:

```bash
# Opção 1: Usar o script completo novamente
./DEPLOY_GOOGLE_CLOUD_COMPLETO.sh

# Opção 2: Deploy rápido (apenas rebuild e deploy)
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/monpec:latest
gcloud run deploy monpec \
    --image gcr.io/SEU_PROJECT_ID/monpec:latest \
    --region us-central1
```

## 🛠️ Solução de Problemas

### Erro: "Internal Server Error"

1. Verifique os logs:
   ```bash
   gcloud run services logs read monpec --region us-central1 --limit=100
   ```

2. Verifique se o domínio está em ALLOWED_HOSTS (já configurado em `settings_gcp.py`)

3. Verifique variáveis de ambiente:
   ```bash
   gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
   ```

### Erro de Conexão com Banco de Dados

1. Verifique se o Cloud SQL está acessível:
   ```bash
   gcloud sql instances describe monpec-db
   ```

2. Verifique se o Cloud Run tem permissão para acessar o Cloud SQL:
   - Vá em Cloud SQL > Instâncias > monpec-db > Conexões
   - Verifique se o Cloud Run está autorizado

### Erro: "Permission Denied"

Verifique se você tem as permissões necessárias:
```bash
gcloud projects get-iam-policy SEU_PROJECT_ID
```

## 📚 Recursos Adicionais

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Documentação Cloud SQL](https://cloud.google.com/sql/docs)
- [Documentação Django no Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-django-service)

## ✅ Checklist de Deploy

- [ ] gcloud CLI instalado e autenticado
- [ ] Projeto Google Cloud configurado
- [ ] APIs habilitadas
- [ ] Dockerfile.prod verificado
- [ ] Variáveis de ambiente configuradas
- [ ] Cloud SQL criado (se necessário)
- [ ] Deploy executado com sucesso
- [ ] Migrações executadas
- [ ] Domínio configurado (opcional)
- [ ] Logs verificados
- [ ] Site acessível

## 🎉 Pronto!

Após o deploy, seu sistema estará disponível em:
- URL do Cloud Run: `https://monpec-XXXXX.run.app`
- Domínio personalizado: `https://monpec.com.br` (após configurar DNS)

Para acessar o admin:
- URL: `https://monpec.com.br/admin` (ou URL do Cloud Run)
























