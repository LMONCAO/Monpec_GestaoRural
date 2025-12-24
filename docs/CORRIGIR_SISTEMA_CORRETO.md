# 🔧 CORRIGIR SISTEMA CORRETO - MARCELO SANGUINO / CANTA GALO

## ⚠️ PROBLEMA IDENTIFICADO

A tarefa agendada do Windows está iniciando o sistema ERRADO de outro diretório:
- **Sistema ERRADO**: `C:\Monpec_projetista\SERVIDOR_PERMANENTE.ps1`
- **Sistema CORRETO**: `C:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural` (este diretório)

## ✅ SISTEMA CORRETO (Este Diretório)

- **Produtor**: Marcelo Sanguino (ID: 2)
- **Fazenda**: FAZENDA CANTA GALO (ID: 2)
- **Inventários**: 9 registros
- **Total**: 12.345 animais, R$ 40.238.000,00
- **Banco de dados**: `db.sqlite3` (neste diretório)

## 🔧 SOLUÇÃO - REMOVER TAREFA ERRADA

### Opção 1: Via PowerShell (Como Administrador)

1. Abra PowerShell como **Administrador**
2. Execute:
```powershell
# Desabilitar tarefa
Disable-ScheduledTask -TaskName "MONPEC_Servidor_Django"

# Remover tarefa permanentemente
Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false
```

### Opção 2: Via Agendador de Tarefas

1. Abra o **Agendador de Tarefas** do Windows
2. Procure por: `MONPEC_Servidor_Django`
3. Clique com botão direito → **Desabilitar** ou **Excluir**

### Opção 3: Via Linha de Comando (Como Administrador)

```cmd
schtasks /Delete /TN "MONPEC_Servidor_Django" /F
```

## 🚀 INICIAR SISTEMA CORRETO

### Opção 1: Executar Manualmente

Duplo clique em: **`INICIAR_SISTEMA_CORRETO.bat`**

Este arquivo:
- Verifica se o banco tem Marcelo Sanguino e Fazenda Canta Galo
- Para todos os processos Python
- Inicia o servidor correto

### Opção 2: Instalar Como Servidor Permanente

1. Clique com botão direito em: **`INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1`**
2. Selecione: **"Executar como administrador"**
3. O script irá:
   - Remover a tarefa antiga
   - Criar nova tarefa que executa o sistema correto
   - Configurar para iniciar automaticamente no login

## 📋 ARQUIVOS CRIADOS

1. **`INICIAR_SISTEMA_CORRETO.bat`** - Inicia o sistema correto (verifica banco antes)
2. **`MONPEC DESENVOLVIMENTO.bat`** - Versão alternativa
3. **`PARAR_TODOS_SISTEMAS.bat`** - Para todos os sistemas
4. **`INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1`** - Instala servidor permanente
5. **`REMOVER_SERVIDOR_PERMANENTE_MONPEC.ps1`** - Remove servidor permanente

## ✅ VERIFICAÇÃO

Para verificar se está usando o sistema correto:

```powershell
python311\python.exe verificar_banco_canta_galo.py
```

Deve mostrar:
- Produtor: Marcelo Sanguino
- Fazenda: FAZENDA CANTA GALO
- 12.345 animais
- R$ 40.238.000,00

## 🎯 CONFIGURAÇÃO CORRETA

- **Settings**: `sistema_rural.settings` (DESENVOLVIMENTO)
- **Banco**: `db.sqlite3` (neste diretório)
- **URL**: `http://127.0.0.1:8000/`
- **Página inicial**: Landing page com vídeo
- **Login**: Página com card promocional acima

