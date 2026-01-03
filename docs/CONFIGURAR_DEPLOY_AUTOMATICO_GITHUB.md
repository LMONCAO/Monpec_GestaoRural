# 🚀 Configuração do Deploy Automático - GitHub Actions para Google Cloud

Este guia explica passo a passo como configurar o deploy automático do MONPEC para o Google Cloud Run usando GitHub Actions.

## 📋 Pré-requisitos

1. ✅ Conta no GitHub com acesso ao repositório `LMONCAO/monpec`
2. ✅ Projeto no Google Cloud Platform chamado `monpec-sistema-rural`
3. ✅ Acesso administrativo ao projeto GCP
4. ✅ Repositório GitHub já criado e código enviado

## 🔧 Passo 1: Criar Service Account no Google Cloud

### 1.1 Acessar o Console do GCP

1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/)
2. Certifique-se de que o projeto `monpec-sistema-rural` está selecionado

### 1.2 Criar Service Account

1. No menu lateral, vá em **IAM & Admin** > **Service Accounts**
2. Clique em **+ CREATE SERVICE ACCOUNT**
3. Preencha os dados:
   - **Service account name**: `github-actions-deploy`
   - **Service account ID**: será preenchido automaticamente
   - **Description**: `Service account para deploy automático via GitHub Actions`
4. Clique em **CREATE AND CONTINUE**

### 1.3 Atribuir Permissões

Adicione as seguintes roles (uma de cada vez, clicando em **ADD ANOTHER ROLE**):

- ✅ **Cloud Run Admin** (`roles/run.admin`) - Para fazer deploy e gerenciar serviços
- ✅ **Service Account User** (`roles/iam.serviceAccountUser`) - Para executar jobs do Cloud Run
- ✅ **Cloud Build Editor** (`roles/cloudbuild.builds.editor`) - Para fazer build de imagens
- ✅ **Storage Admin** (`roles/storage.admin`) - Para acessar Container Registry
- ✅ **Cloud SQL Client** (`roles/cloudsql.client`) - Se você usar Cloud SQL

Clique em **CONTINUE** e depois em **DONE**

## 🔑 Passo 2: Criar Chave JSON

### 2.1 Gerar Chave

1. Na lista de Service Accounts, clique na que você acabou de criar (`github-actions-deploy`)
2. Vá na aba **KEYS**
3. Clique em **ADD KEY** > **Create new key**
4. Selecione o formato **JSON**
5. Clique em **CREATE**

> ⚠️ **IMPORTANTE**: O arquivo JSON será baixado automaticamente. **Guarde este arquivo em local seguro**, pois ele contém credenciais sensíveis. Você não poderá baixá-lo novamente depois.

### 2.2 Verificar o Arquivo

O arquivo JSON deve ter uma estrutura similar a esta:

```json
{
  "type": "service_account",
  "project_id": "monpec-sistema-rural",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

## 🔐 Passo 3: Configurar Secret no GitHub

### 3.1 Acessar Configurações do Repositório

1. Acesse seu repositório no GitHub: https://github.com/LMONCAO/monpec
2. Clique em **Settings** (Configurações)
3. No menu lateral esquerdo, vá em **Secrets and variables** > **Actions**

### 3.2 Adicionar Secret

1. Clique em **New repository secret**
2. Preencha:
   - **Name**: `GCP_SA_KEY` (exatamente este nome, sem espaços)
   - **Secret**: Abra o arquivo JSON que você baixou, copie **TODO O CONTEÚDO** do arquivo (desde o `{` inicial até o `}` final) e cole aqui
3. Clique em **Add secret**

> ✅ **Verificação**: Você deve ver `GCP_SA_KEY` na lista de secrets com o ícone de olho fechado ao lado.

## 📝 Passo 4: Verificar Workflow do GitHub Actions

O workflow já está configurado no arquivo `.github/workflows/deploy-gcp.yml` com as seguintes configurações:

- **PROJECT_ID**: `monpec-sistema-rural`
- **SERVICE_NAME**: `monpec`
- **REGION**: `us-central1`

### 4.1 Verificar o Arquivo do Workflow

Se precisar ajustar, edite o arquivo `.github/workflows/deploy-gcp.yml` na raiz do repositório.

## 🚀 Passo 5: Fazer Push do Workflow para o GitHub

Se você ainda não fez push do arquivo de workflow, faça agora:

```bash
git add .github/workflows/deploy-gcp.yml
git commit -m "Configurar deploy automático para Google Cloud Run"
git push origin main
```

Ou se sua branch principal for `master`:

```bash
git push origin master
```

## ✅ Passo 6: Testar o Deploy

### Opção 1: Deploy Automático (Push para main/master)

Faça qualquer alteração no código e faça push:

```bash
git add .
git commit -m "Teste de deploy automático"
git push origin main
```

### Opção 2: Execução Manual via GitHub UI

1. Acesse seu repositório no GitHub
2. Clique na aba **Actions**
3. No menu lateral, selecione o workflow **🚀 Deploy Automático para Google Cloud Run**
4. Clique em **Run workflow**
5. Selecione a branch (main ou master)
6. Clique em **Run workflow**

## 📊 Passo 7: Monitorar o Deploy

### 7.1 No GitHub

1. Acesse a aba **Actions** no repositório
2. Clique na execução do workflow em andamento
3. Você verá todos os passos sendo executados em tempo real:
   - 📥 Checkout do código
   - 🔐 Autenticação no Google Cloud
   - ⚙️ Configurar gcloud CLI
   - 📦 Configurar projeto GCP
   - 🔨 Habilitar APIs
   - 🐳 Build da imagem Docker
   - 🚀 Deploy para Cloud Run
   - 🔄 Aplicar migrações (opcional)
   - 📊 Coletar arquivos estáticos (opcional)
   - ✅ Verificar status

### 7.2 No Google Cloud Console

1. Acesse o [Console do Cloud Run](https://console.cloud.google.com/run)
2. Selecione o projeto `monpec-sistema-rural`
3. Você verá o serviço `monpec` sendo atualizado ou criado

## ⚙️ Passo 8: Configurar Variáveis de Ambiente no Cloud Run

O workflow faz o deploy básico, mas você precisa configurar variáveis de ambiente e secrets manualmente no Cloud Run.

### 8.1 Via Console do GCP

1. Acesse o [Console do Cloud Run](https://console.cloud.google.com/run)
2. Clique no serviço `monpec`
3. Clique em **EDIT & DEPLOY NEW REVISION**
4. Vá até a seção **Variables & Secrets**
5. Adicione as variáveis de ambiente necessárias (exemplos):
   - `DJANGO_SETTINGS_MODULE` = `sistema_rural.settings_gcp`
   - `DEBUG` = `False`
   - `DB_HOST` = (seu host do banco)
   - `DB_NAME` = (nome do banco)
   - `DB_USER` = (usuário do banco)
   - E outras variáveis que seu Django precisa

### 8.2 Via gcloud CLI (Alternativa)

```bash
gcloud run services update monpec \
  --region us-central1 \
  --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_HOST=seu-host,DB_NAME=seu-banco,DB_USER=seu-usuario"
```

### 8.3 Usando Secrets do GCP (Recomendado para Senhas)

Para informações sensíveis como senhas, use Secrets do GCP:

```bash
# Criar secret
echo -n "sua-senha-secreta" | gcloud secrets create DB_PASSWORD --data-file=-

# Dar permissão para o Cloud Run acessar o secret
gcloud secrets add-iam-policy-binding DB_PASSWORD \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Atualizar serviço para usar o secret
gcloud run services update monpec \
  --region us-central1 \
  --update-secrets "DB_PASSWORD=DB_PASSWORD:latest"
```

## 🔍 Troubleshooting (Solução de Problemas)

### ❌ Erro: "Permission denied" ou "403 Forbidden"

**Causa**: Service account não tem permissões suficientes.

**Solução**:
1. Verifique se todas as roles foram adicionadas (Passo 1.3)
2. Aguarde alguns minutos para as permissões serem propagadas
3. Verifique se o secret `GCP_SA_KEY` está configurado corretamente

### ❌ Erro: "Project not found" ou "Project monpec-sistema-rural not found"

**Causa**: PROJECT_ID incorreto ou service account não tem acesso ao projeto.

**Solução**:
1. Verifique se o projeto existe: `gcloud projects list`
2. Verifique o PROJECT_ID no workflow (deve ser `monpec-sistema-rural`)
3. Certifique-se de que a service account pertence ao projeto correto

### ❌ Erro: "Secret GCP_SA_KEY not found"

**Causa**: Secret não foi configurado no GitHub.

**Solução**:
1. Acesse Settings > Secrets and variables > Actions
2. Verifique se `GCP_SA_KEY` existe
3. Se não existir, crie seguindo o Passo 3

### ❌ Erro: "Dockerfile.prod not found"

**Causa**: Dockerfile de produção não está no repositório.

**Solução**:
1. Certifique-se de que `Dockerfile.prod` existe na raiz do repositório
2. Faça commit e push do arquivo

### ❌ Build falha com erro de dependências

**Causa**: Problemas no `requirements.txt` ou `requirements_producao.txt`.

**Solução**:
1. Verifique os logs do build no Cloud Build Console
2. Teste o build localmente: `docker build -f Dockerfile.prod -t teste .`
3. Verifique se todas as dependências estão corretas

### ❌ Deploy falha - Serviço não inicia

**Causa**: Variáveis de ambiente faltando ou banco de dados inacessível.

**Solução**:
1. Configure todas as variáveis de ambiente (Passo 8)
2. Verifique os logs do Cloud Run: `gcloud run services logs read monpec --region us-central1`
3. Certifique-se de que o banco de dados está acessível

## 📚 Recursos Adicionais

- [Documentação do GitHub Actions](https://docs.github.com/en/actions)
- [Documentação do Google Cloud Run](https://cloud.google.com/run/docs)
- [Google GitHub Actions](https://github.com/google-github-actions)
- [Workload Identity Federation (Método mais seguro)](https://github.com/google-github-actions/auth#setting-up-workload-identity-federation) - Alternativa futura ao JSON key

## ✅ Checklist Final

Use este checklist para garantir que tudo está configurado:

- [ ] Service account `github-actions-deploy` criada no GCP
- [ ] Todas as permissões atribuídas à service account:
  - [ ] Cloud Run Admin
  - [ ] Service Account User
  - [ ] Cloud Build Editor
  - [ ] Storage Admin
  - [ ] Cloud SQL Client (se necessário)
- [ ] Chave JSON baixada e guardada em local seguro
- [ ] Secret `GCP_SA_KEY` configurado no GitHub com o conteúdo completo do JSON
- [ ] Workflow `.github/workflows/deploy-gcp.yml` existe no repositório
- [ ] Código foi feito push para o GitHub
- [ ] Primeiro deploy executado com sucesso (via push ou manualmente)
- [ ] Variáveis de ambiente configuradas no Cloud Run
- [ ] Secrets configurados no GCP (se necessário)
- [ ] Serviço está funcionando e acessível

## 🎉 Pronto!

Agora, sempre que você fizer push para a branch `main` ou `master`, o deploy será feito automaticamente no Google Cloud Run!

---

**Nota**: O workflow está configurado para executar automaticamente apenas em push para `main` ou `master`. Para outras branches, você pode executar manualmente via GitHub Actions UI ou ajustar o workflow para incluir outras branches.







