# Guia para Atualizar o Repositório no GitHub

## ✅ O que foi feito:

1. **Remote atualizado**: O repositório local agora aponta para:
   - `https://github.com/LMONCAO/Monpec_GestaoRural.git`

## 📋 Próximos Passos no GitHub Desktop:

### Opção 1: Se o GitHub Desktop mostra "No local changes"

1. **Verifique se há alterações não commitadas:**
   - No GitHub Desktop, clique em **"View" → "Show in Explorer"**
   - Isso abrirá a pasta do projeto no Windows Explorer

2. **Faça refresh no GitHub Desktop:**
   - Pressione `Ctrl + R` ou feche e abra o GitHub Desktop novamente
   - O GitHub Desktop deve detectar as alterações

3. **Se ainda não aparecer alterações:**
   - Clique no menu **"Repository" → "Repository Settings"**
   - Verifique se o "Primary remote repository" está como: `https://github.com/LMONCAO/Monpec_GestaoRural.git`

### Opção 2: Fazer commit manualmente

1. **No GitHub Desktop:**
   - Clique na aba **"Changes"** (se houver alterações)
   - Adicione uma mensagem de commit (ex: "Atualização do projeto Monpec Gestão Rural")
   - Clique em **"Commit to main"** (ou "Commit to master")

2. **Publicar no GitHub:**
   - Se aparecer o botão **"Publish branch"**, clique nele
   - Ou vá em **"Branch" → "Push origin"**

### Opção 3: Se a branch for diferente (master vs main)

Se o GitHub Desktop mostra branch "main" mas o repositório local está em "master":

1. **No GitHub Desktop:**
   - Vá em **"Branch" → "New branch"**
   - Crie uma branch chamada "main" (se não existir)
   - Ou renomeie a branch atual: **"Branch" → "Rename"**

2. **Sincronizar:**
   - Faça commit das alterações
   - Clique em **"Publish branch"** ou **"Push origin"**

## 🔍 Verificar Status:

Para verificar se tudo está correto:

1. Abra o GitHub Desktop
2. Vá em **"Repository" → "Repository Settings"**
3. Verifique:
   - **Primary remote repository**: `https://github.com/LMONCAO/Monpec_GestaoRural.git`
   - **Current branch**: main ou master (conforme o repositório remoto)

## ⚠️ Nota Importante:

- O repositório local está configurado para `Monpec_GestaoRural`
- Se o repositório no GitHub estiver vazio, você precisará fazer o primeiro push
- Se já houver conteúdo no GitHub, pode ser necessário fazer pull primeiro para sincronizar

## 🚀 Comandos Git (se tiver Git instalado):

Se preferir usar a linha de comando (após instalar o Git):

```bash
git status
git add .
git commit -m "Atualização do projeto Monpec Gestão Rural"
git push -u origin master
```

Ou se a branch for "main":

```bash
git push -u origin main
```


