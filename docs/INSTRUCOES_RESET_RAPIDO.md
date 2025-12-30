# 🔥 INSTRUÇÕES RÁPIDAS: RESETAR E DEPLOY LIMPO

## ✅ Passo a Passo Simplificado

### **Opção 1: Script Automático (Recomendado)**

1. **Abra o PowerShell** no diretório do projeto
2. **Execute:**
   ```powershell
   .\EXECUTAR_RESET_AGORA.ps1
   ```
3. **Siga as instruções** na tela:
   - Digite `CONFIRMAR` para resetar
   - Digite `EXCLUIR` se quiser excluir o banco (ou Enter para manter)
   - Digite `S` para fazer deploy imediatamente

### **Opção 2: Script Separado (Mais Controle)**

1. **Primeiro, resetar:**
   ```powershell
   .\RESETAR_GOOGLE_CLOUD.ps1
   ```
   - Digite `CONFIRMAR` para continuar
   - Digite `EXCLUIR` se quiser excluir o banco

2. **Depois, fazer deploy:**
   ```powershell
   .\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1
   ```

---

## 📋 O Que Será Excluído

- ✅ Domain Mappings (monpec.com.br e www.monpec.com.br)
- ✅ Jobs Cloud Run (migrate, collectstatic, etc.)
- ✅ Serviço Cloud Run (monpec)
- ⚠️ **Cloud SQL** (opcional - você escolhe se exclui)
- ✅ Imagens Docker no Container Registry

---

## ⏱️ Tempo Estimado

- **Reset**: 2-5 minutos
- **Deploy**: 10-20 minutos
- **Total**: 15-25 minutos

---

## 🆘 Em Caso de Problemas

Se o script der erro:

1. **Verifique autenticação:**
   ```powershell
   gcloud auth list
   gcloud config get-value project
   ```

2. **Execute comandos manualmente** (um por vez):
   ```powershell
   # Excluir domain mappings
   gcloud run domain-mappings delete monpec.com.br --region us-central1
   gcloud run domain-mappings delete www.monpec.com.br --region us-central1
   
   # Excluir jobs
   gcloud run jobs delete migrate-monpec --region us-central1
   gcloud run jobs delete collectstatic-monpec --region us-central1
   
   # Excluir serviço
   gcloud run services delete monpec --region us-central1
   
   # Excluir banco (OPCIONAL - cuidado!)
   gcloud sql instances delete monpec-db
   
   # Excluir imagens
   gcloud container images delete gcr.io/monpec-sistema-rural/monpec --force-delete-tags
   ```

---

**Pronto para começar? Execute o script e siga as instruções!** 🚀






