# 🚀 Guia de Deploy no Google Cloud Shell

Este guia mostra como fazer o deploy do sistema MONPEC no Google Cloud Run usando o Cloud Shell.

## 📋 Pré-requisitos

1. ✅ Projeto Google Cloud criado: `monpec-sistema-rural`
2. ✅ Cloud SQL (banco de dados) configurado: `monpec-db`
3. ✅ Autenticado no Google Cloud Shell

---

## 🎯 Opção 1: Deploy Rápido (Recomendado)

Se você já está no Cloud Shell com os arquivos na pasta `Monpec_GestaoRural`, execute:

```bash
# 1. Entrar na pasta do projeto
cd Monpec_GestaoRural

# 2. Configurar o projeto
gcloud config set project monpec-sistema-rural

# 3. Deploy direto (o Cloud Run detecta o Dockerfile automaticamente)
gcloud run deploy monpec \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10
```

O comando `--source .` faz tudo automaticamente:
- ✅ Detecta o `Dockerfile`
- ✅ Faz o build da imagem
- ✅ Faz o deploy no Cloud Run

---

## 🎯 Opção 2: Deploy em Passos (Mais Controle)

### Passo 1: Preparar o Ambiente

```bash
# Entrar na pasta
cd Monpec_GestaoRural

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Habilitar APIs (se ainda não estiverem habilitadas)
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Passo 2: Build da Imagem Docker

```bash
# Build da imagem (leva 5-10 minutos)
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/monpec-sistema-rural/monpec:$TIMESTAMP"

gcloud builds submit --tag $IMAGE_TAG

# Marcar como latest (opcional)
gcloud container images add-tag $IMAGE_TAG gcr.io/monpec-sistema-rural/monpec:latest --quiet
```

### Passo 3: Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10
```

### Passo 4: Verificar o Deploy

```bash
# Obter a URL do serviço
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

# Ver logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=20
```

---

## ⚙️ Configurações do Deploy

### Parâmetros Explicados

- `--source .`: Faz build e deploy automaticamente a partir do diretório atual
- `--region us-central1`: Região onde o serviço será implantado
- `--platform managed`: Usa o Cloud Run totalmente gerenciado
- `--allow-unauthenticated`: Permite acesso público (sem autenticação)
- `--add-cloudsql-instances`: Conecta ao banco de dados Cloud SQL
- `--memory=2Gi`: 2 GB de RAM
- `--cpu=2`: 2 CPUs
- `--timeout=300`: Timeout de 5 minutos
- `--max-instances=10`: Máximo de 10 instâncias simultâneas

### Variáveis de Ambiente

O deploy configura automaticamente:
- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`: Settings para produção
- `DEBUG=False`: Modo produção
- `CLOUD_SQL_CONNECTION_NAME`: Conexão com o banco de dados
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Credenciais do banco

---

## 🔍 Verificação Pós-Deploy

### 1. Obter a URL do Serviço

```bash
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format="value(status.url)")
echo "Sistema disponível em: $SERVICE_URL"
```

### 2. Testar o Acesso

```bash
curl -I $SERVICE_URL
```

Deve retornar `HTTP/2 200` ou `HTTP/2 301/302` (redirecionamento).

### 3. Ver Logs em Tempo Real

```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --project monpec-sistema-rural
```

---

## 🐛 Troubleshooting

### Erro: "Dockerfile not found"

Certifique-se de que o arquivo `Dockerfile` existe na pasta atual:

```bash
ls -la Dockerfile
```

Se não existir, crie a partir do `Dockerfile.prod`:

```bash
cp Dockerfile.prod Dockerfile
```

### Erro: "Permission denied"

Verifique se você tem as permissões necessárias:

```bash
gcloud projects get-iam-policy monpec-sistema-rural
```

Você precisa das roles:
- `Cloud Run Admin`
- `Cloud Build Editor`
- `Service Account User`

### Erro: "Cloud SQL instance not found"

Verifique se o banco de dados existe:

```bash
gcloud sql instances list
```

Se não existir, crie:

```bash
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Erro: "Service unavailable" ou "502 Bad Gateway"

Verifique os logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50
```

Problemas comuns:
- Banco de dados não conectado
- Variáveis de ambiente incorretas
- Erro nas migrações

---

## 📝 Comandos Úteis

### Atualizar o Deploy (Após Fazer Mudanças)

```bash
cd Monpec_GestaoRural
gcloud run deploy monpec --source . --region us-central1
```

### Ver Status do Serviço

```bash
gcloud run services describe monpec --region us-central1
```

### Ver Todas as Revisões

```bash
gcloud run revisions list --service monpec --region us-central1
```

### Rollback para Versão Anterior

```bash
# Listar revisões
gcloud run revisions list --service monpec --region us-central1

# Fazer rollback
gcloud run services update-traffic monpec \
    --to-revisions=REVISION_NAME=100 \
    --region us-central1
```

### Aumentar/Diminuir Recursos

```bash
gcloud run services update monpec \
    --memory=4Gi \
    --cpu=4 \
    --region us-central1
```

---

## ✅ Checklist de Deploy

Antes do deploy, verifique:

- [ ] Arquivo `Dockerfile` existe na raiz do projeto
- [ ] Arquivo `requirements_producao.txt` está atualizado
- [ ] Projeto Google Cloud configurado: `monpec-sistema-rural`
- [ ] Cloud SQL configurado: `monpec-db`
- [ ] APIs habilitadas (Cloud Build, Cloud Run, Cloud SQL)
- [ ] Autenticado no gcloud (`gcloud auth list`)
- [ ] Variáveis de ambiente corretas (senha do banco, etc.)

---

## 🎉 Próximos Passos Após Deploy

1. ✅ Acessar a URL do serviço
2. ✅ Verificar se a landing page está funcionando
3. ✅ Testar login (admin será criado automaticamente)
4. ✅ Verificar logs para garantir que não há erros
5. ✅ Configurar domínio customizado (opcional)

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `gcloud logging read "resource.type=cloud_run_revision" --limit=50`
2. Verifique o status: `gcloud run services describe monpec --region us-central1`
3. Verifique o build: `gcloud builds list --limit=5`

