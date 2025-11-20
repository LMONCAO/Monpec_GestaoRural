# 🔧 Corrigir Caminho no Cloud Shell

## ✅ **SOLUÇÃO RÁPIDA:**

### **No Terminal do Cloud Shell, execute:**

```bash
# Ver onde você está
pwd

# Ver seu nome de usuário
whoami

# Criar pasta no caminho correto
mkdir -p ~/Monpec_projetista

# Verificar se foi criada
ls -la ~/Monpec_projetista

# Ver o caminho completo
echo ~/Monpec_projetista
```

### **Depois, no diálogo "Open Folder":**

1. **Copie o caminho completo** que apareceu no comando `echo ~/Monpec_projetista`
2. **Cole no campo** do diálogo "Open Folder"
3. **Clique em "OK"**

---

## 🎯 **OU: Use o Caminho Absoluto Direto**

No diálogo "Open Folder", digite exatamente:

```
/home/joaoz/Monpec_projetista
```

(Substitua `joaoz` pelo seu nome de usuário real - veja no prompt do terminal)

---

## 🔍 **Verificar Nome de Usuário:**

No terminal, execute:

```bash
echo $USER
# ou
whoami
```

Use esse nome no caminho!

---

## 📋 **Passo a Passo Completo:**

1. **No terminal:**
```bash
mkdir -p ~/Monpec_projetista
cd ~/Monpec_projetista
pwd
```

2. **Copie o caminho** que apareceu (algo como `/home/joaoz/Monpec_projetista`)

3. **No diálogo "Open Folder":**
   - Cole o caminho completo
   - Clique "OK"

4. **Agora você verá a pasta no Explorer!**

5. **Faça upload dos arquivos:**
   - Clique com botão direito na pasta `Monpec_projetista`
   - Selecione "Upload Files" ou "Upload Folder"
   - Selecione `C:\Monpec_projetista` do seu PC

---

**💡 Dica: Se ainda não funcionar, use o método de arrastar e soltar!**






