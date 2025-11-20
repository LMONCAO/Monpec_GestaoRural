# ⚡ INÍCIO SUPER RÁPIDO - 3 Comandos Essenciais

## 🎯 **Para quem quer começar AGORA**

### **1. Verificar Tudo (30 segundos)**
```bash
# No Cloud Shell Editor, execute:
bash verificar_pre_deploy.sh

# Ou no PowerShell (Windows):
.\verificar_pre_deploy.ps1
```

### **2. Seguir o Guia Completo**
Abra o arquivo: **`COMECE_AGORA.md`**

Copie e cole os comandos na ordem!

### **3. Se Precisar de Ajuda**
- Ver logs: `gcloud run services logs read monpec --region us-central1`
- Ver status: `gcloud run services describe monpec --region us-central1`

---

## 📋 **ORDEM DOS ARQUIVOS PARA LER**

1. ✅ **`COMECE_AGORA.md`** ← **COMECE AQUI!**
2. 📖 `PASSO_A_PASSO_DEPLOY_GOOGLE_CLOUD.md` (detalhado)
3. 🔍 `VERIFICACAO_PRE_DEPLOY.md` (checklist)
4. 📚 `COMANDOS_RAPIDOS_GOOGLE_CLOUD.md` (referência)

---

## 🚀 **COMANDO ÚNICO PARA COMEÇAR**

```bash
# No Cloud Shell Editor, copie e cole tudo de uma vez:

gcloud auth login && \
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural" && \
gcloud config set project monpec-sistema-rural && \
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com && \
echo "✅ Configuração inicial concluída! Agora siga o COMECE_AGORA.md"
```

---

**🎯 Pronto! Agora é só seguir o `COMECE_AGORA.md`!**







