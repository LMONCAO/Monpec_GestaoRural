# 🚀 GUIA DE OTIMIZAÇÃO DE DESEMPENHO

## ⚡ OTIMIZAÇÃO COMPLETA (Execute uma vez)

### Passo 1: Otimização Completa do Sistema
1. **Clique com botão direito** em `OTIMIZAR_DESEMPENHO_NOTEBOOK.bat`
2. Selecione **"Executar como administrador"**
3. Aguarde a conclusão (pode levar alguns minutos)
4. **REINICIE o computador** para aplicar todas as mudanças

### O que o script faz:
- ✅ Para processos desnecessários (Teams, Skype, Spotify, etc.)
- ✅ Configura plano de energia para alta performance
- ✅ Desabilita serviços desnecessários do Windows
- ✅ Limpa cache e arquivos temporários
- ✅ Otimiza prioridades de processo
- ✅ Desabilita animações e efeitos visuais
- ✅ Verifica memória e disco

---

## 🔄 OTIMIZAÇÃO RÁPIDA (Quando o Cursor travar)

Execute `OTIMIZAR_CURSOR_RAPIDO.ps1` quando o Cursor estiver lento:

1. Clique com botão direito em `OTIMIZAR_CURSOR_RAPIDO.ps1`
2. Selecione **"Executar com PowerShell"**
3. Aguarde alguns segundos

Isso vai:
- ✅ Aumentar prioridade do Cursor
- ✅ Limpar cache do Cursor
- ✅ Otimizar processos Python
- ✅ Liberar memória

---

## 📋 CONFIGURAÇÕES MANUAIS RECOMENDADAS

### 1. Desabilitar Inicialização Automática de Apps

1. Pressione `Ctrl + Shift + Esc` (Gerenciador de Tarefas)
2. Vá na aba **"Inicialização"**
3. Desabilite aplicações que não precisa iniciar automaticamente:
   - Teams, Skype, Discord
   - Spotify, Steam
   - Adobe Creative Cloud
   - OneDrive (se não usar muito)

### 2. Configurar Memória Virtual (Pagefile)

1. Pressione `Win + R`, digite `sysdm.cpl` e Enter
2. Aba **"Avançado"** > **"Desempenho"** > **"Configurações"**
3. Aba **"Avançado"** > **"Alterar"** (Memória Virtual)
4. Desmarque **"Gerenciar automaticamente"**
5. Configure:
   - **Tamanho inicial:** 1.5x sua RAM (ex: se tem 8GB, use 12288 MB)
   - **Tamanho máximo:** 2x sua RAM (ex: 16GB = 16384 MB)
6. Clique **"Definir"** e **"OK"**
7. **Reinicie** o computador

### 3. Desabilitar Efeitos Visuais do Windows

1. Pressione `Win + R`, digite `sysdm.cpl` e Enter
2. Aba **"Avançado"** > **"Desempenho"** > **"Configurações"**
3. Selecione **"Ajustar para obter o melhor desempenho"**
4. Ou marque apenas:
   - ✅ Suavizar bordas de fontes de tela
   - ✅ Mostrar miniaturas em vez de ícones
5. Clique **"OK"**

### 4. Configurações do Cursor

#### Desabilitar Extensões Desnecessárias
1. No Cursor: `Ctrl + Shift + X` (Extensões)
2. Desabilite extensões que não usa
3. Mantenha apenas as essenciais

#### Reduzir Arquivos Abertos
- Feche arquivos que não está editando
- Use `Ctrl + K, W` para fechar todos os arquivos
- Use `Ctrl + P` para abrir arquivos rapidamente quando precisar

#### Configurar Limites de Memória
1. No Cursor: `Ctrl + Shift + P`
2. Digite: `Preferences: Open Settings (JSON)`
3. Adicione:
```json
{
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/venv/**": true,
    "**/python311/**": true,
    "**/__pycache__/**": true,
    "**/backups/**": true,
    "**/*.sqlite3": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/python311": true,
    "**/__pycache__": true,
    "**/backups": true,
    "**/*.sqlite3": true
  }
}
```

---

## 🔍 VERIFICAR PROBLEMAS

### Se o Cursor continuar travando:

1. **Verifique uso de memória:**
   - `Ctrl + Shift + Esc` > Aba "Desempenho"
   - Se RAM estiver acima de 80%, feche outros programas

2. **Verifique processos pesados:**
   - No Gerenciador de Tarefas, ordene por "Memória"
   - Feche processos que estão usando muita memória

3. **Verifique espaço em disco:**
   - Disco C: deve ter pelo menos 10GB livres
   - Use o Limpeza de Disco do Windows

4. **Reinicie o Cursor:**
   - `Ctrl + Shift + P` > "Developer: Reload Window"
   - Ou feche e abra novamente

---

## 💡 DICAS ADICIONAIS

### Para Desenvolvimento Django:
- ✅ Mantenha apenas o servidor Django rodando
- ✅ Feche outros servidores/processos Python desnecessários
- ✅ Use `.cursorignore` (já criado) para ignorar arquivos grandes
- ✅ Não abra pastas muito grandes no Cursor

### Hardware:
- **RAM mínima recomendada:** 8GB (16GB ideal)
- **SSD é essencial** para boa performance
- Se possível, adicione mais RAM

### Software:
- Mantenha Windows atualizado
- Use antivírus leve (Windows Defender é suficiente)
- Evite múltiplos navegadores abertos

---

## 📞 SE NADA FUNCIONAR

1. **Reinicie o computador** (resolve 80% dos problemas)
2. **Atualize o Cursor** para a versão mais recente
3. **Verifique se há atualizações do Windows**
4. **Considere reinstalar o Cursor** (último recurso)

---

**Última atualização:** 22/12/2025










