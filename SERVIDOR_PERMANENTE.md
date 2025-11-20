# 🔄 SERVIDOR PERMANENTE MONPEC

## 📋 O QUE É?

Este sistema permite que o servidor Django rode **continuamente** no Windows, mesmo após fechar o terminal ou reiniciar o computador. O servidor só para quando a máquina for desligada.

---

## ✨ RECURSOS

- ✅ **Inicia automaticamente** quando o Windows inicia
- ✅ **Reinicia automaticamente** se o servidor cair
- ✅ **Mantém rodando** mesmo fechando o terminal
- ✅ **Monitora continuamente** o status do servidor
- ✅ **Logs detalhados** de tudo que acontece
- ✅ **Fácil de instalar/remover**

---

## 🚀 COMO INSTALAR

### **Passo 1: Abrir PowerShell como Administrador**

1. Clique com **botão direito** no menu Iniciar do Windows
2. Selecione **"Windows PowerShell (Admin)"** ou **"Terminal (Admin)"**
3. Aceite a solicitação de permissão de administrador

### **Passo 2: Navegar até a pasta do projeto**

```powershell
cd C:\Monpec_projetista
```

### **Passo 3: Instalar o servidor permanente**

```powershell
.\INSTALAR_SERVIDOR_PERMANENTE.ps1
```

O script vai:
- ✅ Criar uma tarefa agendada do Windows
- ✅ Configurar para iniciar automaticamente
- ✅ Iniciar o servidor imediatamente
- ✅ Configurar reinicialização automática se cair

### **Resultado esperado:**

```
========================================
  SERVIDOR INSTALADO E RODANDO!
========================================

O servidor agora:
  ✓ Inicia automaticamente com o Windows
  ✓ Reinicia automaticamente se cair
  ✓ Mantém rodando mesmo fechando o terminal

Porta 8000 está ativa!
```

---

## 🔍 COMO VERIFICAR SE ESTÁ RODANDO

### **Opção 1: Usar o script de verificação**

```powershell
.\VERIFICAR_SERVIDOR.ps1
```

Este script mostra:
- ✅ Status da porta 8000
- ✅ Status da tarefa agendada
- ✅ Processos Python rodando
- ✅ Últimas linhas dos logs

### **Opção 2: Verificar manualmente**

```powershell
# Verificar porta 8000
netstat -ano | findstr :8000

# Verificar tarefa agendada
Get-ScheduledTask -TaskName "MONPEC_Servidor_Django"

# Verificar status da tarefa
Get-ScheduledTaskInfo -TaskName "MONPEC_Servidor_Django"
```

### **Opção 3: Testar no navegador**

Abra o navegador e acesse:
```
http://localhost:8000
```

Se a página carregar, o servidor está funcionando! ✅

---

## 📊 LOGS E ERROS

Os logs são salvos automaticamente na pasta do projeto:

- **`django_server.log`** - Log geral do servidor
- **`django_error.log`** - Log de erros (se houver)

### **Ver últimos logs:**

```powershell
# Ver últimas 20 linhas do log
Get-Content django_server.log -Tail 20

# Ver últimas 10 linhas de erros
Get-Content django_error.log -Tail 10

# Monitorar log em tempo real
Get-Content django_server.log -Wait -Tail 10
```

---

## 🛑 COMO REMOVER O SERVIDOR PERMANENTE

Se quiser que o servidor não inicie mais automaticamente:

### **Passo 1: Abrir PowerShell como Administrador**

### **Passo 2: Executar script de remoção**

```powershell
cd C:\Monpec_projetista
.\REMOVER_SERVIDOR_PERMANENTE.ps1
```

Este script vai:
- ✅ Parar a tarefa agendada
- ✅ Parar o servidor atual
- ✅ Remover a configuração automática

**Depois disso, você precisará iniciar o servidor manualmente usando `INICIAR_SERVIDOR_WINDOWS.bat`**

---

## 🔄 REINICIAR O SERVIDOR MANUALMENTE

Mesmo com o servidor permanente instalado, você pode reiniciar manualmente:

### **Opção 1: Reiniciar a tarefa agendada**

```powershell
# Parar
Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django"

# Aguardar alguns segundos
Start-Sleep -Seconds 5

# Iniciar novamente
Start-ScheduledTask -TaskName "MONPEC_Servidor_Django"
```

### **Opção 2: Parar processo e deixar reiniciar automaticamente**

```powershell
# Encontrar PID do processo
netstat -ano | findstr :8000

# Parar o processo (substitua [PID] pelo número encontrado)
taskkill /F /PID [PID]
```

O sistema reiniciará automaticamente em até 1 minuto.

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS

### **Alterar porta do servidor**

Se quiser mudar da porta 8000 para outra:

1. Edite o arquivo `SERVIDOR_PERMANENTE.ps1`
2. Procure por `:8000` e substitua pela porta desejada
3. Reinstale o servidor permanente

### **Alterar intervalo de verificação**

O servidor verifica o status a cada 30 segundos. Para alterar:

1. Edite `SERVIDOR_PERMANENTE.ps1`
2. Procure por `Start-Sleep -Seconds 30`
3. Altere o número de segundos

---

## ❓ TROUBLESHOOTING

### **Servidor não inicia automaticamente**

1. Verifique se instalou como Administrador
2. Verifique a tarefa agendada:
   ```powershell
   Get-ScheduledTask -TaskName "MONPEC_Servidor_Django"
   ```
3. Verifique os logs de erro:
   ```powershell
   Get-Content django_error.log -Tail 20
   ```

### **Servidor para e não reinicia**

1. Verifique os logs de erro:
   ```powershell
   Get-Content django_error.log
   ```
2. Verifique se há espaço em disco
3. Verifique se o Python está funcionando:
   ```powershell
   .\python311\python.exe --version
   ```

### **Erro: "Execution policy" ao executar scripts**

Execute no PowerShell como Administrador:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📱 ACESSO PELO CELULAR

Depois de instalar o servidor permanente, o acesso pelo celular continua funcionando:

1. Verifique o IP local do PC:
   ```powershell
   ipconfig | findstr IPv4
   ```

2. No celular, acesse:
   ```
   http://[IP_DO_PC]:8000
   ```
   
   Exemplo: `http://192.168.100.91:8000`

**⚠️ Lembre-se:** PC e celular devem estar na mesma rede Wi-Fi!

---

## 📋 RESUMO RÁPIDO

### **Instalar servidor permanente:**
```powershell
.\INSTALAR_SERVIDOR_PERMANENTE.ps1
```

### **Verificar status:**
```powershell
.\VERIFICAR_SERVIDOR.ps1
```

### **Remover servidor permanente:**
```powershell
.\REMOVER_SERVIDOR_PERMANENTE.ps1
```

### **Ver logs:**
```powershell
Get-Content django_server.log -Tail 20
```

---

**Última atualização:** Dezembro 2025





