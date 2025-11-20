# ⚡ Solução Rápida - Upload de Arquivos

## 🎯 **AÇÃO IMEDIATA:**

### **No Terminal do Cloud Shell, execute:**

```bash
# Criar a pasta
mkdir -p ~/Monpec_projetista
cd ~/Monpec_projetista
pwd
```

### **Agora no Explorer (painel esquerdo):**

1. **Clique no ícone de pasta** no topo do Explorer (ao lado de "EXPLORER")
2. **Navegue até:** `/home/USER/Monpec_projetista` (onde USER é seu nome de usuário)
3. **Clique em "OK"** para abrir a pasta
4. **Agora você verá a pasta vazia**
5. **Clique com botão direito na pasta `Monpec_projetista`**
6. **Selecione "Upload Files" ou "Upload Folder"**
7. **Selecione a pasta do seu PC:** `C:\Monpec_projetista`

---

## 🔄 **OU: Use o Terminal para Verificar**

```bash
# Ver onde você está
pwd

# Ver o que tem na pasta home
ls -la ~

# Criar pasta se não existir
mkdir -p ~/Monpec_projetista

# Verificar
ls -la ~/Monpec_projetista
```

---

## 📋 **Depois do Upload, Verifique:**

```bash
cd ~/Monpec_projetista
ls -la

# Você deve ver:
# - manage.py
# - Dockerfile
# - requirements_producao.txt
# - sistema_rural/
# - templates/
# etc.
```

---

## 🚀 **Próximo Passo (Após Upload):**

```bash
cd ~/Monpec_projetista
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

---

**💡 Dica: Se o upload não funcionar, use o método Git ou crie os arquivos principais manualmente!**






