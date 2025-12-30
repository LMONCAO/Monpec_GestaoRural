# ⚡ COMANDOS RÁPIDOS PARA GOOGLE CLOUD SHELL

## 🚀 COMANDOS PARA COPIAR E COLAR DIRETAMENTE

### **OPÇÃO 1: COMANDO ÚNICO (RECOMENDADO)**

Cole este comando diretamente no Cloud Shell:

```bash
gcloud config set project monpec-sistema-rural && mkdir -p ~/monpec_deploy && cd ~/monpec_deploy && echo "✅ Pasta criada. Agora faça upload dos arquivos via Cloud Shell Editor e depois execute: chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh"
```

---

### **OPÇÃO 2: PASSOS SEPARADOS**

#### **Passo 1 - Configurar projeto:**
```bash
gcloud config set project monpec-sistema-rural
```

#### **Passo 2 - Criar pasta e entrar:**
```bash
mkdir -p ~/monpec_deploy && cd ~/monpec_deploy
```

#### **Passo 3 - Fazer upload dos arquivos:**
1. Clique no ícone **"Open Editor"** (✏️) no Cloud Shell
2. Clique com botão direito na pasta `monpec_deploy`
3. Selecione **"Upload Files"**
4. Faça upload de **TODOS os arquivos** do projeto:
   - `RESETAR_E_DEPLOY_DO_ZERO.sh`
   - `manage.py`
   - `Dockerfile.prod`
   - `requirements_producao.txt`
   - Pasta `sistema_rural/`
   - Pasta `gestao_rural/`
   - Pasta `templates/`
   - Pasta `static/`
   - E todos os outros arquivos do projeto

**OU** compacte tudo em ZIP, faça upload do ZIP, depois:
```bash
unzip seu_arquivo.zip
```

#### **Passo 4 - Verificar se os arquivos estão lá:**
```bash
ls -la | grep -E "(manage.py|RESETAR_E_DEPLOY_DO_ZERO.sh|Dockerfile)"
```

#### **Passo 5 - Executar o script:**
```bash
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

### **OPÇÃO 3: SE JÁ TEM OS ARQUIVOS EM OUTRA PASTA**

```bash
# Encontrar onde está o script
find ~ -name "RESETAR_E_DEPLOY_DO_ZERO.sh" 2>/dev/null

# Navegar até a pasta que apareceu acima
cd ~/caminho/que/apareceu

# Executar
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 📋 COMANDO COMPLETO (TUDO DE UMA VEZ)

Se você já fez upload dos arquivos e está na pasta certa:

```bash
gcloud config set project monpec-sistema-rural && cd ~/monpec_deploy && chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## ⚠️ VERIFICAÇÃO ANTES DE EXECUTAR

Certifique-se de que estes arquivos existem na pasta:

```bash
ls -la manage.py RESETAR_E_DEPLOY_DO_ZERO.sh Dockerfile.prod requirements_producao.txt
```

Se todos aparecerem ✅, pode executar!

---

## 🎯 SEQUÊNCIA RÁPIDA (COPY/PASTE)

```bash
# 1. Configurar e criar pasta
gcloud config set project monpec-sistema-rural && mkdir -p ~/monpec_deploy && cd ~/monpec_deploy

# 2. (Faça upload dos arquivos via Editor primeiro)

# 3. Executar
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 💡 DICA: UPLOAD RÁPIDO VIA ZIP

1. **No seu computador**: Compacte todo o projeto em ZIP
2. **No Cloud Shell**: Clique em "Upload file" (ícone de nuvem com seta)
3. **Faça upload do ZIP**
4. **Descompacte**:
   ```bash
   unzip Monpec_GestaoRural.zip -d ~/monpec_deploy
   cd ~/monpec_deploy
   chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh
   bash RESETAR_E_DEPLOY_DO_ZERO.sh
   ```

---

## ✅ CHECKLIST ANTES DE EXECUTAR

- [ ] Cloud Shell aberto
- [ ] Projeto configurado: `monpec-sistema-rural`
- [ ] Arquivos enviados (via Editor ou ZIP)
- [ ] Pasta `~/monpec_deploy` criada
- [ ] Arquivo `RESETAR_E_DEPLOY_DO_ZERO.sh` existe
- [ ] Arquivo `manage.py` existe
- [ ] Arquivo `Dockerfile.prod` existe

**Se tudo estiver ✅, execute:**

```bash
bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

