# 📥 Clonar Repositório GitHub para Computador Local

Guia para clonar seu repositório do GitHub para o computador local.

---

## 📋 Pré-requisitos

- ✅ Git instalado no Windows
- ✅ URL do repositório GitHub
- ✅ Acesso ao repositório (público ou credenciais para privado)

---

## 🚀 Passo a Passo

### **Passo 1: Verificar se Git está Instalado**

No PowerShell:

```powershell
git --version
```

Se não estiver instalado, baixe em: https://git-scm.com/download/win

---

### **Passo 2: Navegar até a Pasta Desejada**

```powershell
# Exemplo: ir para Desktop
cd C:\Users\lmonc\Desktop

# Ou criar uma pasta específica
mkdir C:\Projetos
cd C:\Projetos
```

---

### **Passo 3: Clonar o Repositório**

```powershell
# Repositório público
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Exemplo:
# git clone https://github.com/lmoncaosilva/Monpec_GestaoRural.git
```

**Se o repositório for privado:**

```powershell
# Opção 1: Usar token de acesso pessoal
git clone https://SEU_TOKEN@github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Opção 2: Usar SSH (se configurado)
git clone git@github.com:SEU_USUARIO/SEU_REPOSITORIO.git
```

---

### **Passo 4: Entrar na Pasta Clonada**

```powershell
cd SEU_REPOSITORIO
# Exemplo: cd Monpec_GestaoRural
```

---

### **Passo 5: Verificar Arquivos**

```powershell
# Listar arquivos
ls

# Verificar se os arquivos importantes estão lá
Test-Path manage.py
Test-Path Dockerfile
Test-Path requirements_producao.txt
```

---

## 🔄 Sincronizar Depois (Atualizar do GitHub)

Quando quiser atualizar o código local com as mudanças do GitHub:

```powershell
# Entrar na pasta do projeto
cd C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural

# Verificar status
git status

# Buscar mudanças do GitHub
git fetch origin

# Ver diferenças
git diff origin/main

# Atualizar código local
git pull origin main
# ou: git pull origin master
```

---

## 🔐 Autenticação (Se Repositório Privado)

### **Opção 1: Token de Acesso Pessoal**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Copiar o token
4. Usar no clone: `git clone https://TOKEN@github.com/USUARIO/REPO.git`

### **Opção 2: Credenciais do Windows**

```powershell
# Configurar credenciais (salva no Windows Credential Manager)
git config --global credential.helper wincred

# Na primeira vez que clonar, vai pedir usuário e senha/token
```

---

## 📝 Comandos Úteis

```powershell
# Verificar status
git status

# Ver histórico de commits
git log --oneline

# Ver branches
git branch -a

# Mudar de branch
git checkout nome-da-branch

# Ver diferenças entre local e remoto
git diff origin/main
```

---

## ⚠️ Se Já Tem uma Pasta Local

Se você já tem a pasta local e quer sincronizar:

```powershell
# Entrar na pasta existente
cd C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural

# Verificar se já é um repositório Git
git status

# Se não for, inicializar
git init
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git fetch origin
git checkout -b main origin/main
# ou: git checkout -b master origin/master
```

---

## ✅ Checklist

- [ ] Git instalado
- [ ] URL do repositório GitHub
- [ ] Navegar até pasta desejada
- [ ] Executar `git clone`
- [ ] Verificar arquivos clonados
- [ ] Código sincronizado

---

## 🎯 Próximos Passos

Depois de clonar:

1. **Verificar se os arquivos corrigidos estão lá:**
   ```powershell
   Select-String -Path requirements_producao.txt -Pattern "django-logging"
   ```

2. **Se não estiverem, fazer commit e push das correções:**
   ```powershell
   git add requirements_producao.txt Dockerfile
   git commit -m "Corrigir: remover django-logging"
   git push origin main
   ```

3. **Depois clonar no Cloud Shell e fazer deploy**

---

**Última atualização:** Dezembro 2025

