# 🚀 Guia Completo - Deploy no Google Cloud Platform

Este guia contém todas as instruções para fazer o deploy completo do sistema MONPEC no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud** com projeto criado
2. **gcloud CLI** instalado ([instalar](https://cloud.google.com/sdk/docs/install))
3. **Docker** instalado (opcional, para testes locais)
4. **Acesso ao projeto** com permissões de Cloud Run Admin

## 🚀 Deploy Rápido (Automático)

### Opção 1: Script Bash (Linux/Mac)

```bash
# Dar permissão de execução
chmod +x DEPLOY_GOOGLE_CLOUD_COMPLETO.sh

# Executar deploy
./DEPLOY_GOOGLE_CLOUD_COMPLETO.sh
```

### Opção 2: Script PowerShell (Windows)

```powershell
.\DEPLOY_GOOGLE_CLOUD_COMPLETO.ps1
```

O script irá:
- ✅ Verificar autenticação
- ✅ Habilitar APIs necessárias
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Aplicar migrações
- ✅ Configurar variáveis de ambiente

## ⚙️ Configuração Manual

### 1. Autenticar no Google Cloud

```bash
gcloud auth login
gcloud config set project SEU-PROJETO-ID
```

### 2. Habilitar APIs Necessárias

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    containerregistry.googleapis.com
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env_producao` na raiz do projeto:

```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=SenhaSegura123!
DB_HOST=/cloudsql/PROJETO:REGIAO:INSTANCIA
CLOUD_SQL_CONNECTION_NAME=PROJETO:REGIAO:INSTANCIA
```

**Gerar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Build da Imagem Docker

```bash
gcloud builds submit --tag gcr.io/SEU-PROJETO-ID/monpec:latest
```

### 5. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/SEU-PROJETO-ID/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=sua-chave" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1
```

### 6. Configurar Cloud SQL (se usar)

```bash
gcloud run services update monpec \
    --region us-central1 \
    --add-cloudsql-instances=PROJETO:REGIAO:INSTANCIA
```

### 7. Aplicar Migrações

```bash
# Criar job de migração
gcloud run jobs create migrate-monpec \
    --image gcr.io/SEU-PROJETO-ID/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=sua-chave" \
    --command python \
    --args manage.py,migrate,--noinput

# Executar job
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

## 🔧 Configurar Variáveis de Ambiente

### Usando Script Automático

```bash
chmod +x CONFIGURAR_VARIAVEIS_GCP.sh
./CONFIGURAR_VARIAVEIS_GCP.sh
```

### Manualmente

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "SECRET_KEY=nova-chave,DB_NAME=novo-banco"
```

## 📊 Verificar Status

### Ver logs do serviço

```bash
gcloud run services logs read monpec --region us-central1
```

### Ver informações do serviço

```bash
gcloud run services describe monpec --region us-central1
```

### Obter URL do serviço

```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

## 🌐 Configurar Domínio Personalizado

### 1. Mapear domínio no Cloud Run

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### 2. Configurar DNS

Adicione os registros CNAME/A apontando para o Cloud Run conforme as instruções fornecidas pelo comando acima.

## 🔄 Atualizar Deploy

### Atualizar código

```bash
# 1. Fazer build da nova imagem
gcloud builds submit --tag gcr.io/SEU-PROJETO-ID/monpec:latest

# 2. Fazer deploy
gcloud run deploy monpec \
    --image gcr.io/SEU-PROJETO-ID/monpec:latest \
    --region us-central1
```

### Aplicar novas migrações

```bash
chmod +x APLICAR_MIGRACOES_GCP.sh
./APLICAR_MIGRACOES_GCP.sh
```

## 🐛 Solução de Problemas

### Erro: "Permission denied"

```bash
# Verificar permissões
gcloud projects get-iam-policy SEU-PROJETO-ID

# Adicionar permissões necessárias
gcloud projects add-iam-policy-binding SEU-PROJETO-ID \
    --member="user:seu-email@gmail.com" \
    --role="roles/run.admin"
```

### Erro: "Image not found"

```bash
# Verificar se a imagem foi criada
gcloud container images list

# Fazer build novamente
gcloud builds submit --tag gcr.io/SEU-PROJETO-ID/monpec:latest
```

### Erro: "Database connection failed"

1. Verificar se Cloud SQL está rodando:
```bash
gcloud sql instances list
```

2. Verificar connection name:
```bash
gcloud sql instances describe INSTANCIA --format="value(connectionName)"
```

3. Verificar variáveis de ambiente:
```bash
gcloud run services describe monpec --region us-central1 --format="yaml(spec.template.spec.containers[0].env)"
```

### Ver logs detalhados

```bash
# Logs do serviço
gcloud run services logs read monpec --region us-central1 --limit=50

# Logs do build
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

## 📝 Checklist de Deploy

- [ ] gcloud CLI instalado e autenticado
- [ ] Projeto Google Cloud criado e configurado
- [ ] APIs habilitadas (Cloud Run, Cloud Build, etc.)
- [ ] Arquivo `.env_producao` criado com SECRET_KEY
- [ ] Cloud SQL configurado (se usar banco de dados)
- [ ] Build da imagem Docker concluído
- [ ] Deploy no Cloud Run concluído
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações aplicadas
- [ ] Domínio configurado (se usar domínio personalizado)
- [ ] Teste de acesso bem-sucedido

## 🔐 Segurança

### Variáveis Sensíveis

Use Secret Manager para variáveis sensíveis:

```bash
# Criar secret
echo -n "sua-chave-secreta" | gcloud secrets create secret-key --data-file=-

# Usar no Cloud Run
gcloud run services update monpec \
    --region us-central1 \
    --update-secrets SECRET_KEY=secret-key:latest
```

### HTTPS

O Cloud Run fornece HTTPS automaticamente. Certifique-se de que:
- `SECURE_SSL_REDIRECT = True` em `settings_gcp.py` (já configurado)
- Domínio personalizado configurado corretamente

## 💰 Custos

O Cloud Run cobra por:
- **Requisições**: Primeiros 2 milhões/mês são gratuitos
- **CPU/Memória**: Cobrado apenas quando o serviço está processando requisições
- **Tráfego**: Primeiros 1GB/mês são gratuitos

Configure `--min-instances=0` para economizar (serviço pode ter cold start).

## 📞 Suporte

Se houver problemas:

1. Execute o diagnóstico:
```bash
python diagnosticar_erro_producao.py
```

2. Verifique os logs:
```bash
gcloud run services logs read monpec --region us-central1
```

3. Verifique o status do serviço:
```bash
gcloud run services describe monpec --region us-central1
```

---

**Última atualização**: 26/12/2025
















