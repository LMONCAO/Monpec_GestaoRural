# 🔧 Solução para Erro de Deploy

## ❌ Problema

Ao executar o script `DEPLOY_COMPLETO.ps1`, você recebe o erro:
```
O argumento 'DEPLOY_COMPLETO.ps1' para o parâmetro -File não existe.
```

## 🔍 Causa

O erro ocorre porque:
1. O PowerShell não está no diretório correto do projeto
2. O caminho do arquivo não está sendo resolvido corretamente
3. Problemas de codificação de caracteres no caminho (especialmente "ç" em "Orçamentario")

## ✅ Soluções

### Solução 1: Usar o Script Wrapper (Recomendado)

Execute o novo script wrapper que resolve automaticamente o problema:

**Windows (PowerShell):**
```powershell
.\EXECUTAR_DEPLOY.ps1
```

**Windows (CMD/Batch):**
```cmd
EXECUTAR_DEPLOY.bat
```

### Solução 2: Navegar para o Diretório Correto

1. Abra o PowerShell ou CMD
2. Navegue para o diretório do projeto:
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
```

3. Execute o script:
```powershell
.\DEPLOY_COMPLETO.ps1
```

### Solução 3: Usar Caminho Absoluto

Execute o script usando o caminho completo:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural\DEPLOY_COMPLETO.ps1"
```

### Solução 4: Usar o Script Batch Existente

Execute o arquivo `.bat` que já existe no projeto:

```cmd
DEPLOY_COMPLETO.bat
```

## 🔍 Verificar se o Arquivo Existe

Para verificar se o arquivo está no lugar correto:

```powershell
Test-Path "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural\DEPLOY_COMPLETO.ps1"
```

Deve retornar `True`.

## 📋 Checklist

Antes de executar o deploy, verifique:

- [ ] Você está no diretório correto do projeto
- [ ] O arquivo `DEPLOY_COMPLETO.ps1` existe
- [ ] Você tem permissões de execução no PowerShell
- [ ] O Google Cloud SDK está instalado (`gcloud --version`)
- [ ] Você está autenticado no Google Cloud (`gcloud auth list`)

## 🚀 Execução Rápida

A forma mais rápida de executar:

1. Abra o PowerShell
2. Execute:
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
.\EXECUTAR_DEPLOY.ps1
```

Ou simplesmente dê duplo clique em `EXECUTAR_DEPLOY.bat`

## ⚠️ Nota sobre Codificação

Se você ainda tiver problemas com caracteres especiais, certifique-se de que:
- O PowerShell está configurado para UTF-8: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
- O terminal suporta UTF-8

















