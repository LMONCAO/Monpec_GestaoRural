# 🚀 Deploy Automático - PASSO A PASSO PARA FAZER AGORA

## ✅ Você já tem:
- ✅ Projeto no Google Cloud: `monpec-sistema-rural`
- ✅ Workflow configurado: `.github/workflows/deploy-gcp.yml`
- ✅ Código pronto para deploy

## 🔧 PASSO 1: Criar Service Account no Google Cloud (5 minutos)

### 1.1 No Console do GCP (onde você está agora):

1. **Clique em "IAM e admin"** no menu "Acesso rápido" (ou procure no menu lateral)

2. **Clique em "Service Accounts"** (Contas de serviço)

3. **Clique em "+ CREATE SERVICE ACCOUNT"** (Criar conta de serviço)

4. **Preencha:**
   - **Service account name**: `github-actions-deploy`
   - **Service account ID**: será preenchido automaticamente
   - **Description**: `Service account para deploy automático via GitHub Actions`

5. **Clique em "CREATE AND CONTINUE"**

6. **Adicione as seguintes roles** (clique em "ADD ANOTHER ROLE" para cada uma):
   - ✅ `Cloud Run Admin` → Pesquise "Cloud Run Admin" e selecione
   - ✅ `Service Account User` → Pesquise "Service Account User" e selecione
   - ✅ `Cloud Build Editor` → Pesquise "Cloud Build Editor" e selecione
   - ✅ `Storage Admin` → Pesquise "Storage Admin" e selecione
   - ✅ `Cloud SQL Client` → Pesquise "Cloud SQL Client" e selecione (se usar banco Cloud SQL)

7. **Clique em "CONTINUE"** e depois **"DONE"**

### 1.2 Criar Chave JSON:

1. **Na lista de Service Accounts**, clique na que você criou (`github-actions-deploy`)

2. **Vá na aba "KEYS"** (Chaves)

3. **Clique em "ADD KEY"** → **"Create new key"**

4. **Selecione "JSON"**

5. **Clique em "CREATE"**

> ⚠️ **IMPORTANTE**: O arquivo JSON será baixado automaticamente. **ABRA O ARQUIVO** e copie TODO o conteúdo (desde o `{` inicial até o `}` final). Você vai precisar no próximo passo!

---

## 🔐 PASSO 2: Configurar Secret no GitHub (3 minutos)

### 2.1 Acessar Configurações do Repositório:

1. **Abra uma nova aba** e acesse: https://github.com/LMONCAO/monpec

2. **Clique em "Settings"** (Configurações) - no topo do repositório

3. **No menu lateral esquerdo**, vá em:
   - **Secrets and variables** → **Actions**

### 2.2 Adicionar Secret:

1. **Clique em "New repository secret"** (Novo secret do repositório)

2. **Preencha:**
   - **Name**: `GCP_SA_KEY` (exatamente este nome, tudo maiúsculo)
   - **Secret**: Cole TODO o conteúdo do arquivo JSON que você copiou no Passo 1.2

3. **Clique em "Add secret"**

> ✅ **Verificação**: Você deve ver `GCP_SA_KEY` na lista de secrets (com um ícone de olho fechado ao lado)

---

## 📤 PASSO 3: Fazer Push do Workflow para o GitHub (2 minutos)

### 3.1 Abrir Terminal/PowerShell:

No seu computador, abra o PowerShell ou Terminal na pasta do projeto:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

### 3.2 Verificar Status do Git:

```powershell
git status
```

### 3.3 Adicionar e Fazer Commit:

```powershell
git add .github/workflows/deploy-gcp.yml
git add CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md
git add QUICK_START_DEPLOY.md
git commit -m "Configurar deploy automático GitHub Actions para Google Cloud Run"
```

### 3.4 Fazer Push:

```powershell
git push origin main
```

(Se sua branch for `master`, use: `git push origin master`)

---

## ✅ PASSO 4: Verificar e Testar o Deploy (5 minutos)

### 4.1 Verificar no GitHub:

1. **Acesse**: https://github.com/LMONCAO/monpec/actions

2. **Você deve ver** o workflow "🚀 Deploy Automático para Google Cloud Run" executando

3. **Clique no workflow** para ver os detalhes em tempo real

### 4.2 Ou Executar Manualmente:

1. **Acesse**: https://github.com/LMONCAO/monpec/actions

2. **Selecione** o workflow "🚀 Deploy Automático para Google Cloud Run"

3. **Clique em "Run workflow"** (Executar workflow)

4. **Selecione a branch** (`main` ou `master`)

5. **Clique em "Run workflow"**

---

## 🔍 PASSO 5: Verificar Deploy no Google Cloud (2 minutos)

### 5.1 No Console do GCP:

1. **Volte para o Console do Google Cloud**

2. **No menu**, procure por **"Cloud Run"** e clique

3. **Você deve ver** o serviço `monpec` sendo criado/atualizado

4. **Clique no serviço** para ver detalhes

### 5.2 Ver URL do Serviço:

Após o deploy concluir, você verá a URL do serviço (algo como):
- `https://monpec-xxxxx.us-central1.run.app`

---

## ⚙️ PASSO 6: Configurar Variáveis de Ambiente (Importante!)

Após o primeiro deploy, você PRECISA configurar as variáveis de ambiente no Cloud Run:

### 6.1 No Console do Cloud Run:

1. **Clique no serviço `monpec`**

2. **Clique em "EDIT & DEPLOY NEW REVISION"**

3. **Vá até a seção "Variables & Secrets"** (Variáveis e Secrets)

4. **Clique em "ADD VARIABLE"** e adicione cada uma:

   - `DJANGO_SETTINGS_MODULE` = `sistema_rural.settings_gcp`
   - `DEBUG` = `False`
   - `DB_HOST` = (seu host do banco de dados)
   - `DB_NAME` = (nome do banco, exemplo: `monpec_db`)
   - `DB_USER` = (usuário do banco)
   - `DB_PASSWORD` = (senha do banco)
   - `SECRET_KEY` = (sua chave secreta do Django)
   - E outras variáveis que seu sistema precisa

5. **Clique em "DEPLOY"** no final da página

---

## ✅ Checklist Rápido

Use este checklist para não esquecer nada:

- [ ] Service account `github-actions-deploy` criada no GCP
- [ ] Todas as 5 permissões atribuídas (Cloud Run Admin, Service Account User, Cloud Build Editor, Storage Admin, Cloud SQL Client)
- [ ] Chave JSON baixada e conteúdo copiado
- [ ] Secret `GCP_SA_KEY` configurado no GitHub com o JSON completo
- [ ] Código commitado e push feito para o GitHub
- [ ] Workflow executado (automático ou manual)
- [ ] Deploy concluído com sucesso no Cloud Run
- [ ] Variáveis de ambiente configuradas no Cloud Run

---

## 🆘 Se Algo Der Errado

### ❌ Erro: "Permission denied"
- Verifique se todas as 5 permissões foram adicionadas à service account
- Aguarde 2-3 minutos (permissões levam tempo para propagar)

### ❌ Erro: "Secret GCP_SA_KEY not found"
- Verifique se o secret foi criado exatamente com este nome (tudo maiúsculo)
- Certifique-se de ter colado TODO o conteúdo do JSON

### ❌ Build falha
- Verifique os logs no Cloud Build Console
- Certifique-se de que `Dockerfile.prod` existe na raiz do projeto

### ❌ Deploy falha - Serviço não inicia
- Configure as variáveis de ambiente (Passo 6)
- Verifique os logs: Cloud Run → monpec → Logs

---

## 🎉 Pronto!

Depois disso, **todo push para `main` ou `master` fará deploy automático** no Google Cloud Run!

Para atualizar o sistema no futuro, basta fazer:
```powershell
git add .
git commit -m "Atualização do sistema"
git push origin main
```

E o deploy será automático! 🚀








