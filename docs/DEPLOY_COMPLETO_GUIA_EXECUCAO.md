# 🚀 Guia de Execução - Deploy Completo MONPEC

## ✅ O que está configurado:

1. ✅ **Loading Page atualizada** - Landing page com todas as funcionalidades
2. ✅ **Botão Demonstração** - Funcionando e abrindo modal
3. ✅ **Formulário de Demonstração** - Processando dados e criando usuários
4. ✅ **Sistema Assinante** - Configurado e funcionando
5. ✅ **Mercado Pago** - Chaves configuradas e URLs de sucesso/cancelamento
6. ✅ **Usuário Admin** - Criado automaticamente com senha `L6171r12@@`

## 📋 Pré-requisitos:

1. **Google Cloud SDK instalado**
   - Verificar: `gcloud --version`
   - Instalar se necessário: https://cloud.google.com/sdk/docs/install

2. **Autenticado no Google Cloud**
   - Executar: `gcloud auth login`
   - Verificar: `gcloud auth list`

3. **Projeto configurado**
   - Projeto: `monpec-sistema-rural`
   - Região: `us-central1`

## 🎯 Executar Deploy:

### Opção 1: Script Completo Atualizado (Recomendado)

```powershell
.\DEPLOY_COMPLETO_FINAL_ATUALIZADO.ps1
```

Este script faz **TUDO** automaticamente:
- ✅ Habilita APIs necessárias
- ✅ Cria/verifica Cloud SQL
- ✅ Faz build da imagem Docker
- ✅ Faz deploy no Cloud Run
- ✅ Aplica migrações
- ✅ Coleta arquivos estáticos
- ✅ Cria usuário admin
- ✅ Configura domain mappings
- ✅ Configura Mercado Pago

### Opção 2: Script Corrigido Original

```powershell
.\DEPLOY_COMPLETO_CORRIGIDO.ps1
```

## ⏱️ Tempo Estimado:

- **Build da imagem**: 5-10 minutos
- **Deploy**: 2-3 minutos
- **Migrações**: 1-2 minutos
- **Collectstatic**: 1-2 minutos
- **Total**: ~15-20 minutos

## 🔐 Credenciais Configuradas:

### Usuário Admin:
- **Username**: `admin`
- **Senha**: `L6171r12@@`
- **Email**: `admin@monpec.com.br`

### Mercado Pago:
- **Access Token**: Configurado via variável de ambiente
- **Public Key**: Configurado via variável de ambiente
- **Success URL**: `https://monpec.com.br/assinaturas/sucesso/`
- **Cancel URL**: `https://monpec.com.br/assinaturas/cancelado/`

## 🌐 URLs do Sistema:

Após o deploy, o sistema estará disponível em:

1. **Cloud Run URL**: Será exibida ao final do script
   - Formato: `https://monpec-XXXXX.us-central1.run.app`

2. **Domínio Personalizado** (após configurar DNS):
   - `https://monpec.com.br`
   - `https://www.monpec.com.br`

## 📝 Após o Deploy:

### 1. Verificar Status do Serviço:

```powershell
gcloud run services describe monpec --region us-central1
```

### 2. Verificar Logs:

```powershell
gcloud run services logs read monpec --region us-central1 --limit 50
```

### 3. Testar Landing Page:

- Acesse a URL do Cloud Run
- Verifique se a landing page carrega
- Teste o botão "Demonstração"
- Preencha o formulário de demonstração

### 4. Testar Login Admin:

- Acesse: `{URL}/login/`
- Username: `admin`
- Senha: `L6171r12@@`

### 5. Testar Sistema Assinante:

- Após login, acesse: `{URL}/assinaturas/`
- Verifique se os planos aparecem
- Teste o fluxo de checkout do Mercado Pago

## 🔧 Configuração de DNS (Opcional):

Se quiser usar o domínio personalizado:

1. **Obter informações do domain mapping**:

```powershell
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

2. **Configurar registros DNS** no seu provedor:
   - Tipo: `CNAME`
   - Nome: `@` (ou `monpec.com.br`)
   - Valor: O valor retornado pelo comando acima

3. **Aguardar propagação DNS** (5-30 minutos)

## ⚠️ Troubleshooting:

### Erro: "gcloud não encontrado"
- Instale o Google Cloud SDK
- Adicione ao PATH do sistema

### Erro: "Não autenticado"
- Execute: `gcloud auth login`
- Verifique: `gcloud auth list`

### Erro: "Permission denied"
- Verifique se tem permissões de Owner ou Editor no projeto GCP
- Verifique se o projeto está correto: `gcloud config get-value project`

### Erro no Build
- Verifique se `Dockerfile.prod` existe
- Verifique se `requirements_producao.txt` existe
- Verifique os logs: `gcloud builds list --limit 1`

### Erro nas Migrações
- Verifique os logs do job: `gcloud run jobs executions list --job migrate-monpec --region us-central1`
- Execute manualmente se necessário

### Serviço não inicia
- Verifique os logs: `gcloud run services logs read monpec --region us-central1`
- Verifique variáveis de ambiente: `gcloud run services describe monpec --region us-central1`

## 📚 Arquivos Importantes:

- `DEPLOY_COMPLETO_FINAL_ATUALIZADO.ps1` - Script completo atualizado
- `DEPLOY_COMPLETO_CORRIGIDO.ps1` - Script corrigido original
- `Dockerfile.prod` - Dockerfile para produção
- `cloudbuild-config.yaml` - Configuração do Cloud Build (opcional)
- `sistema_rural/settings_gcp.py` - Configurações do Django para GCP

## ✅ Checklist Final:

Após o deploy, verifique:

- [ ] Landing page carrega corretamente
- [ ] Botão "Demonstração" abre o modal
- [ ] Formulário de demonstração funciona
- [ ] Login admin funciona (admin / L6171r12@@)
- [ ] Sistema assinante acessível
- [ ] Páginas do Mercado Pago funcionam
- [ ] Migrações aplicadas
- [ ] Arquivos estáticos coletados

## 🎉 Pronto!

Se tudo estiver funcionando, o sistema está completamente deployado e pronto para uso!








