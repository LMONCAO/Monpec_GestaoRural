# 📤 Como Fazer Upload dos Arquivos no Cloud Shell

## 🎯 **MÉTODO 1: Via Interface do Cloud Shell Editor (Recomendado)**

### **Passo a Passo:**

1. **No Cloud Shell Editor, no painel esquerdo (Explorer):**
   - Você verá "NO FOLDER OPENED"
   - Clique no ícone de **três pontos (⋮)** ou **botão direito** na área do Explorer
   - Ou clique no ícone de **pasta com +** (Upload)

2. **Se não aparecer a opção de upload:**
   - Clique no ícone de **pasta** no topo do Explorer (ao lado de "EXPLORER")
   - Isso abrirá o diálogo "Open Folder"
   - **NÃO** digite nada ainda - primeiro vamos fazer upload

3. **Para fazer upload:**
   - **Opção A:** Arraste e solte os arquivos diretamente na área do Explorer
   - **Opção B:** Use o terminal para criar a pasta e depois faça upload

---

## 🎯 **MÉTODO 2: Via Terminal (Mais Fácil)**

### **Passo a Passo:**

1. **No terminal do Cloud Shell, crie a pasta:**
```bash
mkdir -p Monpec_projetista
cd Monpec_projetista
```

2. **Agora faça upload via interface:**
   - No Explorer, você verá a pasta `Monpec_projetista`
   - Clique com botão direito nela
   - Selecione **"Upload Files"** ou **"Upload Folder"**
   - Selecione a pasta `Monpec_projetista` do seu computador

---

## 🎯 **MÉTODO 3: Via Git (Se tiver repositório)**

Se você tem o código no GitHub/GitLab:

```bash
git clone SEU_REPOSITORIO_URL
cd Monpec_projetista
```

---

## 🎯 **MÉTODO 4: Via gcloud (Do seu PC Windows)**

Se você tem o gcloud instalado no Windows:

```bash
# No PowerShell do seu PC
gcloud compute scp --recurse C:\Monpec_projetista cloud-shell:~/Monpec_projetista
```

---

## ✅ **Verificar se o Upload Funcionou**

Depois do upload, no terminal execute:

```bash
cd Monpec_projetista
ls -la
```

Você deve ver arquivos como:
- `manage.py`
- `Dockerfile`
- `requirements_producao.txt`
- `sistema_rural/`
- etc.

---

## 🆘 **Se Não Conseguir Fazer Upload**

### **Alternativa: Criar Arquivos Diretamente**

Você pode criar os arquivos principais diretamente no Cloud Shell:

```bash
# Criar estrutura básica
mkdir -p Monpec_projetista
cd Monpec_projetista
```

Depois copie e cole o conteúdo dos arquivos principais um por um.

---

## 💡 **DICA: Use o Drag and Drop**

A forma mais fácil é:
1. Abra o File Explorer do Windows
2. Navegue até `C:\Monpec_projetista`
3. Arraste a pasta inteira para a área do Explorer do Cloud Shell
4. Solte!

---

**🚀 Depois do upload, continue com:**
```bash
cd Monpec_projetista
ls -la
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```







