# 🔄 SINCRONIZAR REPOSITÓRIO NO OUTRO COMPUTADOR

## ⚠️ PROBLEMA
Quando você atualiza o repositório em um computador e abre em outro, pode aparecer uma versão antiga porque o outro computador não fez **pull** das mudanças mais recentes do GitHub.

---

## ✅ SOLUÇÃO: Sincronizar o Repositório

### **Passo 1: Abrir o Terminal/PowerShell no outro computador**

Navegue até a pasta do projeto:
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

Ou se estiver em outro caminho, navegue até onde está o projeto.

---

### **Passo 2: Verificar o status atual**

```powershell
git status
```

Isso mostra se há mudanças locais não commitadas.

---

### **Passo 3: Buscar as mudanças mais recentes do GitHub**

```powershell
git fetch origin
```

Este comando busca informações sobre as mudanças no GitHub sem alterar seus arquivos locais.

---

### **Passo 4: Atualizar os arquivos locais**

```powershell
git pull origin master
```

Este comando:
- ✅ Baixa todas as mudanças mais recentes do GitHub
- ✅ Atualiza os arquivos locais com a versão mais recente
- ✅ Sincroniza o repositório local com o remoto

---

### **Passo 5: Verificar se atualizou corretamente**

```powershell
git log --oneline -5
```

Você deve ver o commit mais recente:
```
dbd55b7 Atualização: adicionar e modificar arquivos do projeto
```

---

## 🔍 VERIFICAÇÃO COMPLETA

Execute estes comandos para garantir que está tudo sincronizado:

```powershell
# Verificar status
git status

# Verificar último commit
git log --oneline -1

# Verificar se está sincronizado com o remoto
git status
```

**Resultado esperado:**
```
On branch master
Your branch is up to date with 'origin/master'.
nothing to commit, working tree clean
```

---

## ⚠️ SE HOUVER CONFLITOS

Se você tiver mudanças locais não commitadas que conflitam com as mudanças do GitHub:

### **Opção 1: Salvar suas mudanças locais primeiro**

```powershell
# Ver quais arquivos foram modificados
git status

# Adicionar suas mudanças
git add .

# Fazer commit das suas mudanças
git commit -m "Minhas alterações locais"

# Agora fazer pull
git pull origin master
```

### **Opção 2: Descartar mudanças locais e usar apenas a versão do GitHub**

⚠️ **ATENÇÃO:** Isso vai apagar suas mudanças locais não commitadas!

```powershell
# Descartar todas as mudanças locais
git reset --hard origin/master

# Ou descartar mudanças de arquivos específicos
git checkout -- nome_do_arquivo.py
```

---

## 🚀 COMANDO RÁPIDO (TUDO EM UM)

Se você quer apenas atualizar tudo de uma vez:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentário\Monpec_GestaoRural"
git pull origin master
```

---

## 📋 CHECKLIST DE SINCRONIZAÇÃO

- [ ] Abrir terminal no outro computador
- [ ] Navegar até a pasta do projeto
- [ ] Executar `git status` para verificar estado
- [ ] Executar `git fetch origin` para buscar mudanças
- [ ] Executar `git pull origin master` para atualizar
- [ ] Verificar com `git log --oneline -5` se o último commit está presente
- [ ] Confirmar que `git status` mostra "up to date"

---

## 🔄 SINCRONIZAÇÃO AUTOMÁTICA (OPCIONAL)

Se você quer que o repositório sempre busque atualizações automaticamente, pode criar um script:

**`atualizar_repositorio.ps1`**
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentário\Monpec_GestaoRural"
Write-Host "Buscando atualizações do GitHub..." -ForegroundColor Yellow
git fetch origin
git pull origin master
Write-Host "Repositório atualizado!" -ForegroundColor Green
git log --oneline -3
```

Execute sempre que quiser atualizar:
```powershell
.\atualizar_repositorio.ps1
```

---

## ❓ TROUBLESHOOTING

### **Erro: "Your local changes would be overwritten"**

Você tem mudanças locais que conflitam. Escolha uma opção:
1. Fazer commit das suas mudanças primeiro
2. Ou descartar as mudanças locais (se não forem importantes)

### **Erro: "fatal: not a git repository"**

Você não está na pasta correta do projeto. Navegue até a pasta que contém o arquivo `.git`.

### **Erro: "Permission denied"**

Verifique se você tem permissão para escrever na pasta do projeto.

---

**Última atualização:** Dezembro 2025

