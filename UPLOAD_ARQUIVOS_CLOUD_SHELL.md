# 📤 COMO FAZER UPLOAD DOS ARQUIVOS PARA O CLOUD SHELL

## ✅ VOCÊ JÁ CRIOU A PASTA! AGORA PRECISA FAZER UPLOAD DOS ARQUIVOS

Você está na pasta `~/monpec_deploy`, mas os arquivos ainda não foram enviados.

---

## 🚀 MÉTODO 1: VIA CLOUD SHELL EDITOR (RECOMENDADO)

### **Passo 1: Abrir o Editor**
1. No Cloud Shell, clique no ícone **"Abrir editor"** (✏️) no canto superior direito do terminal
2. Isso abrirá um editor de arquivos na parte superior

### **Passo 2: Upload dos Arquivos**
1. No editor, clique com o **botão direito** na pasta `monpec_deploy` (na barra lateral esquerda)
2. Selecione **"Upload Files..."** ou **"Fazer upload de arquivos..."**
3. Selecione **TODOS os arquivos** do seu projeto:
   - `RESETAR_E_DEPLOY_DO_ZERO.sh`
   - `manage.py`
   - `Dockerfile.prod`
   - `requirements_producao.txt`
   - Pasta `sistema_rural/` (inteira)
   - Pasta `gestao_rural/` (inteira)
   - Pasta `templates/` (inteira)
   - Pasta `static/` (inteira)
   - E todos os outros arquivos do projeto

### **Passo 3: Verificar se os arquivos foram enviados**
No terminal, digite:
```bash
ls -la
```

Você deve ver os arquivos listados.

### **Passo 4: Executar o script**
```bash
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 🚀 MÉTODO 2: VIA UPLOAD DE ARQUIVO ÚNICO (ÍCONE DE NUVEM)

1. No Cloud Shell, clique no ícone de **menu** (☰) no canto superior direito
2. Selecione **"Upload file"** ou **"Fazer upload do arquivo"**
3. Faça upload do arquivo `RESETAR_E_DEPLOY_DO_ZERO.sh`
4. Depois faça upload dos outros arquivos um por um (ou use o Método 1 que é mais fácil)

---

## 🚀 MÉTODO 3: COMPACTAR EM ZIP E FAZER UPLOAD (MAIS RÁPIDO)

### **No seu computador Windows:**

1. **Compacte tudo em ZIP:**
   - Clique com botão direito na pasta `Monpec_GestaoRural`
   - Selecione "Enviar para" → "Pasta compactada (em zip)"
   - Isso criará um arquivo `Monpec_GestaoRural.zip`

### **No Cloud Shell:**

1. **Fazer upload do ZIP:**
   - Clique no ícone de **menu** (☰) → **"Upload file"**
   - Selecione o arquivo ZIP

2. **Descompactar:**
   ```bash
   unzip Monpec_GestaoRural.zip -d ~/monpec_deploy
   cd ~/monpec_deploy/Monpec_GestaoRural
   ```

3. **Mover arquivos para a pasta correta:**
   ```bash
   mv * ../ 2>/dev/null || true
   mv .* ../ 2>/dev/null || true
   cd ..
   ```

4. **Executar:**
   ```bash
   chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
   ```

---

## ✅ COMANDOS RÁPIDOS DEPOIS DO UPLOAD

Depois que fizer upload dos arquivos, execute no terminal:

```bash
# Verificar se os arquivos estão lá
ls -la | grep -E "(RESETAR_E_DEPLOY_DO_ZERO.sh|manage.py|Dockerfile)"

# Se aparecerem, executar:
chmod +x RESETAR_E_DEPLOY_DO_ZERO.sh && bash RESETAR_E_DEPLOY_DO_ZERO.sh
```

---

## 📋 CHECKLIST

- [ ] Pasta `~/monpec_deploy` criada ✅ (você já fez isso!)
- [ ] Arquivo `RESETAR_E_DEPLOY_DO_ZERO.sh` enviado
- [ ] Arquivo `manage.py` enviado
- [ ] Arquivo `Dockerfile.prod` enviado
- [ ] Arquivo `requirements_producao.txt` enviado
- [ ] Pastas `sistema_rural/`, `gestao_rural/`, `templates/`, `static/` enviadas
- [ ] Todos os arquivos verificados com `ls -la`

**Quando tudo estiver ✅, execute o script!**

