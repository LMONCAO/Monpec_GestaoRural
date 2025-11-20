# ☁️ GUIA DE INSTALAÇÃO - GOOGLE CLOUD SDK

## 🚀 OPÇÃO 1: INSTALAÇÃO AUTOMÁTICA (RECOMENDADO)

Execute o script PowerShell:

```powershell
.\INSTALAR_GCLOUD.ps1
```

O script irá:
- ✅ Baixar o instalador automaticamente
- ✅ Executar a instalação
- ✅ Configurar o PATH

---

## 🚀 OPÇÃO 2: INSTALAÇÃO MANUAL

### **Passo 1: Baixar Instalador**

1. Acesse: https://cloud.google.com/sdk/docs/install
2. Clique em **"Download for Windows"**
3. Baixe o arquivo `GoogleCloudSDKInstaller.exe`

### **Passo 2: Instalar**

1. Execute o arquivo baixado
2. Siga o assistente de instalação
3. Marque a opção **"Run gcloud init"** (opcional)

### **Passo 3: Verificar Instalação**

Abra um **novo** PowerShell e execute:

```powershell
gcloud --version
```

Se aparecer a versão, está instalado! ✅

---

## 🔧 CONFIGURAÇÃO INICIAL

### **1. Inicializar gcloud**

```powershell
gcloud init
```

Isso irá:
- Pedir para fazer login
- Selecionar projeto
- Configurar região padrão

### **2. Autenticar**

```powershell
gcloud auth login
```

Isso abrirá o navegador para autenticação.

### **3. Configurar Projeto**

```powershell
gcloud config set project monpec-sistema-rural
```

---

## ✅ VERIFICAÇÃO

Execute para verificar se está tudo OK:

```powershell
# Ver versão
gcloud --version

# Ver configuração atual
gcloud config list

# Ver projetos disponíveis
gcloud projects list
```

---

## 🆘 PROBLEMAS COMUNS

### **Erro: "gcloud não é reconhecido"**

**Solução:**
1. Reinicie o terminal/PowerShell
2. Se ainda não funcionar, adicione manualmente ao PATH:
   - `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin`
   - Ou: `C:\Users\SEU_USUARIO\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`

### **Erro: "Não foi possível fazer login"**

**Solução:**
1. Verifique conexão com internet
2. Tente: `gcloud auth login --no-launch-browser`
3. Copie o link e cole no navegador

### **Erro: "Projeto não encontrado"**

**Solução:**
1. Verifique se o projeto existe no console: https://console.cloud.google.com
2. Verifique se está autenticado: `gcloud auth list`
3. Liste projetos: `gcloud projects list`

---

## 📋 PRÓXIMOS PASSOS

Após instalar e configurar:

1. ✅ Execute: `.\DEPLOY_GCP.ps1` para fazer deploy
2. ✅ Ou siga o guia: `DEPLOY_GOOGLE_CLOUD.md`

---

**🎉 Pronto para usar o Google Cloud!**







