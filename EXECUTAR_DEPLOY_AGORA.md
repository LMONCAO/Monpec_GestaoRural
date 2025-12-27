# 🚀 EXECUTAR DEPLOY AGORA - Guia Rápido

## ✅ Tudo está pronto! Siga estes passos:

### 📋 Pré-requisitos

1. **Google Cloud SDK instalado**
   - Verificar: `gcloud --version`
   - Se não tiver: https://cloud.google.com/sdk/docs/install

2. **Autenticado no Google Cloud**
   ```powershell
   gcloud auth login
   ```

3. **Projeto configurado**
   ```powershell
   gcloud config set project SEU_PROJECT_ID
   ```

### 🚀 Opção 1: Deploy Automático Completo (RECOMENDADO)

Execute este comando no PowerShell:

```powershell
.\DEPLOY_TUDO_AGORA.ps1
```

Este script fará:
- ✅ Build da imagem Docker
- ✅ Deploy no Cloud Run
- ✅ Configuração de variáveis (se você fornecer)
- ✅ Aplicação de migrações (opcional)
- ✅ Criação de superusuário (opcional)

### 🚀 Opção 2: Deploy Passo a Passo

#### Passo 1: Deploy Básico
```powershell
.\DEPLOY_AGORA.ps1
```

#### Passo 2: Configurar Variáveis de Ambiente
Edite o arquivo `CONFIGURAR_VARIAVEIS.ps1` e defina:
- `$SecretKey` - Chave secreta do Django
- `$DbPassword` - Senha do banco de dados
- `$CloudSqlConnection` - Nome da conexão Cloud SQL

Depois execute:
```powershell
.\CONFIGURAR_VARIAVEIS.ps1
```

Ou configure manualmente:
```powershell
gcloud run services update monpec `
  --region us-central1 `
  --update-env-vars="SECRET_KEY=SUA_SECRET_KEY" `
  --update-env-vars="DEBUG=False" `
  --update-env-vars="DB_NAME=monpec_db" `
  --update-env-vars="DB_USER=monpec_user" `
  --update-env-vars="DB_PASSWORD=SUA_SENHA" `
  --update-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME"
```

#### Passo 3: Aplicar Migrações
```powershell
.\APLICAR_MIGRACOES.ps1
```

#### Passo 4: Criar Superusuário
```powershell
.\CRIAR_SUPERUSUARIO.ps1
```

### 📝 Variáveis de Ambiente Necessárias

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `SECRET_KEY` | Chave secreta do Django | ✅ Sim |
| `DEBUG` | Modo debug (False) | ✅ Sim |
| `DB_NAME` | Nome do banco | ✅ Sim |
| `DB_USER` | Usuário do banco | ✅ Sim |
| `DB_PASSWORD` | Senha do banco | ✅ Sim |
| `CLOUD_SQL_CONNECTION_NAME` | Conexão Cloud SQL | ✅ Sim |

### 🗄️ Se ainda não tem banco de dados configurado:

```powershell
# 1. Criar instância Cloud SQL
gcloud sql instances create monpec-db `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=SUA_SENHA_ROOT

# 2. Criar banco e usuário
gcloud sql connect monpec-db --user=postgres
# No PostgreSQL:
# CREATE DATABASE monpec_db;
# CREATE USER monpec_user WITH PASSWORD 'SUA_SENHA';
# GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;
# \q

# 3. Obter connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"

# 4. Conectar Cloud Run ao Cloud SQL
gcloud run services update monpec `
  --region us-central1 `
  --add-cloudsql-instances=PROJECT_ID:REGION:monpec-db
```

### 🔍 Verificar Deploy

```powershell
# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Ver URL
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

# Ver status
gcloud run services describe monpec --region us-central1
```

### 🐛 Problemas?

1. **Erro 500**: Verifique os logs e variáveis de ambiente
2. **Erro de conexão com banco**: Verifique `CLOUD_SQL_CONNECTION_NAME`
3. **Erro de build**: Verifique se o Dockerfile.prod está correto

### 📚 Documentação Completa

- `GUIA_DEPLOY_RAPIDO.md` - Guia detalhado
- `DEPLOY_GCP_COMPLETO.md` - Documentação completa

---

**Pronto para começar? Execute:**
```powershell
.\DEPLOY_TUDO_AGORA.ps1
```









