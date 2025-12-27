# 🚀 DEPLOY AUTOMÁTICO COMPLETO - MONPEC.COM.BR

## ✅ Script Criado: `DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1`

Este script executa automaticamente todo o processo de deploy no Google Cloud Run:

### O que o script faz:

1. **Verifica autenticação no Google Cloud**
2. **Habilita APIs necessárias** (Cloud Build, Cloud Run, Container Registry, SQL Admin)
3. **Cria/Verifica instância Cloud SQL PostgreSQL 15**
4. **Cria banco de dados e usuário**
5. **Faz build da imagem Docker**
6. **Faz deploy no Cloud Run**
7. **Aplica migrações do banco de dados**
8. **Coleta arquivos estáticos (collectstatic)**
9. **Configura domínio monpec.com.br e www.monpec.com.br**
10. **Verifica se tudo está funcionando**

### Como executar:

```powershell
# No PowerShell, navegue até o diretório do projeto e execute:
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
.\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1
```

### Pré-requisitos:

1. **Google Cloud SDK instalado** (gcloud CLI)
   - Download: https://cloud.google.com/sdk/docs/install
   
2. **Autenticado no Google Cloud**
   ```powershell
   gcloud auth login
   ```

3. **Projeto configurado** (já está configurado para: `monpec-sistema-rural`)

### Tempo estimado:

- Build da imagem Docker: 5-10 minutos
- Deploy no Cloud Run: 2-3 minutos
- Migrações: 1-2 minutos
- Collectstatic: 1-2 minutos
- **Total: ~10-20 minutos**

### Após o deploy:

1. **Configure os registros DNS** no seu provedor de domínio:
   ```powershell
   gcloud run domain-mappings describe monpec.com.br --region us-central1
   ```

2. **Aguarde a propagação DNS** (5-30 minutos, às vezes até 48 horas)

3. **Acesse o sistema:**
   - URL do Cloud Run (funciona imediatamente)
   - https://monpec.com.br (após configurar DNS)

4. **Criar superusuário:**
   ```powershell
   gcloud run jobs create create-superuser --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --set-cloudsql-instances [CONNECTION_NAME] --set-env-vars [ENV_VARS] --command python --args 'manage.py,createsuperuser' --interactive
   ```

### Configurações padrão do script:

- **Projeto:** monpec-sistema-rural
- **Região:** us-central1
- **Serviço:** monpec
- **Instância Cloud SQL:** monpec-db
- **Banco de dados:** monpec_db
- **Usuário:** monpec_user
- **Senha padrão:** Monpec2025!SenhaSegura (⚠️ **ALTERE EM PRODUÇÃO!**)
- **SECRET_KEY:** chave temporária (⚠️ **ALTERE EM PRODUÇÃO!**)

### ⚠️ IMPORTANTE:

**Altere as senhas e chaves secretas antes de usar em produção!**

Para alterar, edite o script `DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1` nas linhas:
- Linha 16: `$DB_PASSWORD = "SuaSenhaSeguraAqui"`
- Linha 17: `$SECRET_KEY = "SuaChaveSecretaAqui"`

### Verificar status do deploy:

```powershell
# Ver status do serviço
gcloud run services describe monpec --region us-central1

# Ver logs
gcloud run services logs read monpec --region us-central1

# Ver jobs
gcloud run jobs list --region us-central1
```

### Em caso de erro:

1. **Verifique os logs:**
   ```powershell
   gcloud builds log --project monpec-sistema-rural
   gcloud run services logs read monpec --region us-central1
   ```

2. **Verifique se todas as APIs estão habilitadas:**
   ```powershell
   gcloud services list --enabled
   ```

3. **Verifique o status da instância Cloud SQL:**
   ```powershell
   gcloud sql instances describe monpec-db
   ```

---

**Última atualização:** 26/12/2025










