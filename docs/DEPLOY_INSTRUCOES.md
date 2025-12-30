# INSTRUÇÕES DE DEPLOY - MONPEC

## Pré-requisitos

1. **Conta Google Cloud Platform** com projeto criado
2. **Google Cloud SDK** instalado e configurado
3. **Python 3.11** instalado
4. **Docker** (para Cloud Run)

## Passo a Passo

### 1. Preparação Local

```powershell
# Navegar até o diretório do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Criar backup completo
.\scripts\BACKUP_SISTEMA.ps1

# Verificar dependências
pip install -r requirements.txt
```

### 2. Configurar Google Cloud

```powershell
# Autenticar
gcloud auth login

# Definir projeto
gcloud config set project SEU_PROJECT_ID

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Configurar Variáveis de Ambiente

No Google Cloud Console:
1. Ir para **Cloud Run** > Seu serviço > **Variáveis e Segredos**
2. Adicionar as seguintes variáveis:

```
DEBUG=False
SECRET_KEY=<sua_chave_secreta>
ALLOWED_HOSTS=<seu-dominio.com,*.run.app>
DATABASE_URL=<url_do_banco>
STRIPE_SECRET_KEY=<chave_stripe>
STRIPE_PUBLISHABLE_KEY=<chave_publica>
STRIPE_WEBHOOK_SECRET=<webhook_secret>
EMAIL_HOST=<servidor_email>
EMAIL_PORT=587
EMAIL_HOST_USER=<usuario>
EMAIL_HOST_PASSWORD=<senha>
```

### 4. Deploy

#### Opção A: Cloud Run (Recomendado)

```powershell
# Executar script de deploy
.\scripts\DEPLOY_GCP.ps1

# Ou manualmente:
gcloud run deploy monpec-gestao-rural \
  --source . \
  --region southamerica-east1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

#### Opção B: App Engine

```powershell
# Copiar app.yaml para raiz (se necessário)
copy deploy\config\app.yaml app.yaml

# Deploy
gcloud app deploy
```

### 5. Configurar Banco de Dados

#### Opção A: Cloud SQL (PostgreSQL - Recomendado)

1. Criar instância Cloud SQL
2. Configurar conexão
3. Atualizar `DATABASE_URL` nas variáveis de ambiente
4. Executar migrações:

```powershell
gcloud run services update monpec-gestao-rural \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/db?host=/cloudsql/connection"
```

#### Opção B: SQLite (Apenas para testes)

- SQLite funciona, mas não é recomendado para produção
- Arquivos são efêmeros em Cloud Run

### 6. Configurar Arquivos Estáticos

#### Opção A: Cloud Storage

```powershell
# Criar bucket
gsutil mb gs://monpec-static-files

# Fazer upload
gsutil -m rsync -r staticfiles/ gs://monpec-static-files/static/

# Configurar como público
gsutil iam ch allUsers:objectViewer gs://monpec-static-files
```

#### Opção B: Servir via Cloud Run

- Arquivos estáticos são servidos automaticamente
- Para melhor performance, usar CDN

### 7. Configurar Domínio Personalizado

1. No Cloud Run, ir em **Gerenciar domínios personalizados**
2. Adicionar domínio
3. Configurar DNS conforme instruções
4. Atualizar `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`

### 8. Pós-Deploy

```powershell
# Executar migrações
gcloud run services update monpec-gestao-rural \
  --command "python" \
  --args "manage.py,migrate"

# Criar superusuário
gcloud run services update monpec-gestao-rural \
  --command "python" \
  --args "manage.py,createsuperuser"
```

## Verificação

1. Acessar URL do serviço
2. Verificar landing page
3. Testar login
4. Verificar módulos principais
5. Testar funcionalidades críticas

## Troubleshooting

### Erro 503 - Service Unavailable
- Verificar logs: `gcloud run services logs read monpec-gestao-rural`
- Verificar variáveis de ambiente
- Verificar conexão com banco de dados

### Erro de Migrações
- Executar manualmente via Cloud Shell
- Verificar permissões do banco de dados

### Arquivos Estáticos Não Carregam
- Verificar `collectstatic` foi executado
- Verificar configuração de Cloud Storage
- Verificar permissões do bucket

## Backup e Restauração

### Backup Automático
```powershell
.\scripts\BACKUP_SISTEMA.ps1
```

### Restaurar de Backup
1. Copiar arquivos de volta
2. Executar: `python manage.py loaddata dumpdata.json`
3. Executar: `python manage.py migrate`

## Monitoramento

- **Logs**: Google Cloud Console > Cloud Run > Logs
- **Métricas**: Google Cloud Console > Cloud Run > Métricas
- **Alertas**: Configurar no Cloud Monitoring

## Segurança

1. ✅ Nunca commitar `.env` ou `db.sqlite3`
2. ✅ Usar Secrets Manager para dados sensíveis
3. ✅ Habilitar HTTPS (automático no Cloud Run)
4. ✅ Configurar CORS adequadamente
5. ✅ Usar variáveis de ambiente para configurações

## Custos Estimados

- **Cloud Run**: ~$0.40/GB-hora (primeiros 2 milhões de requisições grátis)
- **Cloud SQL**: ~$7-50/mês (dependendo do tamanho)
- **Cloud Storage**: ~$0.020/GB-mês
- **Tráfego**: Primeiros 1GB grátis/mês

## Suporte

Para problemas:
1. Verificar logs no Cloud Console
2. Consultar documentação: `BACKUP_COMPLETO.md`
3. Verificar URLs em: `BACKUP_COMPLETO.md`
































