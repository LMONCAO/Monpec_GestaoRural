# 🔧 CORRIGIR SSH NA LOCAWEB

## 🚨 **PROBLEMA IDENTIFICADO:**
- Erro: "Unable to find account by name monpec in domain"
- Conta SSH não configurada corretamente

---

## 🎯 **SOLUÇÕES:**

### **1. USAR CONTA CORRETA**
No painel da Locaweb, ao criar chave SSH:
- **Nome:** `monpecprojetista` ✅
- **Chave pública:** Deixe vazio (deixar Locaweb gerar)
- **Domínio:** `ROOT/LOCAWEB/CLOUD/LOCAWEB-monpec` ✅
- **Conta:** `LOCAWEB-monpec` (não "monpec")

### **2. GERAR CHAVE SSH LOCALMENTE**
```bash
# No seu computador Windows
ssh-keygen -t rsa -b 4096 -C "monpec@locaweb.com.br"
# Salvar em: C:\Users\seu_usuario\.ssh\monpec_key

# Copiar chave pública
type C:\Users\seu_usuario\.ssh\monpec_key.pub
```

### **3. USAR CHAVE PÚBLICA NO PAINEL**
1. **Copie a chave pública** gerada
2. **Cole no campo "Chave pública"** do painel
3. **Use conta:** `LOCAWEB-monpec`
4. **Clique em "OK"**

### **4. CONECTAR COM CHAVE**
```bash
# Usar a chave privada
ssh -i C:\Users\seu_usuario\.ssh\monpec_key centos@[IP_DA_VM]
```

---

## 🎯 **RECOMENDAÇÃO:**

**Use o Console Web** - é mais fácil e evita problemas de SSH!

1. **Acesse o painel** da Locaweb
2. **Vá em VMs** → Sua VM
3. **Clique em "Console"**
4. **Siga o guia** `SOLUCAO_CONSOLE_WEB.md`

**✅ Isso resolve todos os problemas de conectividade!**

