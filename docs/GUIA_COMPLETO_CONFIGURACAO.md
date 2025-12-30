# 🚀 GUIA COMPLETO - CONFIGURAÇÃO DO DEPLOY AUTOMÁTICO

Este guia completo explica como configurar o deploy automático do MONPEC para o Google Cloud Run usando GitHub Actions.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Verificação Inicial](#verificação-inicial)
3. [Configurar Service Account no GCP](#configurar-service-account-no-gcp)
4. [Configurar Secret no GitHub](#configurar-secret-no-github)
5. [Verificar Configuração](#verificar-configuração)
6. [Testar Deploy](#testar-deploy)
7. [Troubleshooting](#troubleshooting)

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Conta no GitHub com acesso ao repositório `LMONCAO/Monpec_GestaoRural`
- ✅ Projeto no Google Cloud Platform chamado `monpec-sistema-rural`
- ✅ Acesso administrativo ao projeto GCP
- ✅ Google Cloud SDK instalado ([Download](https://cloud.google.com/sdk/docs/install))
- ✅ GitHub CLI instalado (opcional, mas recomendado) ([Download](https://cli.github.com/))

---

## 🔍 Verificação Inicial

Execute o script de verificação completa:

```powershell
.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1
```

Este script verifica:
- ✅ Arquivos de workflow do GitHub Actions
- ✅ Dockerfile de produção
- ✅ Configuração do Git
- ✅ Ferramentas instaladas (gh, gcloud)
- ✅ Service Account no GCP
- ✅ Secret no GitHub

---

## 🔧 Configurar Service Account no GCP

### Opção 1: Script Automático (Recomendado)

Execute o script PowerShell:

```powershell
.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1
```

O script irá:
1. ✅ Verificar autenticação no Google Cloud
2. ✅ Configurar o projeto `monpec-sistema-rural`
3. ✅ Criar a Service Account `github-actions-deploy`
4. ✅ Atribuir todas as permissões necessárias
5. ✅ Gerar a chave JSON `github-actions-deploy-key.json`

### Opção 2: Manual via Console

1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/)
2. Selecione o projeto `monpec-sistema-rural`
3. Vá em **IAM & Admin** > **Service Accounts**
4. Clique em **+ CREATE SERVICE ACCOUNT**
5. Preencha:
   - **Service account name**: `github-actions-deploy`
   - **Description**: `Service account para deploy automático via GitHub Actions`
6. Clique em **CREATE AND CONTINUE**
7. Adicione as seguintes roles:
   - `Cloud Run Admin`
   - `Service Account User`
   - `Cloud Build Editor`
   - `Storage Admin`
   - `Cloud SQL Client` (se usar Cloud SQL)
8. Clique em **DONE**
9. Na lista, clique na Service Account criada
10. Vá na aba **KEYS**
11. Clique em **ADD KEY** > **Create new key**
12. Selecione **JSON** e clique em **CREATE**
13. O arquivo será baixado automaticamente

---

## 🔐 Configurar Secret no GitHub

### Opção 1: Verificar se já está configurado

Execute o script:

```powershell
.\VERIFICAR_SECRET_GITHUB.ps1
```

### Opção 2: Configurar manualmente

1. **Abra o arquivo JSON** que você baixou (`github-actions-deploy-key.json`)
2. **Copie TODO o conteúdo** (desde o `{` inicial até o `}` final)
3. **Acesse**: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
4. **Clique em**: "New repository secret"
5. **Preencha**:
   - **Name**: `GCP_SA_KEY` (exatamente este nome, tudo maiúsculo)
   - **Secret**: Cole o conteúdo completo do arquivo JSON
6. **Clique em**: "Add secret"

> ⚠️ **IMPORTANTE**: O nome do secret deve ser exatamente `GCP_SA_KEY` (sem espaços, tudo maiúsculo)

---

## ✅ Verificar Configuração

Execute novamente o script de verificação:

```powershell
.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1
```

Todos os itens devem estar marcados com ✅.

---

## 🚀 Testar Deploy

### Opção 1: Push Automático

Faça qualquer alteração e faça push:

```powershell
git add .
git commit -m "Teste de deploy automático"
git push origin master
```

O deploy será iniciado automaticamente!

### Opção 2: Execução Manual via GitHub UI

1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/actions
2. No menu lateral, selecione **🚀 Deploy Automático para Google Cloud Run**
3. Clique em **Run workflow**
4. Selecione a branch `master`
5. Clique em **Run workflow**

### Monitorar o Deploy

1. Acesse a aba **Actions** no GitHub
2. Clique na execução do workflow em andamento
3. Você verá todos os passos sendo executados:
   - 📥 Checkout do código
   - 🔐 Autenticação no Google Cloud
   - ⚙️ Configurar gcloud CLI
   - 📦 Configurar projeto GCP
   - 🔨 Habilitar APIs
   - 🐳 Build da imagem Docker
   - 🚀 Deploy para Cloud Run
   - 🔄 Aplicar migrações
   - 📊 Coletar arquivos estáticos
   - ✅ Verificar status

---

## 🔍 Troubleshooting

### ❌ Erro: "Secret GCP_SA_KEY not found"

**Causa**: Secret não foi configurado no GitHub.

**Solução**:
1. Execute: `.\VERIFICAR_SECRET_GITHUB.ps1`
2. Se não estiver configurado, siga o [passo de configurar secret](#configurar-secret-no-github)

### ❌ Erro: "Permission denied" ou "403 Forbidden"

**Causa**: Service Account não tem permissões suficientes.

**Solução**:
1. Execute: `.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1`
2. Verifique se todas as roles foram atribuídas
3. Aguarde alguns minutos para as permissões serem propagadas

### ❌ Erro: "Project not found"

**Causa**: PROJECT_ID incorreto ou service account não tem acesso.

**Solução**:
1. Verifique o projeto: `gcloud projects list`
2. Verifique o PROJECT_ID no workflow (deve ser `monpec-sistema-rural`)
3. Certifique-se de que a service account pertence ao projeto correto

### ❌ Erro: "Dockerfile.prod not found"

**Causa**: Dockerfile de produção não está no repositório.

**Solução**:
1. Certifique-se de que `Dockerfile.prod` existe na raiz do repositório
2. Faça commit e push do arquivo

### ❌ Build falha

**Causa**: Problemas no `requirements.txt` ou `Dockerfile.prod`.

**Solução**:
1. Verifique os logs do build no Cloud Build Console
2. Teste o build localmente: `docker build -f Dockerfile.prod -t teste .`
3. Verifique se todas as dependências estão corretas

### ❌ Deploy falha - Serviço não inicia

**Causa**: Variáveis de ambiente faltando ou banco de dados inacessível.

**Solução**:
1. Configure todas as variáveis de ambiente no Cloud Run
2. Verifique os logs: `gcloud run services logs read monpec --region us-central1`
3. Certifique-se de que o banco de dados está acessível

---

## 📚 Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `VERIFICAR_CONFIGURACAO_COMPLETA.ps1` | Verifica toda a configuração |
| `CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1` | Cria e configura Service Account no GCP |
| `VERIFICAR_SECRET_GITHUB.ps1` | Verifica se o secret está configurado |
| `VERIFICAR_STATUS_GITHUB_ACTIONS.ps1` | Verifica status do deploy no GitHub Actions |

---

## 🔗 Links Úteis

- **GitHub Actions**: https://github.com/LMONCAO/Monpec_GestaoRural/actions
- **GitHub Secrets**: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
- **Google Cloud Console**: https://console.cloud.google.com/run
- **Service Accounts**: https://console.cloud.google.com/iam-admin/serviceaccounts
- **Cloud Run**: https://console.cloud.google.com/run/detail/us-central1/monpec

---

## ✅ Checklist Final

Use este checklist para garantir que tudo está configurado:

- [ ] Service Account `github-actions-deploy` criada no GCP
- [ ] Todas as permissões atribuídas à Service Account
- [ ] Chave JSON baixada e guardada em local seguro
- [ ] Secret `GCP_SA_KEY` configurado no GitHub
- [ ] Workflow `.github/workflows/deploy-gcp.yml` existe no repositório
- [ ] Dockerfile.prod existe na raiz do repositório
- [ ] Código foi feito push para o GitHub
- [ ] Primeiro deploy executado com sucesso
- [ ] Variáveis de ambiente configuradas no Cloud Run (se necessário)
- [ ] Serviço está funcionando e acessível

---

## 🎉 Pronto!

Agora, sempre que você fizer push para a branch `master` ou `main`, o deploy será feito automaticamente no Google Cloud Run!

Para verificar o status do deploy, execute:

```powershell
.\VERIFICAR_STATUS_GITHUB_ACTIONS.ps1
```

---

**Última atualização**: Dezembro 2025








