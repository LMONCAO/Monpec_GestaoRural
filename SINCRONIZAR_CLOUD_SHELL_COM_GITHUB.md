# 🔄 Sincronizar Cloud Shell com GitHub

Guia para trabalhar com Git no Cloud Shell e sincronizar mudanças com o GitHub.

---

## 📋 Opções de Sincronização

### **Opção 1: Clonar do GitHub → Fazer Mudanças no Cloud Shell → Push de Volta**

Este é o fluxo mais comum e recomendado.

---

## 🚀 Passo a Passo Completo

### **Passo 1: Clonar Repositório no Cloud Shell**

```bash
# Clonar do GitHub
git clone https://github.com/SEU_USUARIO/Monpec_GestaoRural.git

# Entrar na pasta
cd Monpec_GestaoRural
```

---

### **Passo 2: Fazer Mudanças no Cloud Shell (se necessário)**

```bash
# Editar arquivos
nano requirements_producao.txt
# ou
vim Dockerfile

# Fazer as alterações necessárias
```

---

### **Passo 3: Configurar Git no Cloud Shell (se ainda não configurou)**

```bash
# Configurar nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

---

### **Passo 4: Fazer Commit das Mudanças**

```bash
# Ver o que foi alterado
git status

# Adicionar arquivos alterados
git add requirements_producao.txt Dockerfile

# Fazer commit
git commit -m "Corrigir: remover django-logging e otimizar Dockerfile"
```

---

### **Passo 5: Fazer Push para GitHub**

```bash
# Push para GitHub
git push origin main
# ou: git push origin master
```

**Se o repositório for privado e pedir autenticação:**

```bash
# Opção 1: Usar token
git push https://SEU_TOKEN@github.com/SEU_USUARIO/Monpec_GestaoRural.git main

# Opção 2: Configurar credenciais
git config --global credential.helper store
# Na primeira vez vai pedir usuário e token
```

---

## 🔄 Fluxo Completo: GitHub → Cloud Shell → Deploy → Push de Volta

### **1. Clonar do GitHub no Cloud Shell**

```bash
git clone https://github.com/SEU_USUARIO/Monpec_GestaoRural.git
cd Monpec_GestaoRural
```

### **2. Fazer Deploy**

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1
```

### **3. Se Fizer Mudanças no Cloud Shell**

```bash
# Fazer mudanças
nano arquivo.py

# Commit
git add arquivo.py
git commit -m "Descrição da mudança"

# Push para GitHub
git push origin main
```

### **4. Sincronizar no Computador Local**

No seu computador:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
git pull origin main
```

---

## 🔐 Autenticação no Cloud Shell

### **Método 1: Token de Acesso Pessoal (Recomendado)**

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Dar permissões: `repo` (acesso completo a repositórios)
4. Copiar o token

No Cloud Shell:

```bash
# Usar token no clone
git clone https://TOKEN@github.com/USUARIO/REPO.git

# Ou configurar globalmente
git config --global credential.helper store
# Quando pedir, usar: usuário = seu-usuario, senha = TOKEN
```

### **Método 2: SSH (Mais Seguro)**

```bash
# Gerar chave SSH no Cloud Shell
ssh-keygen -t ed25519 -C "seu-email@exemplo.com"

# Ver chave pública
cat ~/.ssh/id_ed25519.pub

# Copiar e adicionar no GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key

# Clonar usando SSH
git clone git@github.com:SEU_USUARIO/Monpec_GestaoRural.git
```

---

## 📝 Comandos Úteis no Cloud Shell

```bash
# Ver status
git status

# Ver diferenças
git diff

# Ver histórico
git log --oneline

# Atualizar do GitHub
git pull origin main

# Ver branches
git branch -a

# Criar nova branch
git checkout -b nova-branch

# Mudar de branch
git checkout main
```

---

## ⚠️ Importante

### **Sempre Fazer Pull Antes de Fazer Push**

Se outras pessoas (ou você em outro lugar) fizeram mudanças:

```bash
# Sempre atualizar primeiro
git pull origin main

# Resolver conflitos se houver
# Depois fazer push
git push origin main
```

---

## 🔄 Fluxo Recomendado

```
GitHub (origem)
    ↓ (git clone)
Cloud Shell (trabalho)
    ↓ (git push)
GitHub (atualizado)
    ↓ (git pull)
Computador Local (sincronizado)
```

---

## ✅ Checklist

- [ ] Git configurado no Cloud Shell
- [ ] Repositório clonado do GitHub
- [ ] Autenticação configurada (token ou SSH)
- [ ] Mudanças feitas e commitadas
- [ ] Push feito para GitHub
- [ ] Computador local sincronizado (git pull)

---

## 🎯 Exemplo Prático Completo

```bash
# 1. Clonar
git clone https://github.com/SEU_USUARIO/Monpec_GestaoRural.git
cd Monpec_GestaoRural

# 2. Configurar Git (primeira vez)
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"

# 3. Fazer deploy
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1

# 4. Se fizer mudanças
nano requirements_producao.txt
git add requirements_producao.txt
git commit -m "Atualizar dependências"
git push origin main

# 5. No computador local, sincronizar
git pull origin main
```

---

**Última atualização:** Dezembro 2025

