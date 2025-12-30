# 🚀 Deploy Automático GitHub Actions → Google Cloud

Este projeto está configurado para fazer deploy automático no Google Cloud Run sempre que houver push para a branch `main` ou `master`.

## ⚡ Início Rápido

### 1. Configurar Service Account no GCP

Execute no terminal (com `gcloud` autenticado):

```bash
# Criar service account
gcloud iam service-accounts create github-actions-deploy \
    --display-name="GitHub Actions Deploy" \
    --project=monpec-sistema-rural

# Atribuir permissões necessárias
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

### 2. Configurar Secret no GitHub

1. Acesse: https://github.com/LMONCAO/monpec/settings/secrets/actions
2. Clique em **New repository secret**
3. Nome: `GCP_SA_KEY`
4. Valor: Cole o conteúdo completo do arquivo `github-actions-key.json`
5. Clique em **Add secret**

### 3. Fazer Push e Testar

```bash
git add .
git commit -m "Configurar GitHub Actions para deploy automático"
git push origin main
```

Pronto! O deploy será executado automaticamente. Você pode acompanhar em:
**Actions** → https://github.com/LMONCAO/monpec/actions

## 📁 Arquivos Criados

- `.github/workflows/deploy-gcp.yml` - Workflow completo com migrações e collectstatic
- `.github/workflows/deploy-gcp-simple.yml` - Workflow simplificado (recomendado para começar)
- `.github/GITHUB_ACTIONS_SETUP.md` - Documentação detalhada

## 🔄 Como Funciona

1. **Push para main/master** → GitHub Actions detecta mudanças
2. **Build** → Cria imagem Docker usando `Dockerfile.prod`
3. **Deploy** → Faz deploy no Cloud Run
4. **Verificação** → Exibe URL do serviço

## ⚙️ Configurações

As configurações principais estão em `.github/workflows/deploy-gcp-simple.yml`:

```yaml
PROJECT_ID: monpec-sistema-rural
SERVICE_NAME: monpec
REGION: us-central1
```

## 🔍 Ver Logs

- **GitHub Actions**: https://github.com/LMONCAO/monpec/actions
- **Cloud Build**: https://console.cloud.google.com/cloud-build/builds?project=monpec-sistema-rural
- **Cloud Run**: https://console.cloud.google.com/run?project=monpec-sistema-rural

## 📚 Documentação Completa

Para mais detalhes, veja: `.github/GITHUB_ACTIONS_SETUP.md`








