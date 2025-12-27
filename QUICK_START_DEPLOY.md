# ⚡ Quick Start - Deploy Automático GitHub → Google Cloud

## 🎯 Resumo Rápido

Para configurar o deploy automático do MONPEC para o Google Cloud Run via GitHub Actions:

## 📋 Checklist Rápido

1. **✅ Criar Service Account no GCP**
   - Console GCP → IAM & Admin → Service Accounts → CREATE
   - Nome: `github-actions-deploy`
   - Permissões: Cloud Run Admin, Service Account User, Cloud Build Editor, Storage Admin

2. **✅ Baixar Chave JSON**
   - Service Account → Keys → ADD KEY → JSON → CREATE
   - Guarde o arquivo em local seguro

3. **✅ Configurar Secret no GitHub**
   - Repositório → Settings → Secrets and variables → Actions → New secret
   - Name: `GCP_SA_KEY`
   - Value: Cole TODO o conteúdo do arquivo JSON

4. **✅ Fazer Push do Workflow**
   ```bash
   git add .github/workflows/deploy-gcp.yml
   git commit -m "Configurar deploy automático"
   git push origin main
   ```

5. **✅ Testar**
   - Faça qualquer alteração e push para `main`
   - Ou execute manualmente: GitHub → Actions → Run workflow

## 📚 Guia Completo

Para instruções detalhadas, consulte: [`CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md`](CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md)

## ⚙️ Configurações do Workflow

O workflow está configurado em `.github/workflows/deploy-gcp.yml`:

- **PROJECT_ID**: `monpec-sistema-rural`
- **SERVICE_NAME**: `monpec`
- **REGION**: `us-central1`
- **Triggers**: Push para `main`/`master` ou execução manual

## 🚀 Após o Deploy

Lembre-se de configurar as variáveis de ambiente no Cloud Run:

1. Acesse: https://console.cloud.google.com/run
2. Clique no serviço `monpec`
3. EDIT → Variables & Secrets
4. Adicione variáveis necessárias (DB_HOST, DB_NAME, etc.)

---

**Pronto!** Agora todo push para `main` fará deploy automático! 🎉
