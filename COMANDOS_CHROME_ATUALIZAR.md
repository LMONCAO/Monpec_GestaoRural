# 🌐 COMANDOS CHROME - ATUALIZAR IP E CACHE

## 🔄 ATUALIZAR/RECARREGAR PÁGINA

### **Recarregar Página Normal:**
```
F5
```
ou
```
Ctrl + R
```

### **Recarregar Forçado (Limpa Cache):**
```
Ctrl + F5
```
ou
```
Ctrl + Shift + R
```
ou
```
Shift + F5
```

**⚠️ IMPORTANTE:** Use `Ctrl + F5` para forçar o Chrome a buscar uma nova versão da página, ignorando o cache.

---

## 🗑️ LIMPAR CACHE E DADOS

### **Abrir DevTools (Ferramentas do Desenvolvedor):**
```
F12
```
ou
```
Ctrl + Shift + I
```

### **Limpar Cache com DevTools Aberto:**
1. Pressione `F12` (abre DevTools)
2. Clique com botão direito no **ícone de recarregar** (ao lado da barra de endereço)
3. Selecione **"Esvaziar cache e atualizar forçadamente"**

Ou use:
```
Ctrl + Shift + Delete
```
- Selecione **"Imagens e arquivos em cache"**
- Clique em **"Limpar dados"**

---

## 🔍 LIMPAR DNS DO CHROME

### **Limpar Cache DNS do Windows:**
No PowerShell (como Administrador):
```powershell
ipconfig /flushdns
```

### **Limpar Cache DNS do Chrome:**
1. Abra: `chrome://net-internals/#dns`
2. Clique em **"Clear host cache"**

---

## 🔧 ATUALIZAR IP ESPECÍFICO

### **Se o IP do servidor mudou:**

1. **Limpar cache do Chrome:**
   - `Ctrl + Shift + Delete`
   - Selecione "Imagens e arquivos em cache"
   - Período: "Todo o período"
   - Clique em "Limpar dados"

2. **Limpar DNS:**
   ```powershell
   ipconfig /flushdns
   ```

3. **Recarregar página forçado:**
   - `Ctrl + F5` na página

4. **Ou fechar e reabrir o Chrome completamente**

---

## 📱 NO CELULAR (Android/iPhone)

### **Chrome Android:**
- **Recarregar normal:** Puxe para baixo na página
- **Recarregar forçado:** Menu (3 pontos) → "Recarregar" (segure pressionado)

### **Chrome iPhone:**
- **Recarregar normal:** Puxe para baixo
- **Limpar cache:** Configurações → Privacidade → Limpar dados de navegação

---

## 🎯 COMANDOS ÚTEIS DO CHROME

### **Abrir Console (para debug):**
```
F12
```
ou
```
Ctrl + Shift + J
```

### **Abrir em Modo Anônimo:**
```
Ctrl + Shift + N
```

### **Fechar todas as abas:**
```
Ctrl + Shift + W
```

### **Nova aba:**
```
Ctrl + T
```

### **Fechar aba atual:**
```
Ctrl + W
```

---

## 🔄 ATUALIZAR IP DO SERVIDOR

### **Se o IP do servidor Django mudou:**

1. **Verificar novo IP:**
   ```powershell
   ipconfig | findstr IPv4
   ```

2. **No Chrome, acesse o novo IP:**
   ```
   http://NOVO_IP:8000
   ```

3. **Se ainda mostra página antiga:**
   - `Ctrl + F5` (recarregar forçado)
   - Ou `Ctrl + Shift + Delete` (limpar cache)

---

## 🚨 SOLUÇÃO RÁPIDA PARA ATUALIZAR IP

### **Passo a Passo:**

1. **Limpar DNS do Windows:**
   ```powershell
   ipconfig /flushdns
   ```

2. **No Chrome:**
   - Pressione `Ctrl + Shift + Delete`
   - Marque "Imagens e arquivos em cache"
   - Clique em "Limpar dados"

3. **Acesse o novo IP:**
   ```
   http://192.168.100.91:8000
   ```

4. **Se não funcionar, recarregue forçado:**
   - `Ctrl + F5`

---

## 📋 RESUMO DOS COMANDOS MAIS USADOS

| Ação | Comando |
|------|---------|
| Recarregar página | `F5` ou `Ctrl + R` |
| Recarregar forçado (limpa cache) | `Ctrl + F5` |
| Limpar cache | `Ctrl + Shift + Delete` |
| Limpar DNS Windows | `ipconfig /flushdns` |
| Abrir DevTools | `F12` |
| Modo anônimo | `Ctrl + Shift + N` |

---

**Última atualização:** Dezembro 2025






