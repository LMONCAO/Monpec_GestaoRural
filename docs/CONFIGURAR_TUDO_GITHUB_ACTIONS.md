# 🚀 Guia Completo: Configurar GitHub Actions para Deploy Automático

Este guia mostra como configurar tudo automaticamente para que o GitHub faça deploy no Google Cloud sempre que você fizer push.

## ⚡ Opção 1: Script Automático (Recomendado)

### Windows (PowerShell)
```powershell
.\CONFIGURAR_GITHUB_ACTIONS.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x CONFIGURAR_GITHUB_ACTIONS.sh
./CONFIGURAR_GITHUB_ACTIONS.sh
```

O script vai:
1. ✅ Verificar se o gcloud está instalado
2. ✅ Fazer login no GCP (se necessário)
3. ✅ Criar service account no GCP
4. ✅ Atribuir todas as permissões necessárias
5. ✅ Criar chave JSON
6. ✅ Adicionar ao .gitignore
7. ✅ Mostrar instruções para adicionar o secret no GitHub

## 📝 Opção 2: Manual (Passo a Passo)

### Passo 1: Criar Service Account no GCP

Execute no terminal (com `gcloud` instalado e autenticado):

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Criar service account
gcloud iam service-accounts create github-actions-deploy \
    --display-name="GitHub Actions Deploy" \
    --description="Service account para deploy automático via GitHub Actions" \
    --project=monpec-sistema-rural

# Atribuir permissões
gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding monpec-sistema-rural \
    --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Criar e baixar chave JSON
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com \
    --project=monpec-sistema-rural
```

### Passo 2: Adicionar Secret no GitHub

1. **Acesse**: https://github.com/LMONCAO/monpec/settings/secrets/actions

2. **Clique em**: "New repository secret"

3. **Configure**:
   - **Name**: `GCP_SA_KEY`
   - **Secret**: Cole o conteúdo **COMPLETO** do arquivo `github-actions-key.json`
   - Clique em "Add secret"

### Passo 3: Fazer Commit e Push

```bash
# Adicionar arquivos do GitHub Actions
git add .github/
git add README_GITHUB_ACTIONS.md
git add CONFIGURAR_GITHUB_ACTIONS.ps1
git add CONFIGURAR_GITHUB_ACTIONS.sh
git add CONFIGURAR_TUDO_GITHUB_ACTIONS.md

# Commit
git commit -m "Adicionar GitHub Actions para deploy automático no GCP"

# Push (o deploy será executado automaticamente!)
git push origin main
```

### Passo 4: Acompanhar o Deploy

1. **GitHub Actions**: https://github.com/LMONCAO/monpec/actions
   - Você verá o workflow sendo executado em tempo real
   - Cada passo será exibido com logs detalhados

2. **Cloud Build**: https://console.cloud.google.com/cloud-build/builds?project=monpec-sistema-rural
   - Veja o progresso do build da imagem Docker

3. **Cloud Run**: https://console.cloud.google.com/run?project=monpec-sistema-rural
   - Veja o serviço sendo atualizado

## ✅ Verificar se Funcionou

Após o push, você deve ver:

1. **No GitHub Actions**:
   - ✅ Workflow "🚀 Deploy Simples para Google Cloud Run" aparecendo
   - ✅ Todos os steps executando com sucesso (marcas verdes)
   - ✅ URL do serviço exibida no final

2. **No Cloud Run**:
   - ✅ Nova revisão do serviço `monpec` criada
   - ✅ Serviço rodando com a nova imagem

3. **No site**:
   - ✅ https://monpec.com.br atualizado com as últimas mudanças

## 🔄 Como Funciona Agora

A partir de agora, **sempre que você fizer push para `main` ou `master`**:

1. 🚀 GitHub Actions detecta o push
2. 🐳 Faz build da imagem Docker usando `Dockerfile.prod`
3. 📦 Faz push da imagem para Container Registry
4. 🚀 Faz deploy no Cloud Run
5. ✅ Site atualizado automaticamente!

## 🔍 Troubleshooting

### Erro: "Permission denied" no GitHub Actions

**Solução**: Verifique se:
- O secret `GCP_SA_KEY` foi adicionado corretamente no GitHub
- A service account tem todas as permissões necessárias
- Execute os comandos de atribuição de permissões novamente

### Erro: "Project not found"

**Solução**: 
- Verifique se o `PROJECT_ID` está correto no workflow (`.github/workflows/deploy-gcp-simple.yml`)
- Certifique-se de que a service account tem acesso ao projeto

### Build falha

**Solução**:
- Verifique se o `Dockerfile.prod` existe e está correto
- Veja os logs detalhados no Cloud Build console
- Verifique se o `requirements_producao.txt` existe

### Deploy falha

**Solução**:
- Verifique os logs do Cloud Run
- Certifique-se de que as variáveis de ambiente estão configuradas
- Verifique se o banco de dados está acessível

## 📚 Arquivos Criados

- `.github/workflows/deploy-gcp-simple.yml` - Workflow simplificado (executa automaticamente)
- `.github/workflows/deploy-gcp.yml` - Workflow completo (com migrações)
- `.github/GITHUB_ACTIONS_SETUP.md` - Documentação detalhada
- `README_GITHUB_ACTIONS.md` - Guia rápido
- `CONFIGURAR_GITHUB_ACTIONS.ps1` - Script automático (Windows)
- `CONFIGURAR_GITHUB_ACTIONS.sh` - Script automático (Linux/Mac)
- `CONFIGURAR_TUDO_GITHUB_ACTIONS.md` - Este guia

## 🎯 Próximos Passos

1. ✅ Execute o script de configuração
2. ✅ Adicione o secret no GitHub
3. ✅ Faça commit e push
4. ✅ Acompanhe o deploy no GitHub Actions
5. ✅ Celebre! 🎉

## 💡 Dicas

- Você pode executar o workflow manualmente pelo GitHub (Actions → Run workflow)
- O deploy leva cerca de 5-10 minutos (principalmente o build)
- Você pode cancelar um deploy em andamento se necessário
- Os logs ficam disponíveis por 90 dias no GitHub

---

**Pronto! Agora seu site será atualizado automaticamente sempre que você fizer push! 🚀**








