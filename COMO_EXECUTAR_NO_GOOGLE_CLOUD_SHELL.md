# 🌐 COMO EXECUTAR O SCRIPT NO GOOGLE CLOUD SHELL

## 📋 PASSO A PASSO COMPLETO

### **PASSO 1: ACESSAR O GOOGLE CLOUD SHELL**

1. **Acesse**: https://console.cloud.google.com/
2. **Faça login** com sua conta Google Cloud
3. **Selecione o projeto**: `monpec-sistema-rural`
4. **Abra o Cloud Shell**:
   - Clique no ícone do terminal (☁️) no canto superior direito
   - Ou use o atalho: `Ctrl + Shift + T` (Windows/Linux) ou `Cmd + Shift + T` (Mac)

---

### **PASSO 2: UPLOAD DOS ARQUIVOS**

Você tem **2 opções**:

#### **OPÇÃO A: Upload Manual (Recomendado para primeira vez)**

1. No Cloud Shell, clique no ícone de **menu** (☰) no canto superior direito
2. Clique em **"Upload file"** ou **"Fazer upload do arquivo"**
3. Selecione e faça upload de:
   - `RESETAR_E_DEPLOY_DO_ZERO.sh`
   - Todos os arquivos do projeto (pode fazer upload de uma pasta ZIP)

**OU**

#### **OPÇÃO B: Usar Git (Se seu projeto estiver no GitHub/GitLab)**

```bash
# Clonar seu repositório
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git

# Entrar na pasta
cd SEU-REPOSITORIO
```

**OU**

#### **OPÇÃO C: Copiar arquivos manualmente via Cloud Shell Editor**

1. No Cloud Shell, clique no ícone de **"Open Editor"** (✏️)
2. Crie uma nova pasta ou navegue até onde quer os arquivos
3. Cole o conteúdo dos arquivos manualmente
4. Salve os arquivos

---

### **PASSO 3: NAVEGAR ATÉ A PASTA DO PROJETO**

```bash
# Ver onde você está
pwd

# Navegar até a pasta do projeto
# (Ajuste o caminho conforme necessário)
cd ~/Monpec_GestaoRural

# OU se você fez upload para outra pasta:
cd ~/Downloads
cd Monpec_GestaoRural
```

**Dica**: Use `ls` para listar arquivos e `cd` para navegar.

---

### **PASSO 4: DAR PERMISSÃO DE EXECUÇÃO**

```bash
# Dar permissão de execução ao script
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

### **PASSO 5: EXECUTAR O SCRIPT**

```bash
# Executar o script
bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

**OU**

```bash
# Executar diretamente
./RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 🎯 CAMINHO COMPLETO (RESUMO)

### **Sequência de Comandos:**

```bash
# 1. Abrir Cloud Shell (via console web)

# 2. Navegar até a pasta (ajuste conforme necessário)
cd ~/Monpec_GestaoRural

# 3. Verificar se o script está lá
ls -la RESETAR_E_DEPLOY_DO_ZERO.sh

# 4. Dar permissão de execução
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh

# 5. Executar
bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 📂 ESTRUTURA DE DIRETÓRIOS NO CLOUD SHELL

```
~ (home directory)
├── Monpec_GestaoRural/          # Seu projeto (após upload/clone)
│   ├── RESETAR_E_DEPLOY_DO_ZERO.sh
│   ├── manage.py
│   ├── Dockerfile.prod
│   ├── requirements_producao.txt
│   ├── sistema_rural/
│   └── ...
```

---

## ⚠️ IMPORTANTE

### **Certifique-se de que está no diretório correto:**

O script **DEVE** ser executado no diretório raiz do projeto Django que contém:
- ✅ `manage.py`
- ✅ `Dockerfile.prod` ou `Dockerfile`
- ✅ `requirements_producao.txt` ou `requirements.txt`
- ✅ `sistema_rural/` (pasta do Django)

### **Verificar antes de executar:**

```bash
# Verificar se está no diretório correto
pwd

# Listar arquivos
ls -la

# Verificar se manage.py existe
ls -la manage.py

# Verificar se Dockerfile.prod existe
ls -la Dockerfile.prod
```

Se todos esses arquivos estiverem lá, você está no lugar certo! ✅

---

## 🚀 EXEMPLO COMPLETO DE EXECUÇÃO

```bash
# 1. Abrir Cloud Shell (no navegador)

# 2. Verificar projeto
gcloud config get-value project
# Deve mostrar: monpec-sistema-rural

# 3. Se não estiver no projeto correto, configurar:
gcloud config set project monpec-sistema-rural

# 4. Navegar até a pasta do projeto
cd ~/Monpec_GestaoRural

# 5. Verificar arquivos
ls -la | grep -E "(manage.py|Dockerfile|requirements)"

# 6. Dar permissão
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh

# 7. Executar
bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 💡 DICAS

### **Se você não souber onde está:**

```bash
# Ver diretório atual
pwd

# Listar tudo
ls -la

# Buscar o script
find ~ -name "RESETAR_E_DEPLOY_DO_ZERO.sh" 2>/dev/null
```

### **Se você não souber qual pasta usar:**

1. Faça upload de um ZIP com todos os arquivos
2. Descompacte no Cloud Shell:
   ```bash
   unzip seu_arquivo.zip
   cd pasta_descompactada
   ```

---

## ✅ VERIFICAÇÃO FINAL

Antes de executar, confirme:

- [ ] Está no Google Cloud Shell (terminal no navegador)
- [ ] Projeto correto: `monpec-sistema-rural`
- [ ] Está no diretório raiz do projeto Django
- [ ] Arquivo `manage.py` existe
- [ ] Arquivo `Dockerfile.prod` existe
- [ ] Script `RESETAR_E_DEPLOY_DO_ZERO.sh` existe
- [ ] Permissão de execução foi dada (`chmod +x`)

Se tudo estiver ✅, pode executar o script!

---

## 🎯 COMANDO FINAL

```bash
bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

**Pronto!** 🚀

