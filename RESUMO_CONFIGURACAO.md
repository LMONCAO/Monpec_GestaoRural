# 📋 RESUMO DA CONFIGURAÇÃO DO SISTEMA

## ✅ Configuração Atual

O sistema está configurado para usar **`sistema_rural.settings` (DESENVOLVIMENTO)** por padrão.

## 🔧 Como Funciona

### Script PowerShell (`iniciar_sistema_completo.ps1`)
- **Padrão:** `sistema_rural.settings` (DESENVOLVIMENTO)
- **Produção:** Só usa `sistema_rural.settings_producao` se:
  - A variável `$env:DJANGO_ENV='production'` estiver definida, OU
  - O nome do computador contiver "servidor", "server" ou "prod"

### Script Bash (`iniciar_sistema_completo.sh`)
- **Padrão:** `sistema_rural.settings` (DESENVOLVIMENTO)
- **Produção:** Só usa `sistema_rural.settings_producao` se:
  - A variável `DJANGO_ENV=production` estiver definida, OU
  - O hostname contiver "servidor", "server" ou "prod"

## 🚀 Como Iniciar

### Windows (PowerShell):
```powershell
.\iniciar_sistema_completo.ps1
```

### Linux/Mac (Bash):
```bash
./iniciar_sistema_completo.sh
```

## ⚙️ Forçar Produção (se necessário)

### Windows:
```powershell
$env:DJANGO_ENV='production'
.\iniciar_sistema_completo.ps1
```

### Linux/Mac:
```bash
export DJANGO_ENV=production
./iniciar_sistema_completo.sh
```

## 🔍 Verificar Processos

Para verificar quais processos estão rodando:
```powershell
.\verificar_processos_sistema.ps1
```

## 📝 Arquivos de Settings Disponíveis

- ✅ `sistema_rural/settings.py` - DESENVOLVIMENTO (padrão)
- ✅ `sistema_rural/settings_producao.py` - PRODUÇÃO

## ⚠️ Importante

O script automaticamente:
1. Para todos os processos Python existentes antes de iniciar
2. Verifica e libera a porta 8000 se necessário
3. Mostra claramente qual settings está sendo usado
4. Inicia o servidor na porta 8000
















