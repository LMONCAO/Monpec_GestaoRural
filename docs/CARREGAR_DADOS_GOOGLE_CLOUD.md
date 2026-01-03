# 🚀 Carregar Dados no Google Cloud - Guia Completo

Este guia explica como carregar dados do banco de dados no Google Cloud Run de forma automatizada.

## 📋 Índice

1. [Métodos Disponíveis](#métodos-disponíveis)
2. [Google Cloud Shell (Recomendado)](#google-cloud-shell-recomendado)
3. [PowerShell Local](#powershell-local)
4. [Via Cloud Run Jobs](#via-cloud-run-jobs)
5. [Troubleshooting](#troubleshooting)

## 🎯 Métodos Disponíveis

### 1. Google Cloud Shell (Mais Fácil)
Execute diretamente no navegador via Cloud Shell.

### 2. PowerShell Local
Execute no seu computador com Google Cloud SDK instalado.

### 3. Cloud Run Jobs (Automatizado)
Crie jobs recorrentes ou agendados.

## 🌐 Google Cloud Shell (Recomendado)

### Opção 1: Script Completo

1. **Acesse o Google Cloud Shell:**
   - Vá para: https://console.cloud.google.com/
   - Clique no ícone do Cloud Shell (terminal no topo)

2. **Execute o script:**
   ```bash
   # Sincronizar dados existentes (mais comum)
   bash <(curl -s https://raw.githubusercontent.com/seu-repo/main/scripts/deploy/CARREGAR_DADOS_CLOUD_SHELL.sh) sincronizar "" 1
   
   # Ou faça upload do arquivo e execute:
   # 1. Faça upload do arquivo scripts/deploy/CARREGAR_DADOS_CLOUD_SHELL.sh
   # 2. Execute:
   chmod +x CARREGAR_DADOS_CLOUD_SHELL.sh
   ./CARREGAR_DADOS_CLOUD_SHELL.sh sincronizar "" 1
   ```

### Opção 2: Comando Único (Copiar e Colar)

Copie e cole este comando completo no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"
FONTE="sincronizar"
USUARIO_ID="1"

gcloud config set project $PROJECT_ID
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create carregar-dados-banco \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,carregar_dados_banco,--fonte,$FONTE,--usuario-id,$USUARIO_ID" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=1800

gcloud run jobs execute carregar-dados-banco --region=$REGION --wait
```

### Opção 3: Importar de Arquivo SQLite (se você tem o arquivo)

Se você tem um arquivo SQLite para importar:

```bash
# 1. Faça upload do arquivo SQLite para o Cloud Shell
#    (use o ícone de upload no Cloud Shell)

# 2. Execute o comando (ajuste o caminho):
bash CARREGAR_DADOS_CLOUD_SHELL.sh sqlite "backup/db_backup.sqlite3" 1
```

## 💻 PowerShell Local

Se você tem o Google Cloud SDK instalado localmente:

### Instalar Google Cloud SDK (se necessário)

```powershell
# Baixe e instale do site oficial:
# https://cloud.google.com/sdk/docs/install

# Ou via Chocolatey:
choco install gcloudsdk
```

### Executar o Script

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Sincronizar dados existentes
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sincronizar -UsuarioId 1

# Importar de SQLite (se você tem o arquivo)
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sqlite -Caminho "backup/db_backup.sqlite3" -UsuarioId 1

# Testar primeiro (dry-run)
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sincronizar -UsuarioId 1 -DryRun
```

## 🔄 Via Cloud Run Jobs (Automatizado)

### Criar Job Recorrente

Para executar automaticamente (ex: todo dia às 2h):

```bash
# Criar job (não executar imediatamente)
gcloud run jobs create carregar-dados-banco \
  --region=us-central1 \
  --image="gcr.io/monpec-sistema-rural/monpec:latest" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,carregar_dados_banco,--fonte,sincronizar,--usuario-id,1" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Agendar execução (Cloud Scheduler)
gcloud scheduler jobs create http carregar-dados-diario \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/monpec-sistema-rural/jobs/carregar-dados-banco:run" \
  --http-method=POST \
  --oauth-service-account-email=SERVICE_ACCOUNT_EMAIL
```

### Executar Job Manualmente

```bash
gcloud run jobs execute carregar-dados-banco --region=us-central1 --wait
```

## 🔍 Verificar Status e Logs

### Ver Status do Job

```bash
gcloud run jobs describe carregar-dados-banco --region=us-central1
```

### Ver Logs

```bash
# Últimos 50 logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=carregar-dados-banco" --limit=50 --format=json

# Logs em tempo real
gcloud logging tail "resource.type=cloud_run_job AND resource.labels.job_name=carregar-dados-banco"
```

### Ver Execuções

```bash
gcloud run jobs executions list --job=carregar-dados-banco --region=us-central1
```

## 🛠️ Troubleshooting

### Erro: "Image not found"

**Problema:** A imagem Docker não foi encontrada.

**Solução:**
```bash
# Verificar imagens disponíveis
gcloud container images list --repository=gcr.io/monpec-sistema-rural

# Se não existir, fazer build e deploy primeiro
# Veja: scripts/deploy/DEPLOY_GOOGLE_CLOUD_COMPLETO.sh
```

### Erro: "Permission denied"

**Problema:** Permissões insuficientes.

**Solução:**
```bash
# Verificar permissões
gcloud projects get-iam-policy monpec-sistema-rural

# Se necessário, adicionar permissões
gcloud projects add-iam-policy-binding monpec-sistema-rural \
  --member="user:SEU_EMAIL@gmail.com" \
  --role="roles/run.admin"
```

### Erro: "Cloud SQL connection failed"

**Problema:** Não consegue conectar ao banco.

**Solução:**
```bash
# Verificar instância do Cloud SQL
gcloud sql instances describe monpec-db

# Verificar usuário e senha
# (ajuste as variáveis no script se necessário)
```

### Job Falha com Timeout

**Problema:** O job demora muito e é interrompido.

**Solução:** Aumente o timeout:
```bash
gcloud run jobs update carregar-dados-banco \
  --region=us-central1 \
  --timeout=3600  # 1 hora
```

### Dados Não Aparecem

**Solução:**
1. Verifique os logs do job para erros
2. Verifique se o `usuario-id` está correto
3. Verifique se os dados foram realmente importados:
   ```bash
   # Conectar ao banco e verificar
   gcloud sql connect monpec-db --user=monpec_user
   ```

## 📝 Exemplos de Uso

### Exemplo 1: Sincronizar Dados Existentes (Mais Comum)

```bash
# Cloud Shell - Comando único
bash CARREGAR_DADOS_CLOUD_SHELL.sh sincronizar "" 1

# PowerShell
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sincronizar -UsuarioId 1
```

### Exemplo 2: Importar de SQLite

```bash
# Cloud Shell (após fazer upload do arquivo)
bash CARREGAR_DADOS_CLOUD_SHELL.sh sqlite "backup/db_backup.sqlite3" 1

# PowerShell
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sqlite -Caminho "backup/db_backup.sqlite3" -UsuarioId 1
```

### Exemplo 3: Importar de PostgreSQL

```bash
# Cloud Shell
bash CARREGAR_DADOS_CLOUD_SHELL.sh postgresql "host:port:database:user:password" 1

# PowerShell (ajuste os parâmetros)
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte postgresql -UsuarioId 1
```

### Exemplo 4: Testar Primeiro (Dry-Run)

```bash
# Cloud Shell
bash CARREGAR_DADOS_CLOUD_SHELL.sh sincronizar "" 1 "" "--dry-run"

# PowerShell
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sincronizar -UsuarioId 1 -DryRun
```

## 🔗 Links Úteis

- [Documentação Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs)
- [Documentação Cloud Shell](https://cloud.google.com/shell/docs)
- [Documentação do Comando Django](docs/CARREGAR_DADOS_BANCO.md)

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `gcloud logging read ...`
2. Verifique a documentação completa: `docs/CARREGAR_DADOS_BANCO.md`
3. Teste localmente primeiro: `python manage.py carregar_dados_banco --dry-run`

