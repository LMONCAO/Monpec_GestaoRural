# ✅ SOLUÇÃO: Erro de Log no Windows

## 🚨 ERRO ENCONTRADO

```
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\var\\log\\monpec\\django.log'
ValueError: Unable to configure handler 'file'
```

## 🔍 CAUSA

O arquivo `settings_producao.py` foi configurado para Linux e usa caminhos que não existem no Windows:
- `/var/log/monpec/django.log` (caminho Linux)
- `/var/www/monpec.com.br/static` (caminho Linux)

## ✅ SOLUÇÃO

**Use `settings_windows.py` ao invés de `settings_producao.py`!**

### **Comando Correto:**

```powershell
cd C:\Monpec_projetista
.\python311\python.exe manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
```

### **Ou use o script:**

Clique duas vezes em: **`INICIAR_SERVIDOR_WINDOWS.bat`**

---

## 📋 DIFERENÇAS

| Arquivo | Uso | Caminhos |
|---------|-----|----------|
| `settings_producao.py` | Linux/Servidor | `/var/log/`, `/var/www/` |
| `settings_windows.py` | Windows/Desenvolvimento | `BASE_DIR/logs/`, `BASE_DIR/staticfiles/` |

---

## ⚠️ IMPORTANTE

**SEMPRE use `settings_windows` no Windows!**

- ✅ `--settings=sistema_rural.settings_windows` ← CORRETO
- ❌ `--settings=sistema_rural.settings_producao` ← ERRADO (causa o erro)

---

## 🚀 INICIAR SERVIDOR

### **Opção 1: Script Automático**
```
INICIAR_SERVIDOR_WINDOWS.bat
```

### **Opção 2: Manual**
```powershell
.\python311\python.exe manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
```

---

## 📱 ACESSO

- **PC:** `http://localhost:8000`
- **Celular:** `http://192.168.100.91:8000`

---

**Última atualização:** Dezembro 2025






