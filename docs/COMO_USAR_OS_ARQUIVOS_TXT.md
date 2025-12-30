# 📝 Como Usar os Arquivos .txt

## ⚠️ IMPORTANTE: Entendendo os Arquivos .txt

Os arquivos `.txt` que você tem no projeto (como `COMANDO_FINAL_CLOUD_SHELL.txt`, `COMANDO_UNICO_ATUALIZAR_CLOUD_SHELL.txt`, etc.) são comandos para executar no **Google Cloud Shell** (no navegador), **NÃO** no Windows Command Prompt.

## 🎯 Duas Opções para Fazer Deploy

### ✅ OPÇÃO 1: Script PowerShell Local (MAIS FÁCIL)

Use o script que acabei de criar: `DEPLOY_DIRETO_GOOGLE_CLOUD.ps1`

**No PowerShell ou Google Cloud SDK Shell:**

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
.\DEPLOY_DIRETO_GOOGLE_CLOUD.ps1
```

Este script faz tudo automaticamente:
- ✅ Build da imagem
- ✅ Deploy no Cloud Run
- ✅ Mostra a URL do serviço

---

### ✅ OPÇÃO 2: Usar os Arquivos .txt no Cloud Shell

Se preferir usar os comandos dos arquivos `.txt`, você precisa:

1. **Abrir o Google Cloud Shell** (no navegador):
   - Acesse: https://console.cloud.google.com/
   - Clique no ícone do terminal no canto superior direito (Cloud Shell)

2. **Fazer upload do código** para o Cloud Shell:
   - No Cloud Shell, clique nos 3 pontinhos (menu) → "Upload file"
   - Ou use `gcloud cloud-shell scp` para copiar arquivos

3. **Copiar e colar o conteúdo** de um dos arquivos `.txt`:
   - Abra o arquivo (ex: `COMANDO_FINAL_CLOUD_SHELL.txt`)
   - Copie TODO o conteúdo
   - Cole no Cloud Shell
   - Pressione Enter

---

## 📋 Qual Arquivo .txt Usar?

### Para Deploy Completo:
- **`COMANDO_FINAL_CLOUD_SHELL.txt`** - Deploy completo com correções

### Para Atualização Rápida:
- **`COMANDO_UNICO_ATUALIZAR_CLOUD_SHELL.txt`** - Atualização rápida

### Para Corrigir Erros:
- **`COMANDO_CORRIGIR_E_DEPLOY.txt`** - Corrige erros e faz deploy

---

## 🚀 RECOMENDAÇÃO

**Use o script PowerShell local** (`DEPLOY_DIRETO_GOOGLE_CLOUD.ps1`) porque:
- ✅ Mais fácil (não precisa abrir navegador)
- ✅ Funciona direto do seu computador
- ✅ Não precisa fazer upload de arquivos
- ✅ Mais rápido

Os arquivos `.txt` são úteis se você quiser executar comandos diretamente no Cloud Shell do navegador.

---

## ⚠️ IMPORTANTE

**NÃO tente executar os comandos dos arquivos `.txt` no Command Prompt do Windows!**

Eles são comandos bash/Linux para o Cloud Shell. Use:
- **Windows**: Script PowerShell (`DEPLOY_DIRETO_GOOGLE_CLOUD.ps1`)
- **Cloud Shell (navegador)**: Comandos dos arquivos `.txt`



