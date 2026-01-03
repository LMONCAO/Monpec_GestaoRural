# 📖 GUIA DE USO - SCRIPTS DE LIMPEZA E INSTALAÇÃO

**Data:** 2025-01-27  
**Projeto:** monpec-sistema-rural

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Scripts Disponíveis](#scripts-disponíveis)
4. [Como Usar](#como-usar)
5. [Resolução de Problemas](#resolução-de-problemas)
6. [FAQ](#faq)

---

## 🎯 VISÃO GERAL

Este guia explica como usar os scripts de limpeza e instalação do sistema MONPEC no Google Cloud Platform. Os scripts foram criados para resolver problemas de deploy causados por configurações conflitantes e recursos antigos.

### O que os scripts fazem?

**Scripts de Limpeza:**
- Deletam serviços Cloud Run antigos
- Deletam jobs do Cloud Run
- Deletam instância Cloud SQL (com confirmação)
- Deletam imagens Docker antigas
- Deletam domain mappings

**Scripts de Instalação:**
- Criam nova instância Cloud SQL PostgreSQL 15
- Criam banco de dados e usuário
- Fazem build da imagem Docker
- Fazem deploy no Cloud Run com configurações corretas
- Configuram variáveis de ambiente
- Aplicam migrações do Django
- Coletam arquivos estáticos

---

## ✅ PRÉ-REQUISITOS

### 1. Google Cloud SDK (gcloud CLI)

**Windows:**
```powershell
# Baixar e instalar de:
# https://cloud.google.com/sdk/docs/install
```

**Linux/Mac:**
```bash
# Instalar via script
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Verificar instalação:**
```bash
gcloud --version
```

### 2. Autenticação no Google Cloud

```bash
# Fazer login
gcloud auth login

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Verificar projeto atual
gcloud config get-value project
```

### 3. Permissões Necessárias

Você precisa ter as seguintes permissões no projeto:
- **Cloud Run Admin** - Para criar/deletar serviços
- **Cloud SQL Admin** - Para criar/deletar instâncias
- **Cloud Build Editor** - Para fazer build de imagens
- **Service Account User** - Para executar serviços
- **Storage Admin** - Para gerenciar imagens Docker

### 4. APIs Habilitadas

Os scripts habilitam automaticamente, mas você pode verificar:

```bash
gcloud services list --enabled
```

APIs necessárias:
- `cloudbuild.googleapis.com`
- `run.googleapis.com`
- `containerregistry.googleapis.com`
- `sqladmin.googleapis.com`
- `sql-component.googleapis.com`

---

## 📚 SCRIPTS DISPONÍVEIS

### Scripts de Limpeza

| Script | Plataforma | Descrição |
|--------|-----------|-----------|
| `LIMPAR_RECURSOS_GCP.sh` | Linux/Mac/Cloud Shell | Limpa recursos do GCP |
| `LIMPAR_RECURSOS_GCP.ps1` | Windows PowerShell | Limpa recursos do GCP |

### Scripts de Instalação

| Script | Plataforma | Descrição |
|--------|-----------|-----------|
| `INSTALAR_DO_ZERO.sh` | Linux/Mac/Cloud Shell | Instala tudo do zero |
| `INSTALAR_DO_ZERO.ps1` | Windows PowerShell | Instala tudo do zero |

### Script Completo

| Script | Plataforma | Descrição |
|--------|-----------|-----------|
| `LIMPAR_E_INSTALAR_COMPLETO.sh` | Linux/Mac/Cloud Shell | Limpa e instala em sequência |

---

## 🚀 COMO USAR

### Opção 1: Limpar e Instalar Separadamente

#### No Windows (PowerShell):

```powershell
# 1. Limpar recursos
.\LIMPAR_RECURSOS_GCP.ps1

# 2. Instalar do zero
.\INSTALAR_DO_ZERO.ps1
```

#### No Linux/Mac/Cloud Shell:

```bash
# 1. Dar permissão de execução
chmod +x LIMPAR_RECURSOS_GCP.sh INSTALAR_DO_ZERO.sh

# 2. Limpar recursos
./LIMPAR_RECURSOS_GCP.sh

# 3. Instalar do zero
./INSTALAR_DO_ZERO.sh
```

### Opção 2: Limpar e Instalar em Sequência (Recomendado)

#### No Linux/Mac/Cloud Shell:

```bash
# 1. Dar permissão de execução
chmod +x LIMPAR_E_INSTALAR_COMPLETO.sh

# 2. Executar tudo de uma vez
./LIMPAR_E_INSTALAR_COMPLETO.sh
```

---

## 📝 PROCESSO DETALHADO

### Passo 1: Preparação

1. **Fazer backup dos dados** (se houver dados importantes)
2. **Verificar projeto Google Cloud:**
   ```bash
   gcloud config get-value project
   ```
3. **Ter senha do banco pronta** (mínimo 8 caracteres)
4. **Ter SECRET_KEY do Django** (ou deixar gerar automaticamente)

### Passo 2: Executar Limpeza

O script de limpeza vai:
1. Verificar projeto atual
2. Pedir confirmação
3. Deletar serviço Cloud Run
4. Deletar jobs do Cloud Run
5. Deletar instância Cloud SQL (com confirmação dupla)
6. Deletar imagens Docker antigas (com confirmação)
7. Deletar domain mappings

**⚠️ ATENÇÃO:** A exclusão do banco de dados requer confirmação explícita digitando "DELETAR BANCO".

### Passo 3: Executar Instalação

O script de instalação vai:
1. Verificar projeto atual
2. Habilitar APIs necessárias
3. Solicitar senha do banco de dados
4. Solicitar SECRET_KEY (ou gerar automaticamente)
5. Criar instância Cloud SQL PostgreSQL 15
6. Criar banco de dados e usuário
7. Fazer build da imagem Docker
8. Fazer deploy no Cloud Run
9. Configurar variáveis de ambiente
10. Aplicar migrações
11. Coletar arquivos estáticos

### Passo 4: Pós-Instalação

Após a instalação, você precisará:

1. **Criar superusuário:**
   ```bash
   gcloud run jobs create create-superuser \
     --image gcr.io/monpec-sistema-rural/monpec \
     --region us-central1 \
     --set-cloudsql-instances [CONNECTION_NAME] \
     --set-env-vars [ENV_VARS] \
     --command python \
     --args 'manage.py,createsuperuser' \
     --interactive
   
   gcloud run jobs execute create-superuser --region us-central1
   ```

2. **Configurar domínio personalizado (opcional):**
   ```bash
   gcloud run domain-mappings create \
     --service monpec \
     --domain monpec.com.br \
     --region us-central1
   ```

3. **Acessar o sistema:**
   - URL será exibida ao final da instalação
   - Formato: `https://monpec-xxxxx-uc.a.run.app`

---

## 🔧 RESOLUÇÃO DE PROBLEMAS

### Erro: "gcloud: command not found"

**Solução:**
- Instale o Google Cloud SDK
- Verifique se está no PATH
- Reinicie o terminal

### Erro: "Permission denied"

**Solução:**
```bash
# No Linux/Mac, dar permissão de execução
chmod +x *.sh
```

### Erro: "Project not found"

**Solução:**
```bash
# Verificar projeto atual
gcloud config get-value project

# Configurar projeto correto
gcloud config set project monpec-sistema-rural
```

### Erro: "Insufficient permissions"

**Solução:**
- Verifique se você tem as permissões necessárias
- Entre em contato com o administrador do projeto
- Verifique se as APIs estão habilitadas

### Erro: "Instance already exists"

**Solução:**
- Execute o script de limpeza primeiro
- Ou use a instância existente (o script pergunta)

### Erro: "Build timeout"

**Solução:**
- O timeout padrão é 600s (10 minutos)
- Se o build demorar mais, aumente o timeout no script
- Verifique se há problemas de rede

### Erro: "Migration failed"

**Solução:**
- Verifique os logs do job de migração:
  ```bash
  gcloud run jobs executions list --job migrate-monpec --region us-central1
  ```
- Verifique se o banco de dados está acessível
- Verifique se as variáveis de ambiente estão corretas

### Erro: "Service not found"

**Solução:**
- Verifique se o deploy foi concluído
- Verifique se o serviço existe:
  ```bash
  gcloud run services list --region us-central1
  ```

---

## ❓ FAQ

### P: Os scripts vão deletar meus dados?

**R:** Sim, os scripts de limpeza vão deletar todos os recursos do GCP, incluindo o banco de dados. **SEMPRE faça backup antes de executar!**

### P: Posso executar apenas a instalação sem limpar?

**R:** Sim, mas pode haver conflitos com recursos antigos. Recomendamos limpar primeiro.

### P: Quanto tempo leva a instalação completa?

**R:** Aproximadamente 15-30 minutos, dependendo da velocidade da rede e do build da imagem Docker.

### P: Posso cancelar durante a execução?

**R:** Sim, mas alguns recursos podem já ter sido criados/deletados. Você precisará limpar manualmente.

### P: Como faço backup do banco de dados?

**R:**
```bash
# Exportar banco de dados
gcloud sql export sql monpec-db gs://[BUCKET]/backup.sql \
  --database=monpec_db
```

### P: Posso usar uma instância Cloud SQL existente?

**R:** Sim, o script pergunta se você quer usar uma instância existente.

### P: Como configuro variáveis de ambiente adicionais?

**R:** Após a instalação, você pode atualizar:
```bash
gcloud run services update monpec \
  --region us-central1 \
  --update-env-vars VARIAVEL=valor
```

### P: Como vejo os logs do serviço?

**R:**
```bash
gcloud run services logs tail monpec --region us-central1
```

### P: Como atualizo o código após a instalação?

**R:**
```bash
# Fazer build e deploy novamente
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1
```

---

## 📞 SUPORTE

Se encontrar problemas não listados aqui:

1. Consulte `RELATORIO_PROBLEMAS_DEPLOY_GCP.md` para detalhes dos problemas
2. Verifique os logs do Google Cloud Console
3. Verifique os logs do Cloud Run:
   ```bash
   gcloud run services logs tail monpec --region us-central1
   ```

---

## 📚 ARQUIVOS RELACIONADOS

- `RELATORIO_PROBLEMAS_DEPLOY_GCP.md` - Relatório completo de problemas
- `RESUMO_EXECUTIVO_SOLUCAO.md` - Resumo executivo da solução
- `LIMPAR_RECURSOS_GCP.sh` / `.ps1` - Scripts de limpeza
- `INSTALAR_DO_ZERO.sh` / `.ps1` - Scripts de instalação
- `LIMPAR_E_INSTALAR_COMPLETO.sh` - Script completo

---

**Status:** ✅ Pronto para uso  
**Última atualização:** 2025-01-27























