# 🚀 Deploy via GitHub - Guia Rápido

Este guia mostra como fazer o deploy do MONPEC usando GitHub Actions.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Conta no GitHub
- ✅ Repositório criado no GitHub (ou acesso ao repositório existente)
- ✅ Google Cloud SDK instalado
- ✅ Service Account configurada no GCP
- ✅ Secret `GCP_SA_KEY` configurado no GitHub

---

## 🔍 Passo 1: Verificar Configuração

Execute o script de verificação:

```powershell
.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1
```

Este script verifica:
- ✅ Arquivos de workflow do GitHub Actions
- ✅ Dockerfile de produção
- ✅ Configuração do Git
- ✅ Service Account no GCP
- ✅ Secret no GitHub

---

## 🔧 Passo 2: Configurar Service Account (se necessário)

Se a Service Account não estiver configurada, execute:

```powershell
.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1
```

Este script:
1. Cria a Service Account `github-actions-deploy`
2. Atribui todas as permissões necessárias
3. Gera a chave JSON `github-actions-deploy-key.json`

---

## 🔐 Passo 3: Configurar Secret no GitHub

### Opção A: Usando GitHub CLI (Recomendado)

```powershell
# Autenticar no GitHub (se ainda não estiver)
gh auth login

# Verificar se o secret já existe
gh secret list --repo LMONCAO/Monpec_GestaoRural

# Se não existir, adicionar o secret
$keyContent = Get-Content "github-actions-deploy-key.json" -Raw
gh secret set GCP_SA_KEY --repo LMONCAO/Monpec_GestaoRural --body $keyContent
```

### Opção B: Manualmente via Interface Web

1. Abra o arquivo `github-actions-deploy-key.json` no bloco de notas
2. Copie TODO o conteúdo (desde o `{` inicial até o `}` final)
3. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
4. Clique em: **"New repository secret"**
5. Preencha:
   - **Name**: `GCP_SA_KEY` (exatamente este nome, tudo maiúsculo)
   - **Secret**: Cole o conteúdo completo do arquivo JSON
6. Clique em: **"Add secret"**

---

## 📦 Passo 4: Inicializar Repositório Git (se necessário)

Se o projeto ainda não for um repositório Git:

```powershell
# Inicializar repositório
git init

# Adicionar remote (substitua pela URL do seu repositório)
git remote add origin https://github.com/LMONCAO/Monpec_GestaoRural.git

# Verificar remote
git remote -v
```

---

## 📝 Passo 5: Fazer Commit e Push

```powershell
# Verificar status
git status

# Adicionar todos os arquivos (ou apenas os necessários)
git add .

# Ou adicionar apenas arquivos específicos:
git add .github/workflows/deploy-gcp.yml
git add Dockerfile.prod
git add *.md
git add .gitignore

# Fazer commit
git commit -m "Configurar deploy automático GitHub Actions"

# Verificar branch atual
git branch

# Fazer push para a branch principal (main ou master)
git push -u origin main
# OU
git push -u origin master
```

> **Nota**: Se você receber um erro sobre branch não existente, crie a branch primeiro:
> ```powershell
> git checkout -b main
> git push -u origin main
> ```

---

## 🚀 Passo 6: Disparar Deploy

### Opção A: Deploy Automático (Recomendado)

O deploy será disparado automaticamente quando você fizer push para `main` ou `master`.

### Opção B: Deploy Manual via GitHub UI

1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/actions
2. No menu lateral, selecione **🚀 Deploy Automático para Google Cloud Run**
3. Clique em **Run workflow**
4. Selecione a branch (`main` ou `master`)
5. Clique em **Run workflow**

---

## 📊 Passo 7: Monitorar o Deploy

1. Acesse a aba **Actions** no GitHub: https://github.com/LMONCAO/Monpec_GestaoRural/actions
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

## ✅ Verificar Status do Deploy

Execute o script para verificar o status:

```powershell
.\VERIFICAR_STATUS_GITHUB_ACTIONS.ps1
```

Ou acesse diretamente:
- **GitHub Actions**: https://github.com/LMONCAO/Monpec_GestaoRural/actions
- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/monpec

---

## 🆘 Troubleshooting

### Erro: "Secret GCP_SA_KEY not found"

**Solução**: Configure o secret no GitHub seguindo o [Passo 3](#-passo-3-configurar-secret-no-github)

### Erro: "Permission denied" ou "403 Forbidden"

**Solução**: 
1. Execute: `.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1`
2. Verifique se todas as roles foram atribuídas
3. Aguarde alguns minutos para as permissões serem propagadas

### Erro: "Project not found"

**Solução**: 
1. Verifique o projeto: `gcloud projects list`
2. Verifique o PROJECT_ID no workflow (deve ser `monpec-sistema-rural`)
3. Certifique-se de que a service account pertence ao projeto correto

### Erro: "Dockerfile.prod not found"

**Solução**: 
1. Certifique-se de que `Dockerfile.prod` existe na raiz do repositório
2. Faça commit e push do arquivo

### Build falha

**Solução**: 
1. Verifique os logs do build no Cloud Build Console
2. Teste o build localmente: `docker build -f Dockerfile.prod -t teste .`
3. Verifique se todas as dependências estão corretas no `requirements_producao.txt`

### Deploy falha - Serviço não inicia

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
- [ ] Repositório Git inicializado e conectado ao GitHub
- [ ] Código foi feito push para o GitHub
- [ ] Primeiro deploy executado com sucesso
- [ ] Variáveis de ambiente configuradas no Cloud Run (se necessário)
- [ ] Serviço está funcionando e acessível

---

## 🎉 Pronto!

Agora, sempre que você fizer push para a branch `main` ou `master`, o deploy será feito automaticamente no Google Cloud Run!

Para verificar o status do deploy, execute:

```powershell
.\VERIFICAR_STATUS_GITHUB_ACTIONS.ps1
```

---

**Última atualização**: Dezembro 2025








