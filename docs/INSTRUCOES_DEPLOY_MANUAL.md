# 🚀 Instruções para Deploy Manual via GitHub

Como há problemas com o caminho do projeto, siga estes passos manualmente:

## 📋 Passo a Passo

### 1️⃣ Abrir PowerShell no Diretório do Projeto

1. Abra o **Explorador de Arquivos**
2. Navegue até: `C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural`
3. Clique com botão direito na pasta
4. Selecione **"Abrir no Terminal"** ou **"Abrir no PowerShell"**

### 2️⃣ Verificar se é Repositório Git

```powershell
git status
```

Se não for um repositório Git, inicialize:

```powershell
git init
git remote add origin https://github.com/LMONCAO/Monpec_GestaoRural.git
```

### 3️⃣ Verificar Arquivos Necessários

```powershell
# Verificar se os arquivos existem
Test-Path ".github\workflows\deploy-gcp.yml"
Test-Path "Dockerfile.prod"
```

Ambos devem retornar `True`.

### 4️⃣ Verificar Configuração

```powershell
# Verificar Service Account
.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1
```

### 5️⃣ Adicionar e Fazer Commit

```powershell
# Adicionar todos os arquivos
git add .

# Ou adicionar apenas arquivos específicos
git add .github/workflows/deploy-gcp.yml
git add Dockerfile.prod
git add *.md
git add .gitignore

# Fazer commit
git commit -m "Deploy automático via GitHub Actions"
```

### 6️⃣ Verificar Branch

```powershell
# Ver branch atual
git branch

# Se não houver branch, criar
git checkout -b main
# OU
git checkout -b master
```

### 7️⃣ Fazer Push

```powershell
# Push para GitHub (substitua 'main' pela sua branch)
git push -u origin main
# OU
git push -u origin master
```

### 8️⃣ Monitorar Deploy

Após o push, o deploy será iniciado automaticamente. Acompanhe em:

- **GitHub Actions**: https://github.com/LMONCAO/Monpec_GestaoRural/actions
- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/monpec

---

## ⚠️ Verificações Importantes

### Antes de fazer push, certifique-se de:

1. ✅ **Service Account configurada no GCP**
   - Execute: `.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1`

2. ✅ **Secret configurado no GitHub**
   - Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
   - Adicione o secret `GCP_SA_KEY` com o conteúdo do arquivo JSON

3. ✅ **Workflow existe**
   - Arquivo: `.github/workflows/deploy-gcp.yml`

4. ✅ **Dockerfile existe**
   - Arquivo: `Dockerfile.prod`

---

## 🆘 Se algo der errado

### Erro: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/LMONCAO/Monpec_GestaoRural.git
```

### Erro: "Permission denied"
- Verifique suas credenciais Git
- Configure: `git config --global user.name "Seu Nome"`
- Configure: `git config --global user.email "seu@email.com"`

### Erro: "Secret not found" no GitHub Actions
- Verifique se o secret `GCP_SA_KEY` está configurado
- Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions

---

## 📚 Scripts Disponíveis

Execute estes scripts no diretório do projeto:

- `.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1` - Verifica toda a configuração
- `.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1` - Configura Service Account
- `.\VERIFICAR_SECRET_GITHUB.ps1` - Verifica secret no GitHub
- `.\VERIFICAR_STATUS_GITHUB_ACTIONS.ps1` - Verifica status do deploy

---

## ✅ Checklist Final

- [ ] Repositório Git inicializado
- [ ] Remote configurado (origin)
- [ ] Service Account configurada no GCP
- [ ] Secret `GCP_SA_KEY` configurado no GitHub
- [ ] Arquivos commitados
- [ ] Push realizado para GitHub
- [ ] Deploy iniciado no GitHub Actions

---

**Boa sorte com o deploy! 🚀**








