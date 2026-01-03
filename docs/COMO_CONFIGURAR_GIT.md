# 📚 Guia Completo: Configurar Git e Enviar Arquivos para Repositório Remoto

## 🎯 Objetivo
Configurar um repositório Git local e enviar todos os arquivos do projeto para um repositório remoto (GitHub, GitLab, etc.) para sincronizar com o Cloud Shell.

---

## 📋 Pré-requisitos

1. **Git instalado** - Verificar com: `git --version`
2. **Conta no GitHub/GitLab** (ou outro serviço Git)
3. **Acesso ao diretório do projeto**

---

## 🔧 Passo 1: Verificar e Configurar Git Local

### 1.1. Abrir terminal no diretório do projeto
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

### 1.2. Verificar se Git está inicializado
```powershell
git status
```

Se aparecer erro "not a git repository", inicializar:
```powershell
git init
```

### 1.3. Configurar usuário Git (se ainda não configurado)
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

---

## 📝 Passo 2: Melhorar o .gitignore

O arquivo `.gitignore` já existe, mas vamos garantir que está completo. Ele deve ignorar:
- Arquivos temporários
- Arquivos de ambiente (.env)
- Arquivos compilados (__pycache__, *.pyc)
- Arquivos do sistema operacional
- Backups e arquivos grandes

---

## 🗂️ Passo 3: Adicionar Arquivos ao Git

### 3.1. Verificar quais arquivos serão adicionados
```powershell
git status
```

### 3.2. Adicionar todos os arquivos do projeto
```powershell
git add .
```

### 3.3. Verificar o que foi adicionado
```powershell
git status
```

---

## 💾 Passo 4: Fazer o Primeiro Commit

```powershell
git commit -m "Commit inicial: projeto Monpec Gestão Rural"
```

---

## 🌐 Passo 5: Criar Repositório Remoto

### Opção A: GitHub (Recomendado)

1. Acesse: https://github.com
2. Clique em **"New repository"** (ou **"+"** → **"New repository"**)
3. Nome do repositório: `monpec-gestao-rural` (ou outro nome)
4. **NÃO** marque "Initialize with README" (já temos arquivos)
5. Clique em **"Create repository"**
6. Copie a URL do repositório (ex: `https://github.com/seu-usuario/monpec-gestao-rural.git`)

### Opção B: GitLab

1. Acesse: https://gitlab.com
2. Clique em **"New project"** → **"Create blank project"**
3. Preencha o nome e crie o projeto
4. Copie a URL do repositório

---

## 🔗 Passo 6: Conectar ao Repositório Remoto

### 6.1. Adicionar repositório remoto
```powershell
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
```

**Substitua** `SEU-USUARIO` e `SEU-REPOSITORIO` pela URL do seu repositório.

### 6.2. Verificar se foi adicionado
```powershell
git remote -v
```

Deve mostrar:
```
origin  https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git (fetch)
origin  https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git (push)
```

---

## 🚀 Passo 7: Enviar Arquivos para o Repositório Remoto

### 7.1. Renomear branch principal (se necessário)
```powershell
git branch -M main
```

### 7.2. Enviar arquivos
```powershell
git push -u origin main
```

**OU** se a branch for `master`:
```powershell
git push -u origin master
```

### 7.3. Autenticação
- Se pedir usuário/senha, use um **Personal Access Token** (não a senha normal)
- Para criar token no GitHub: Settings → Developer settings → Personal access tokens → Generate new token

---

## ✅ Passo 8: Verificar no Repositório Remoto

Acesse seu repositório no GitHub/GitLab e verifique se todos os arquivos aparecem.

---

## 🔄 Passo 9: Sincronizar com Cloud Shell

### 9.1. No Cloud Shell, clonar o repositório
```bash
cd ~
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
cd SEU-REPOSITORIO
```

### 9.2. Ou, se já tiver o projeto no Cloud Shell, adicionar o remote
```bash
cd ~/SEU-PROJETO
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git pull origin main
```

---

## 📤 Passo 10: Atualizar Repositório (Futuro)

Sempre que fizer alterações locais:

```powershell
# 1. Verificar mudanças
git status

# 2. Adicionar arquivos modificados
git add .

# 3. Fazer commit
git commit -m "Descrição das mudanças"

# 4. Enviar para o repositório remoto
git push
```

---

## 🔐 Autenticação no GitHub (Personal Access Token)

Se precisar criar um token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Marque as permissões: `repo` (acesso completo aos repositórios)
4. Generate token
5. **Copie o token** (ele só aparece uma vez!)
6. Use o token como senha quando o Git pedir

---

## ⚠️ Arquivos que NÃO devem ser enviados

O `.gitignore` já está configurado para ignorar:
- `.env` (variáveis de ambiente com senhas)
- `*.pyc` (arquivos compilados Python)
- `__pycache__/` (cache Python)
- `staticfiles/` (arquivos estáticos coletados)
- `db.sqlite3` (banco de dados local)
- Arquivos temporários e backups

---

## 🆘 Problemas Comuns

### Erro: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin SUA-URL-AQUI
```

### Erro: "failed to push some refs"
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Erro de autenticação
- Use Personal Access Token em vez de senha
- Ou configure SSH keys

---

## 📞 Próximos Passos

Após configurar o Git:
1. ✅ Fazer commit inicial
2. ✅ Enviar para repositório remoto
3. ✅ Clonar no Cloud Shell
4. ✅ Fazer deploy com código atualizado

---

**Dúvidas?** Verifique a documentação do Git: https://git-scm.com/doc



