# ✅ Como Verificar se o Upload Funcionou

## 🔍 **MÉTODO 1: Verificar no Terminal (Mais Rápido)**

### **No terminal do Cloud Shell, execute:**

```bash
# Verificar se está na pasta correta
pwd
# Deve mostrar: /home/1_moncaosilva/Monpec_projetista

# Listar todos os arquivos e pastas
ls -la
```

### **✅ O que você DEVE ver se o upload funcionou:**

```
total XX
drwxr-xr-x  X user group  XXXX Nov 18 17:XX .
drwxr-xr-x  X user group  XXXX Nov 18 17:XX ..
-rw-r--r--  X user group  XXXX Nov 18 17:XX manage.py
-rw-r--r--  X user group  XXXX Nov 18 17:XX Dockerfile
-rw-r--r--  X user group  XXXX Nov 18 17:XX requirements_producao.txt
-rw-r--r--  X user group  XXXX Nov 18 17:XX requirements.txt
drwxr-xr-x  X user group  XXXX Nov 18 17:XX sistema_rural
drwxr-xr-x  X user group  XXXX Nov 18 17:XX templates
drwxr-xr-x  X user group  XXXX Nov 18 17:XX gestao_rural
... (muitos outros arquivos e pastas)
```

### **❌ Se você ver apenas:**

```
total 8
drwxr-xr-x  X user group  XXXX Nov 18 17:XX .
drwxr-xr-x  X user group  XXXX Nov 18 17:XX ..
```

**Isso significa que a pasta está VAZIA - o upload não funcionou ainda!**

---

## 🔍 **MÉTODO 2: Verificar Arquivos Específicos**

### **Verificar se os arquivos principais existem:**

```bash
# Verificar manage.py
ls -la manage.py

# Verificar Dockerfile
ls -la Dockerfile

# Verificar requirements
ls -la requirements_producao.txt

# Verificar pasta sistema_rural
ls -la sistema_rural/

# Verificar pasta templates
ls -la templates/
```

### **✅ Se todos existirem, o upload funcionou!**

---

## 🔍 **MÉTODO 3: Contar Arquivos**

```bash
# Contar quantos arquivos e pastas existem
ls -1 | wc -l

# Se mostrar mais de 10, provavelmente funcionou!
# Se mostrar apenas 2 (ou menos), está vazio!
```

---

## 🔍 **MÉTODO 4: Verificar no Explorer (Interface Visual)**

1. **No painel esquerdo (Explorer) do Cloud Shell Editor**
2. **Você deve ver a pasta `Monpec_projetista` expandida**
3. **Dentro dela, você deve ver:**
   - 📄 `manage.py`
   - 📄 `Dockerfile`
   - 📄 `requirements_producao.txt`
   - 📁 `sistema_rural/`
   - 📁 `templates/`
   - 📁 `gestao_rural/`
   - E muitos outros arquivos/pastas

### **✅ Se você ver esses arquivos, o upload funcionou!**

---

## 🆘 **Se o Upload NÃO Funcionou:**

### **Opção 1: Tentar Novamente**

1. No Explorer, clique com botão direito na pasta `Monpec_projetista`
2. Selecione "Upload Files" ou "Upload Folder"
3. Selecione `C:\Monpec_projetista` do seu PC

### **Opção 2: Arrastar e Soltar**

1. Abra o File Explorer do Windows
2. Navegue até `C:\Monpec_projetista`
3. Arraste a pasta inteira para o Explorer do Cloud Shell
4. Solte na pasta `Monpec_projetista`

### **Opção 3: Usar Git (se tiver repositório)**

```bash
cd ~
git clone SEU_REPOSITORIO_URL
cd Monpec_projetista
```

---

## ✅ **CHECKLIST: Upload Funcionou Se:**

- [ ] `ls -la` mostra mais de 10 arquivos/pastas
- [ ] `manage.py` existe
- [ ] `Dockerfile` existe
- [ ] `requirements_producao.txt` existe
- [ ] Pasta `sistema_rural/` existe
- [ ] Pasta `templates/` existe
- [ ] No Explorer você vê os arquivos listados

---

## 🚀 **Depois de Confirmar que Funcionou:**

Execute o build:

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

---

**💡 Execute `ls -la` no terminal para verificar rapidamente!**







