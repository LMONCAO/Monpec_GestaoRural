# 🚀 INICIAR SERVIDOR AGORA

## 🔄 SERVIDOR PERMANENTE (RECOMENDADO)

Se você quer que o servidor **rode continuamente** e **inicie automaticamente** com o Windows:

1. **Abra PowerShell como Administrador**
2. **Execute:** `.\INSTALAR_SERVIDOR_PERMANENTE.ps1`
3. **Pronto!** O servidor ficará sempre ativo.

📖 **Veja instruções completas em:** `SERVIDOR_PERMANENTE.md`

---

## ⚠️ O SERVIDOR PAROU - COMO REINICIAR

### **OPÇÃO 1: Usar o Script Automático (RECOMENDADO)**

1. **Abra o arquivo:** `INICIAR_SERVIDOR_WINDOWS.bat`
2. **Clique duas vezes** no arquivo
3. **Aguarde** o servidor iniciar
4. **Anote o IP** que aparece na tela

---

### **OPÇÃO 2: Iniciar Manualmente pelo Terminal**

1. **Abra o PowerShell** ou **Prompt de Comando**
2. **Navegue até a pasta do projeto:**
   ```powershell
   cd C:\Monpec_projetista
   ```

3. **Inicie o servidor:**
   ```powershell
   .\python311\python.exe manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
   ```

   **OU se o Python estiver no PATH:**
   ```powershell
   python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
   ```
   
   **⚠️ IMPORTANTE:** Use `settings_windows` (não `settings_producao`) para evitar erros de caminho no Windows!

---

## 📱 ACESSO PELO CELULAR

### **IP da sua máquina:** `192.168.100.91`

No navegador do celular, digite:
```
http://192.168.100.91:8000
```

---

## ✅ VERIFICAR SE ESTÁ FUNCIONANDO

### **No terminal, você deve ver:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### **Para verificar se está rodando:**
```powershell
netstat -ano | findstr :8000
```

**Deve mostrar:** `TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING`

---

## 🚨 SE DER ERRO

### **Erro: "ModuleNotFoundError: No module named 'django'"**

Instale as dependências:
```powershell
.\python311\python.exe -m pip install -r requirements.txt
```

### **Erro: "Port already in use"**

Pare o processo que está usando a porta:
```powershell
# Encontrar processo
netstat -ano | findstr :8000

# Parar processo (substitua PID pelo número encontrado)
taskkill /F /PID [PID]
```

### **Erro: "DisallowedHost"**

O arquivo `sistema_rural/settings_windows.py` já está configurado com:
- `ALLOWED_HOSTS = ['*']` (permite qualquer host em desenvolvimento)
- `DEBUG = True`
- `SECURE_SSL_REDIRECT = False`
- `CSRF_TRUSTED_ORIGINS` atualizado

### **Erro: "FileNotFoundError: No such file or directory: 'C:\\var\\log\\monpec\\django.log'"**

**Solução:** Use `settings_windows` ao invés de `settings_producao`:
```powershell
.\python311\python.exe manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
```

O `settings_windows.py` não usa caminhos do Linux e funciona perfeitamente no Windows.

---

## 🔥 FIREWALL DO WINDOWS

Se o celular não conseguir acessar, pode ser o firewall:

1. **Abra o Firewall do Windows**
2. **Permitir um aplicativo pelo Firewall**
3. **Adicione Python** ou **desabilite temporariamente** para teste

---

## 📋 RESUMO RÁPIDO

1. ✅ Execute: `INICIAR_SERVIDOR_WINDOWS.bat` (ou use `settings_windows`)
2. ✅ Aguarde: "Starting development server"
3. ✅ No celular: `http://192.168.100.91:8000`
4. ✅ Celular e PC na mesma rede Wi-Fi

**⚠️ LEMBRE-SE:** Sempre use `--settings=sistema_rural.settings_windows` no Windows!

---

**Última atualização:** Dezembro 2025

