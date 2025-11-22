# 🔐 Resolver Autenticação do GitHub

## ⚠️ PROBLEMA CRÍTICO

O erro que você está vendo:
```
Password authentication is not supported for Git operations.
fatal: Authentication failed
```

**Isso significa:** GitHub não aceita mais senha! Precisa usar **Personal Access Token (PAT)**.

---

## ✅ SOLUÇÃO: Criar Personal Access Token

### Passo 1: Criar Token no GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome: `Monpec_GestaoRural_Deploy`
4. Selecione as permissões:
   - ✅ `repo` (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN IMEDIATAMENTE** (você não verá ele novamente!)
   - Exemplo: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### Passo 2: Usar Token no Windows (PowerShell)

No seu computador Windows, execute:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Configurar Git (se ainda não fez)
git config --global user.email "l.moncaosilva@gmail.com"
git config --global user.name "LMONCAO"

# Verificar status
git status

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Adicionar meta tag Google Search Console"

# Fazer push (vai pedir senha - use o TOKEN!)
git push origin master
```

**Quando pedir:**
- **Username:** `LMONCAO`
- **Password:** Cole o **TOKEN** que você copiou (não a senha!)

---

### Passo 3: Salvar Credenciais (Opcional mas Recomendado)

Para não precisar digitar o token toda vez:

**Windows (PowerShell):**

```powershell
# Instalar Git Credential Manager (se não tiver)
# Baixe de: https://github.com/GitCredentialManager/git-credential-manager/releases

# Ou usar cache temporário
git config --global credential.helper wincred
```

**OU** usar SSH (mais seguro):

```powershell
# Gerar chave SSH
ssh-keygen -t ed25519 -C "l.moncaosilva@gmail.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar no GitHub: https://github.com/settings/keys
# Depois mudar URL do repositório:
git remote set-url origin git@github.com:LMONCAO/Monpec_GestaoRural.git
```

---

## 🚀 DEPLOY NO CLOUD SHELL (DEPOIS DO PUSH)

**IMPORTANTE:** Não faça commit/push no Cloud Shell! Só faça `git pull`.

No Cloud Shell, execute:

```bash
# 1. Configurar Git (só uma vez)
git config --global user.email "l.moncaosilva@gmail.com"
git config --global user.name "LMONCAO"

# 2. Ir para a pasta
cd ~/Monpec_GestaoRural

# 3. Atualizar código (NÃO fazer commit aqui!)
git pull origin master

# 4. Dar permissão ao script
chmod +x deploy_completo_cloud_shell.sh

# 5. Executar deploy
./deploy_completo_cloud_shell.sh
```

---

## 📋 RESUMO DO FLUXO CORRETO

### ✅ NO WINDOWS (PowerShell):
1. Criar Personal Access Token no GitHub
2. Fazer `git add`, `git commit`, `git push` (usando token como senha)
3. Código vai para o GitHub

### ✅ NO CLOUD SHELL:
1. Configurar Git (user.email e user.name)
2. Fazer `git pull` para baixar código atualizado
3. Executar `./deploy_completo_cloud_shell.sh`
4. Deploy acontece

---

## 🆘 PROBLEMAS COMUNS

### Erro: "Authentication failed"
- ✅ Use Personal Access Token, não senha
- ✅ Token deve ter permissão `repo`

### Erro: "Author identity unknown"
```bash
git config --global user.email "l.moncaosilva@gmail.com"
git config --global user.name "LMONCAO"
```

### Erro: "Permission denied" no script
```bash
chmod +x deploy_completo_cloud_shell.sh
```

---

## 🔗 LINKS ÚTEIS

- Criar Token: https://github.com/settings/tokens
- Configurar SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- Git Credential Manager: https://github.com/GitCredentialManager/git-credential-manager

