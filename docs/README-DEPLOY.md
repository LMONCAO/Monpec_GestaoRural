# Guia de Deploy - Sistema MONPEC

Este guia explica como fazer deploy do sistema MONPEC no Google Cloud Run de forma otimizada e confiável.

## 📋 Pré-requisitos

1. **Google Cloud SDK (gcloud)** instalado e configurado
   - Download: https://cloud.google.com/sdk/docs/install
   - Autenticação: `gcloud auth login`

2. **Projeto Google Cloud** criado
   - Configure o projeto: `gcloud config set project SEU-PROJETO-ID`

3. **APIs habilitadas** (o script faz isso automaticamente):
   - Cloud Build API
   - Cloud Run API
   - Cloud SQL Admin API
   - Container Registry API

## 🚀 Deploy Rápido

### Linux/Mac (Cloud Shell)

```bash
# 1. Faça upload do projeto ou clone do repositório

# 2. Execute o script de deploy
./deploy-gcp.sh
```

### Windows (PowerShell)

```powershell
# 1. Execute o script de deploy
.\deploy-gcp.ps1
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Antes de fazer o deploy, configure as variáveis de ambiente necessárias:

```bash
# Linux/Mac
export GCP_PROJECT="seu-projeto-id"
export SECRET_KEY="sua-secret-key-django"
export DB_NAME="nome-do-banco"
export DB_USER="usuario-do-banco"
export DB_PASSWORD="senha-do-banco"
export DB_HOST="host-do-banco"
export CLOUD_SQL_CONNECTION_NAME="projeto:regiao:instancia"
```

```powershell
# Windows PowerShell
$env:GCP_PROJECT = "seu-projeto-id"
$env:SECRET_KEY = "sua-secret-key-django"
$env:DB_NAME = "nome-do-banco"
$env:DB_USER = "usuario-do-banco"
$env:DB_PASSWORD = "senha-do-banco"
$env:DB_HOST = "host-do-banco"
$env:CLOUD_SQL_CONNECTION_NAME = "projeto:regiao:instancia"
```

### Parâmetros do Script

O script usa valores padrão que podem ser sobrescritos:

- **PROJECT_ID**: Obtido de `GCP_PROJECT` ou `gcloud config get-value project`
- **SERVICE_NAME**: `monpec` (padrão)
- **REGION**: `us-central1` (padrão)

### Personalizar no Linux/Mac

```bash
export GCP_PROJECT="meu-projeto"
export CLOUD_RUN_SERVICE="meu-servico"
export CLOUD_RUN_REGION="us-east1"
./deploy-gcp.sh
```

### Personalizar no Windows

```powershell
.\deploy-gcp.ps1 -ProjectId "meu-projeto" -ServiceName "meu-servico" -Region "us-east1"
```

## 📦 O que o Script Faz

1. **Verifica dependências**: gcloud CLI, autenticação, projeto
2. **Habilita APIs**: Garante que todas as APIs necessárias estão habilitadas
3. **Build da imagem**: Cria a imagem Docker usando Cloud Build
4. **Deploy no Cloud Run**: Faz deploy do serviço com configurações otimizadas
5. **Executa migrações**: Cria e executa um job para aplicar migrações do Django

## 🔄 Executar Migrações Separadamente

Se precisar executar migrações após o deploy:

### Linux/Mac

```bash
./executar-migracoes.sh
```

### Windows (via gcloud diretamente)

```powershell
# Executar job de migração existente
gcloud run jobs execute migrate-monpec --region=us-central1

# Ou criar e executar manualmente
gcloud run jobs create migrate-monpec `
    --image gcr.io/SEU-PROJETO/monpec:latest `
    --region us-central1 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --set-cloudsql-instances SEU-CONNECTION-NAME `
    --command python `
    --args "manage.py,migrate,--noinput"
```

## 🐛 Troubleshooting

### Erro: "Project ID not found"

```bash
# Configure o projeto
gcloud config set project SEU-PROJETO-ID

# Ou defina a variável
export GCP_PROJECT="SEU-PROJETO-ID"
```

### Erro: "Build failed"

- Verifique os logs: `gcloud builds list --limit=1`
- Verifique se o Dockerfile.prod existe
- Verifique se requirements.txt está correto
- Verifique o .gcloudignore (muitos arquivos podem causar timeout)

### Erro: "Job creation failed"

- O job pode já existir. O script tenta atualizar se necessário
- Verifique as permissões do projeto
- Verifique se o Cloud SQL connection name está correto

### Erro: "Migration failed"

```bash
# Ver logs do job
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-monpec" --limit=50

# Executar manualmente
gcloud run jobs execute migrate-monpec --region=us-central1 --wait
```

## 📊 Verificar Deploy

### Ver status do serviço

```bash
gcloud run services describe monpec --region=us-central1
```

### Ver logs

```bash
gcloud run services logs read monpec --region=us-central1 --limit=50
```

### Obter URL

```bash
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

## 🎯 Otimizações Aplicadas

1. **.gcloudignore otimizado**: Exclui arquivos desnecessários do build
   - Scripts (.sh, .ps1, .bat)
   - Documentação (.md, .txt)
   - Arquivos temporários e backups
   - Node modules e caches

2. **Dockerfile otimizado**: 
   - Build em camadas para aproveitar cache
   - Instalação eficiente de dependências
   - Estrutura limpa e organizada

3. **Scripts robustos**:
   - Tratamento de erros adequado
   - Verificação de recursos existentes
   - Mensagens claras e informativas
   - Suporte a jobs existentes

## 📝 Próximos Passos Após Deploy

1. **Configurar domínio personalizado** (opcional):
   ```bash
   gcloud run domain-mappings create \
     --service monpec \
     --domain monpec.com.br \
     --region us-central1
   ```

2. **Criar superusuário**:
   ```bash
   gcloud run jobs create create-superuser \
     --image gcr.io/SEU-PROJETO/monpec:latest \
     --region us-central1 \
     --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
     --command python \
     --args "manage.py,createsuperuser" \
     --interactive
   ```

3. **Configurar variáveis de ambiente adicionais**:
   ```bash
   gcloud run services update monpec \
     --region us-central1 \
     --update-env-vars "NOVA_VARIAVEL=valor"
   ```

## 🔒 Segurança

- **Nunca** commite arquivos `.env` com credenciais
- Use **Secret Manager** para senhas e tokens sensíveis
- Mantenha `DEBUG=False` em produção
- Configure **ALLOWED_HOSTS** corretamente
- Use **Cloud SQL Proxy** ou conexão privada para banco de dados

## 📚 Referências

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)











