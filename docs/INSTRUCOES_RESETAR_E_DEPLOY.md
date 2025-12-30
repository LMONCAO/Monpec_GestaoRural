# 🔥 Instruções: Resetar e Deploy do Zero

## 📋 O que este script faz?

O script `RESETAR_E_DEPLOY_DO_ZERO.sh` faz um **reset completo** do Google Cloud e depois faz um **deploy do zero** com todos os seus arquivos.

### Etapas do Script:

1. ✅ **Exclui todos os recursos existentes:**
   - Serviços Cloud Run
   - Jobs Cloud Run  
   - Domain Mappings
   - Imagens Docker no Container Registry
   - (Opcional) Instância Cloud SQL e todos os dados

2. ✅ **Configura o banco de dados:**
   - Cria nova instância Cloud SQL (se necessário)
   - Cria banco de dados e usuário
   - Configura senhas

3. ✅ **Faz build da imagem Docker:**
   - Verifica arquivos necessários (Dockerfile, requirements)
   - Faz build completo da imagem

4. ✅ **Faz deploy completo:**
   - Deploy no Cloud Run
   - Configura variáveis de ambiente
   - Conecta ao Cloud SQL
   - Configura recursos (CPU, memória, timeout)

5. ✅ **Fornece informações finais:**
   - URL do serviço
   - Credenciais de acesso

---

## 🚀 Como Usar

### Opção 1: Google Cloud Shell (RECOMENDADO)

1. Acesse o [Google Cloud Shell](https://shell.cloud.google.com/)
2. Faça upload dos arquivos do projeto para o Cloud Shell:
   ```bash
   # No Cloud Shell, use o botão de upload (ícone de pasta) 
   # para fazer upload dos arquivos do projeto
   ```

3. Execute o script:
   ```bash
   bash RESETAR_E_DEPLOY_DO_ZERO.sh
   ```

### Opção 2: Terminal Local (Linux/Mac/WSL)

1. Instale o Google Cloud SDK:
   - https://cloud.google.com/sdk/docs/install

2. Faça login:
   ```bash
   gcloud auth login
   ```

3. Execute o script:
   ```bash
   bash RESETAR_E_DEPLOY_DO_ZERO.sh
   ```

---

## ⚠️ IMPORTANTE: Antes de Executar

### 🔴 ATENÇÃO CRÍTICA:

- **O script EXCLUI todos os recursos do projeto**
- **Se você escolher excluir o Cloud SQL, TODOS OS DADOS serão perdidos permanentemente**
- **Faça backup do banco de dados antes de executar!**

### ✅ Checklist Antes de Executar:

- [ ] Fiz backup do banco de dados (se quiser manter os dados)
- [ ] Estou no diretório raiz do projeto Django
- [ ] Os arquivos estão no Cloud Shell (se usar Cloud Shell)
- [ ] Estou autenticado no Google Cloud
- [ ] Tenho permissões de administrador no projeto

---

## 📝 Arquivos Necessários

O script verifica automaticamente se os seguintes arquivos existem:

- ✅ `Dockerfile.prod` ou `Dockerfile`
- ✅ `requirements_producao.txt` ou `requirements.txt`
- ✅ `manage.py`
- ✅ Arquivos do projeto Django

Se algum arquivo estiver faltando, o script vai parar e informar qual está faltando.

---

## 🔐 Credenciais Padrão

Após o deploy, você pode acessar o sistema com:

- **Username:** `admin`
- **Senha:** `L6171r12@@`

⚠️ **IMPORTANTE:** Altere a senha após o primeiro acesso!

---

## 🛠️ Configurações do Script

As configurações estão no início do script. Você pode alterar se necessário:

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
```

---

## 📊 O que Esperar Durante a Execução

### Tempo Total Estimado: 10-20 minutos

1. **Confirmação e configuração:** ~30 segundos
2. **Exclusão de recursos:** ~1-2 minutos
3. **Configuração do Cloud SQL:** ~3-5 minutos (se criar nova instância)
4. **Build da imagem Docker:** ~5-15 minutos ⏳ (depende da velocidade)
5. **Deploy no Cloud Run:** ~2-5 minutos
6. **Verificação final:** ~30 segundos

⚠️ **Não feche o terminal durante a execução!**

---

## 🔍 Verificando o Deploy

Após o deploy concluir, você pode:

### Ver logs do serviço:
```bash
gcloud run services logs read monpec --region us-central1
```

### Ver status do serviço:
```bash
gcloud run services describe monpec --region us-central1
```

### Ver URL do serviço:
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

---

## ❓ Solução de Problemas

### Erro: "gcloud CLI não está instalado"
- Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### Erro: "Não autenticado"
- Execute: `gcloud auth login`

### Erro: "Dockerfile não encontrado"
- Certifique-se de estar no diretório raiz do projeto
- Verifique se o arquivo `Dockerfile.prod` ou `Dockerfile` existe

### Erro: "Erro no build"
- Verifique se o `Dockerfile.prod` está correto
- Verifique se o `requirements_producao.txt` não tem erros
- Veja os logs do build: `gcloud builds list --limit=1`

### Erro: "Erro no deploy"
- Verifique se a instância Cloud SQL existe e está acessível
- Verifique as permissões do serviço
- Veja os logs: `gcloud run services logs read monpec --region us-central1`

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do Cloud Run
2. Verifique os logs do Cloud Build
3. Verifique se todas as APIs estão habilitadas
4. Verifique se você tem permissões adequadas no projeto

---

## ✅ Depois do Deploy

1. Acesse a URL fornecida pelo script
2. Faça login com as credenciais padrão
3. **ALTERE A SENHA IMEDIATAMENTE**
4. Configure o domínio personalizado (se necessário)
5. Configure backups automáticos

---

**🎉 Pronto! Agora você tem um script completo para resetar tudo e fazer deploy do zero!**

