# ⚡ Resumo Rápido: Sincronizar GitHub com Google Cloud

## 🎯 O que foi criado:

1. ✅ **Workflow do GitHub Actions** (`.github/workflows/deploy-google-cloud.yml`)
   - Faz deploy automático quando você faz push no branch `main` ou `master`
   - Build automático da imagem Docker
   - Deploy automático no Google Cloud Run

2. ✅ **Guia Completo** (`GUIA_SINCRONIZAR_GITHUB_GCLOUD.md`)
   - Passo a passo detalhado de configuração
   - Troubleshooting
   - Configurações avançadas

## 🚀 Configuração Rápida (5 minutos):

### 1. Criar Service Account no Google Cloud
- IAM & Admin → Service Accounts → Create
- Nome: `github-actions-deploy`
- Permissões: Cloud Run Admin, Service Account User, Storage Admin, Cloud Build Editor
- Criar chave JSON e baixar

### 2. Adicionar Secrets no GitHub
Settings → Secrets and variables → Actions → New repository secret:

- `GCP_SA_KEY` → conteúdo completo do arquivo JSON baixado
- `SECRET_KEY` → `django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE`
- `DB_NAME` → `monpec_db`
- `DB_USER` → `monpec_user`
- `DB_PASSWORD` → `L6171r12@@jjms`
- `DJANGO_SUPERUSER_PASSWORD` → `L6171r12@@`

### 3. Habilitar APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 4. Fazer Push
```bash
git add .
git commit -m "Configurar CI/CD"
git push origin main
```

## ✅ Como Funciona:

1. Você faz push no GitHub → GitHub Actions detecta
2. Autentica no Google Cloud → Usa o Service Account
3. Faz build da imagem → Docker build no Cloud Build
4. Faz deploy → Atualiza Cloud Run automaticamente
5. Sistema atualizado! 🎉

## 📖 Documentação Completa:

Para mais detalhes, consulte: `GUIA_SINCRONIZAR_GITHUB_GCLOUD.md`

---

**Pronto! Agora seu projeto está sincronizado!** 🚀

