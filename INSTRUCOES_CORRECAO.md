# 🔧 INSTRUÇÕES PARA CORRIGIR O SISTEMA

## ⚠️ PROBLEMA IDENTIFICADO

A tarefa agendada do Windows está iniciando o sistema do **diretório errado**:
- ❌ **Diretório ERRADO**: `C:\Monpec_projetista\SERVIDOR_PERMANENTE.ps1`
- ✅ **Diretório CORRETO**: `C:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural` (com banco Marcelo Sanguino / Fazenda Canta Galo)

## ✅ SOLUÇÃO RÁPIDA

### Opção 1: Script Automático (RECOMENDADO)

1. **Clique com botão direito** em: `CORRIGIR_SISTEMA_ADMIN.bat`
2. Selecione: **"Executar como administrador"**
3. O script irá:
   - Parar processos Python
   - Remover a tarefa antiga (diretório errado)
   - Verificar o banco de dados
   - Criar nova tarefa apontando para o diretório correto
   - Instalar o servidor permanente correto

### Opção 2: Script PowerShell

1. **Clique com botão direito** em: `CORRIGIR_TAREFA_AGENDADA_AGORA.ps1`
2. Selecione: **"Executar como administrador"**
3. O script fará a correção automaticamente

### Opção 3: Manual (PowerShell como Admin)

Abra PowerShell **como Administrador** e execute:

```powershell
# 1. Parar e remover tarefa antiga
schtasks /Delete /TN "MONPEC_Servidor_Django" /F

# 2. Executar script de instalação
cd "C:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural"
.\INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1
```

## 📋 VERIFICAÇÃO DO BANCO DE DADOS

O banco de dados está **CORRETO**:
- ✅ **Produtor**: Marcelo Sanguino (ID: 2)
- ✅ **Fazenda**: FAZENDA CANTA GALO (ID: 2)
- ✅ **Inventários**: 9 registros
- ✅ **Total**: 12.345 animais
- ✅ **Arquivo**: `db.sqlite3` (neste diretório)

## 🚀 INICIAR MANUALMENTE (SEM TAREFA AGENDADA)

Se preferir iniciar manualmente, use sempre:

**`INICIAR_SISTEMA_CORRETO.bat`**

Este arquivo:
- ✅ Verifica se o banco tem Marcelo Sanguino e Fazenda Canta Galo
- ✅ Para todos os processos Python
- ✅ Inicia o servidor correto
- ✅ Impede inicialização se o banco estiver errado

## 📝 ARQUIVOS CRIADOS/MODIFICADOS

1. ✅ **`INICIAR_SISTEMA.bat`** - Atualizado para redirecionar ao script correto
2. ✅ **`MONPEC DESENVOLVIMENTO.bat`** - Atualizado para verificar banco antes de iniciar
3. ✅ **`CORRIGIR_SISTEMA_ADMIN.bat`** - Script para correção automática (executar como Admin)
4. ✅ **`CORRIGIR_TAREFA_AGENDADA_AGORA.ps1`** - Script PowerShell para correção
5. ✅ **`VERIFICAR_E_CORRIGIR_SISTEMA.ps1`** - Script para verificar status do sistema

## ⚙️ CONFIGURAÇÃO APÓS CORREÇÃO

Após executar a correção, o sistema será configurado para:
- ✅ Iniciar automaticamente quando você fizer login no Windows
- ✅ Usar sempre o banco correto (db.sqlite3 com Marcelo Sanguino)
- ✅ Reiniciar automaticamente se o servidor parar
- ✅ URL: http://127.0.0.1:8000/

## 🔍 VERIFICAR SE ESTÁ CORRETO

Execute: `VERIFICAR_E_CORRIGIR_SISTEMA.ps1`

Este script mostra:
- Status do banco de dados
- Tarefa agendada (diretório e arquivo)
- Processos Python rodando
- Porta 8000 em uso













