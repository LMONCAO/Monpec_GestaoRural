# 🔥 INSTRUÇÕES: RESETAR GOOGLE CLOUD COMPLETAMENTE

Este guia explica como excluir **TODOS** os recursos do Google Cloud do projeto e fazer um reset completo do ambiente.

## ⚠️ ATENÇÃO

**Este processo é IRREVERSÍVEL e vai excluir:**
- ✅ Todos os serviços Cloud Run
- ✅ Todos os jobs Cloud Run
- ✅ Instância Cloud SQL (e **TODOS os dados do banco**)
- ✅ Domain Mappings
- ✅ Imagens Docker no Container Registry

**Faça backup dos dados importantes antes de executar!**

---

## 📋 Métodos para Resetar

### Método 1: PowerShell (Windows)

```powershell
# Navegue até o diretório do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Execute o script de reset
.\RESETAR_GOOGLE_CLOUD.ps1
```

### Método 2: Bash / Google Cloud Shell

```bash
# No Google Cloud Shell ou terminal Linux/Mac
chmod +x RESETAR_GOOGLE_CLOUD.sh
./RESETAR_GOOGLE_CLOUD.sh
```

---

## 🔄 Processo de Reset

O script executa as seguintes etapas:

### 1. **Domain Mappings**
- Exclui `monpec.com.br`
- Exclui `www.monpec.com.br`

### 2. **Cloud Run Jobs**
- Exclui `migrate-monpec`
- Exclui `collectstatic-monpec`
- Exclui `create-superuser`
- Exclui qualquer outro job encontrado

### 3. **Cloud Run Services**
- Exclui o serviço `monpec`
- Exclui qualquer outro serviço encontrado

### 4. **Cloud SQL** ⚠️
- **PERGUNTA antes de excluir** a instância `monpec-db`
- Se confirmar, exclui o banco e **TODOS os dados permanentemente**
- Se não confirmar, mantém o banco

### 5. **Container Registry**
- Exclui todas as imagens Docker do projeto
- Inclui a imagem `gcr.io/monpec-sistema-rural/monpec`

### 6. **Build History**
- Mostra builds antigos (não exclui automaticamente)

---

## ✅ Após o Reset

Após executar o reset, você pode fazer um **novo deploy limpo**:

### Deploy Automático (PowerShell)
```powershell
.\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1
```

### Deploy no Cloud Shell (Bash)
```bash
chmod +x DEPLOY_GOOGLE_CLOUD_SHELL.sh
./DEPLOY_GOOGLE_CLOUD_SHELL.sh
```

---

## 🛠️ Reset Manual (Alternativa)

Se preferir fazer manualmente, execute os comandos abaixo:

### 1. Excluir Domain Mappings
```bash
gcloud run domain-mappings delete monpec.com.br --region us-central1
gcloud run domain-mappings delete www.monpec.com.br --region us-central1
```

### 2. Excluir Jobs
```bash
gcloud run jobs delete migrate-monpec --region us-central1
gcloud run jobs delete collectstatic-monpec --region us-central1
gcloud run jobs delete create-superuser --region us-central1
```

### 3. Excluir Serviços Cloud Run
```bash
gcloud run services delete monpec --region us-central1
```

### 4. Excluir Cloud SQL (CUIDADO!)
```bash
# ⚠️ Isso exclui TODOS os dados!
gcloud sql instances delete monpec-db
```

### 5. Excluir Imagens Docker
```bash
# Listar imagens
gcloud container images list --repository=gcr.io/monpec-sistema-rural

# Excluir imagem específica
gcloud container images delete gcr.io/monpec-sistema-rural/monpec --force-delete-tags
```

---

## 📝 Verificar Recursos Restantes

Para verificar se ainda existem recursos:

```bash
# Listar serviços Cloud Run
gcloud run services list --region us-central1

# Listar jobs Cloud Run
gcloud run jobs list --region us-central1

# Listar instâncias Cloud SQL
gcloud sql instances list

# Listar domain mappings
gcloud run domain-mappings list --region us-central1

# Listar imagens
gcloud container images list --repository=gcr.io/monpec-sistema-rural
```

---

## ⚠️ Avisos Importantes

1. **Backup de Dados**: Faça backup do banco de dados antes de excluir!
   ```bash
   gcloud sql export sql monpec-db gs://[BUCKET]/backup.sql --database=monpec_db
   ```

2. **Domain DNS**: Se excluir domain mappings, você precisará reconfigurar os registros DNS após o novo deploy.

3. **Custos**: Alguns recursos podem continuar gerando custos até serem completamente excluídos (geralmente alguns minutos).

4. **Tempo de Exclusão**: A exclusão de instâncias Cloud SQL pode levar alguns minutos.

---

## 🆘 Problemas Comuns

### Erro: "Resource not found"
- Normal se o recurso já foi excluído antes
- O script continua mesmo com esses erros

### Erro: "Permission denied"
- Verifique se está autenticado: `gcloud auth list`
- Verifique se tem permissões no projeto: `gcloud projects get-iam-policy monpec-sistema-rural`

### Erro: "Cannot delete instance that has backups"
- Desabilite backups primeiro ou aguarde alguns dias após desabilitar

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `gcloud logging read`
2. Verifique o status: `gcloud projects describe monpec-sistema-rural`
3. Consulte a documentação: https://cloud.google.com/docs

---

**Última atualização:** 26/12/2025






