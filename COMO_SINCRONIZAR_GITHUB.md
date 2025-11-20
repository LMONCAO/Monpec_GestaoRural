# 📤 Como Colocar Arquivos no GitHub e Sincronizar

## 🎯 Objetivo
Enviar todos os arquivos do projeto para o GitHub e manter sincronizado.

## 📋 Passo a Passo no GitHub Desktop

### 1️⃣ Verificar se os arquivos estão sendo rastreados

**No GitHub Desktop:**
- Clique em **"View" → "Show in Explorer"** para abrir a pasta
- Verifique se os arquivos do projeto estão na pasta

### 2️⃣ Adicionar arquivos ao Git (se necessário)

Se o GitHub Desktop mostra "0 changed files", pode ser que os arquivos não estejam sendo rastreados:

**Opção A - Via GitHub Desktop:**
1. Clique em **"Repository" → "Repository Settings"**
2. Vá em **"Ignored Files"** e verifique se algum arquivo importante está sendo ignorado
3. Volte para a tela principal e pressione **Ctrl + R** para atualizar

**Opção B - Forçar detecção de alterações:**
1. Feche o GitHub Desktop completamente
2. Abra novamente
3. O GitHub Desktop deve detectar os arquivos

### 3️⃣ Fazer o Primeiro Commit (se o repositório está vazio)

Se o repositório no GitHub está vazio:

1. **No GitHub Desktop:**
   - Clique na aba **"Changes"** (ou pressione `Ctrl + 1`)
   - Você deve ver uma lista de arquivos não rastreados ou modificados
   - Se não aparecer nada, clique em **"View" → "Show in Explorer"** e verifique os arquivos

2. **Se aparecerem arquivos:**
   - Marque todos os arquivos que deseja adicionar (ou deixe todos marcados)
   - Na parte inferior, digite uma mensagem de commit, por exemplo:
     ```
     Commit inicial - Projeto Monpec Gestão Rural
     ```
   - Clique em **"Commit to master"** (ou "Commit to main")

3. **Publicar no GitHub:**
   - Após o commit, aparecerá um botão **"Publish branch"** no topo
   - Clique em **"Publish branch"**
   - Isso enviará todos os arquivos para o GitHub

### 4️⃣ Se já houver commits locais

Se você já fez commits localmente mas não enviou:

1. **No GitHub Desktop:**
   - Vá na aba **"History"** (ou pressione `Ctrl + 2`)
   - Verifique se há commits que não foram enviados (aparecerá um indicador)
   - Clique no botão **"Push origin"** no topo da janela

### 5️⃣ Sincronizar com o GitHub (Pull/Push)

**Para baixar alterações do GitHub:**
- Clique em **"Repository" → "Pull"** (ou `Ctrl + Shift + P`)

**Para enviar alterações para o GitHub:**
- Clique em **"Repository" → "Push"** (ou `Ctrl + P`)

## 🔄 Sincronização Automática

Após o primeiro push, para manter sincronizado:

1. **Sempre que fizer alterações:**
   - O GitHub Desktop detectará automaticamente
   - Aparecerão na aba "Changes"
   - Faça commit e push

2. **Antes de começar a trabalhar:**
   - Faça um **Pull** para pegar as últimas alterações do GitHub
   - Isso evita conflitos

## ⚠️ Solução de Problemas

### Problema: "0 changed files" mas há arquivos na pasta

**Solução 1: Verificar .gitignore**
- O arquivo `.gitignore` pode estar ignorando arquivos importantes
- Verifique o arquivo `.gitignore` na raiz do projeto

**Solução 2: Adicionar arquivos manualmente**
- Use o script `adicionar_arquivos_git.ps1` que será criado

**Solução 3: Reiniciar o GitHub Desktop**
- Feche completamente o GitHub Desktop
- Abra novamente
- Pressione `Ctrl + R` para atualizar

### Problema: Erro ao fazer push

**Possíveis causas:**
- Repositório remoto tem alterações que você não tem localmente
- **Solução:** Faça um Pull primeiro, depois Push

- Problemas de autenticação
- **Solução:** Verifique suas credenciais do GitHub no GitHub Desktop

## 📝 Comandos Úteis no GitHub Desktop

- **Atualizar visualização:** `Ctrl + R`
- **Ver alterações:** `Ctrl + 1`
- **Ver histórico:** `Ctrl + 2`
- **Fazer Pull:** `Ctrl + Shift + P`
- **Fazer Push:** `Ctrl + P`
- **Abrir no Explorer:** Menu "View" → "Show in Explorer"
- **Abrir no Cursor:** Menu "View" → "Open in Cursor"

## 🚀 Fluxo de Trabalho Recomendado

1. **Início do dia:**
   - Abra o GitHub Desktop
   - Faça **Pull** para pegar atualizações
   - Comece a trabalhar

2. **Durante o trabalho:**
   - Faça suas alterações nos arquivos
   - O GitHub Desktop detecta automaticamente

3. **Ao terminar uma tarefa:**
   - Abra o GitHub Desktop
   - Revise as alterações na aba "Changes"
   - Adicione uma mensagem de commit descritiva
   - Faça **Commit**
   - Faça **Push** para enviar ao GitHub

4. **Fim do dia:**
   - Certifique-se de que todos os commits foram enviados (Push)
   - Verifique se não há alterações pendentes

