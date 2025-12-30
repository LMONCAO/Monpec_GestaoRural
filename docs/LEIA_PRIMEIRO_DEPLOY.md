# 🎯 LEIA PRIMEIRO - Deploy Automático Configurado!

## ✅ O que já está pronto:

1. ✅ **Workflow do GitHub Actions** configurado (`.github/workflows/deploy-gcp.yml`)
2. ✅ **Documentação completa** criada
3. ✅ **Código pronto** para deploy automático

## 🚀 O QUE VOCÊ PRECISA FAZER AGORA (3 passos):

### ⚡ PASSO 1: Criar Service Account no Google Cloud (5 min)

**Você está no Console do GCP agora! Siga estes passos:**

1. Clique em **"IAM e admin"** no menu
2. Clique em **"Service Accounts"**
3. Clique em **"+ CREATE SERVICE ACCOUNT"**
4. Nome: `github-actions-deploy`
5. Adicione estas 5 permissões:
   - ✅ Cloud Run Admin
   - ✅ Service Account User  
   - ✅ Cloud Build Editor
   - ✅ Storage Admin
   - ✅ Cloud SQL Client
6. Crie uma **chave JSON** e baixe o arquivo

📋 **Guia detalhado**: `DEPLOY_AGORA_PASSO_A_PASSO.md` (Passo 1)

---

### 🔐 PASSO 2: Configurar Secret no GitHub (3 min)

1. Acesse: https://github.com/LMONCAO/monpec/settings/secrets/actions
2. Clique em **"New repository secret"**
3. Name: `GCP_SA_KEY`
4. Secret: Cole TODO o conteúdo do JSON baixado
5. Clique em **"Add secret"**

📋 **Guia detalhado**: `DEPLOY_AGORA_PASSO_A_PASSO.md` (Passo 2)

---

### 📤 PASSO 3: Fazer Push do Código (2 min)

Abra PowerShell na pasta do projeto e execute:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentário\Monpec_GestaoRural"

git add .github/workflows/deploy-gcp.yml
git add *.md
git commit -m "Configurar deploy automático GitHub Actions"
git push origin main
```

(Se sua branch for `master`, use: `git push origin master`)

---

## ✅ Depois disso:

1. ✅ O deploy será executado **automaticamente** no GitHub Actions
2. ✅ Você pode acompanhar em: https://github.com/LMONCAO/monpec/actions
3. ✅ O sistema será atualizado no Google Cloud Run

---

## 📚 Documentação Completa:

- 📖 **Guia passo a passo completo**: `DEPLOY_AGORA_PASSO_A_PASSO.md`
- 📖 **Configuração detalhada**: `CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md`
- ⚡ **Quick start**: `QUICK_START_DEPLOY.md`

---

## 🆘 Precisa de ajuda?

Consulte `DEPLOY_AGORA_PASSO_A_PASSO.md` para instruções detalhadas com screenshots e troubleshooting!

---

**⏱️ Tempo total estimado: 10 minutos**

**🎉 Depois disso, todo push para `main` fará deploy automático!**








