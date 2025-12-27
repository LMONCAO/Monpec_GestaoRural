# 🚀 Guia Rápido de Deploy - MONPEC com Admin

## Deploy Completo Automatizado

### Windows (Recomendado)

Execute o arquivo:
```
DEPLOY_COMPLETO.bat
```

Ou via PowerShell:
```powershell
.\DEPLOY_COMPLETO.ps1
```

### Linux/Mac

```bash
# Dar permissão de execução
chmod +x deploy.sh

# Executar deploy
./deploy.sh monpec-sistema-rural us-central1
```

## O que o script faz automaticamente:

1. ✅ **Build da Imagem Docker** - Constrói a imagem do sistema
2. ✅ **Deploy no Cloud Run** - Publica o sistema na web
3. ✅ **Executa Migrações** - Configura o banco de dados
4. ✅ **Cria Usuário Admin** - Configura acesso administrativo

## Credenciais de Acesso

Após o deploy, você terá acesso com:

- **URL**: Será exibida ao final do deploy
- **Usuário**: `admin`
- **Senha**: `L6171r12@@`

## Configuração do Projeto

Por padrão, o script usa:
- **Project ID**: `monpec-sistema-rural`
- **Região**: `us-central1`
- **Serviço**: `monpec`

Para usar um projeto diferente:
```powershell
.\DEPLOY_COMPLETO.ps1 -ProjectId "seu-projeto-id" -Region "us-central1"
```

## Pré-requisitos

1. ✅ Google Cloud SDK instalado (`gcloud`)
2. ✅ Autenticado no Google Cloud (`gcloud auth login`)
3. ✅ Projeto GCP criado e configurado
4. ✅ APIs habilitadas (o script faz isso automaticamente)

## Verificar Status

Após o deploy, você pode verificar:

```bash
# Ver URL do serviço
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

# Ver logs
gcloud run services logs read monpec --region us-central1 --follow
```

## Próximos Passos (Opcional)

### 1. Configurar Variáveis de Ambiente

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "SECRET_KEY=sua-chave-secreta-forte"
```

### 2. Conectar ao Cloud SQL (se usar banco PostgreSQL)

```bash
gcloud run services update monpec \
    --region us-central1 \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db
```

### 3. Configurar Domínio Personalizado

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

Depois, configure os registros DNS conforme mostrado pelo comando.

## Troubleshooting

### Erro: "Google Cloud SDK não está instalado"
- Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Certifique-se de que `gcloud` está no PATH

### Erro: "Não autenticado"
- Execute: `gcloud auth login`
- Verifique: `gcloud auth list`

### Erro: "Projeto não encontrado"
- Verifique o Project ID: `gcloud projects list`
- Configure: `gcloud config set project SEU_PROJECT_ID`

### Erro: "Permissão negada"
- Verifique permissões: `gcloud projects get-iam-policy SEU_PROJECT_ID`
- Certifique-se de ter permissões de Owner ou Editor

### Erro ao criar usuário admin
- Execute manualmente:
```bash
gcloud run jobs execute monpec-create-admin --region us-central1 --wait
```

## Acesso ao Sistema

Após o deploy bem-sucedido:

1. Acesse a URL exibida no final do script
2. Faça login com:
   - Usuário: `admin`
   - Senha: `L6171r12@@`
3. Acesse o painel administrativo em: `/admin/`

## Suporte

Para problemas ou dúvidas:
- Verifique os logs: `gcloud run services logs read monpec --region us-central1`
- Consulte a documentação: `GUIA_DEPLOY_RAPIDO.md`
- Consulte o guia completo: `DEPLOY_GCP_COMPLETO.md`



































