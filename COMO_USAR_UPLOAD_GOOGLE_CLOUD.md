# Como Fazer Upload da Pasta para Google Cloud Storage

## Pré-requisitos

1. **Instalar Google Cloud SDK**
   - Baixe em: https://cloud.google.com/sdk/docs/install
   - Ou use: `winget install Google.CloudSDK`

2. **Autenticar no Google Cloud**
   ```powershell
   gcloud auth login
   gcloud config set project SEU_PROJECT_ID
   ```

## Método 1: Script Interativo (Recomendado)

### PowerShell:
Execute o script interativo que faz perguntas:

```powershell
.\upload_para_google_cloud.ps1
```

### Batch (.bat):
```cmd
upload_para_google_cloud.bat
```

O script irá:
- Verificar se você está autenticado
- Perguntar o nome do bucket
- Oferecer opções de exclusão de arquivos
- Escolher entre sincronização ou cópia completa

## Método 2: Script Simples (Rápido)

### PowerShell:
Para upload rápido sem perguntas:

```powershell
.\upload_para_google_cloud_simples.ps1 -BucketName "meu-bucket"
```

Com nome de projeto personalizado:
```powershell
.\upload_para_google_cloud_simples.ps1 -BucketName "meu-bucket" -ProjectName "monpec"
```

### Batch (.bat):
```cmd
upload_para_google_cloud_simples.bat meu-bucket
```

Com nome de projeto personalizado:
```cmd
upload_para_google_cloud_simples.bat meu-bucket monpec
```

Com modo específico (sync ou copy):
```cmd
upload_para_google_cloud_simples.bat meu-bucket monpec sync
```

## Método 3: Comando Direto (Mais Rápido)

Se você já sabe o nome do bucket:

```powershell
# Sincronizar (recomendado - só envia arquivos novos/modificados)
gsutil -m rsync -r -x "venv/**" -x "__pycache__/**" -x ".git/**" . gs://SEU-BUCKET/nome-projeto/

# Ou copiar tudo
gsutil -m cp -r -x "venv/**" -x "__pycache__/**" -x ".git/**" . gs://SEU-BUCKET/nome-projeto/
```

## Criar um Bucket Novo

Se o bucket não existir:

```powershell
gsutil mb -p SEU_PROJECT_ID -l us-central1 gs://NOME-DO-BUCKET
```

## Verificar Arquivos Enviados

```powershell
# Listar arquivos
gsutil ls -r gs://SEU-BUCKET/nome-projeto/

# Ver tamanho total
gsutil du -sh gs://SEU-BUCKET/nome-projeto/
```

## Arquivos Excluídos Automaticamente

Os scripts excluem automaticamente:
- `venv/` - Ambiente virtual Python
- `__pycache__/` - Cache Python
- `.git/` - Repositório Git
- `node_modules/` - Dependências Node
- `*.pyc` - Arquivos compilados
- `.env` - Variáveis de ambiente
- `logs/` - Arquivos de log
- `temp/` - Arquivos temporários

## Dicas

1. **Use sincronização (rsync)** para uploads subsequentes - é muito mais rápido
2. **Use o modo paralelo (-m)** - já está incluído nos scripts
3. **Verifique o tamanho** antes de fazer upload: `Get-ChildItem -Recurse | Measure-Object -Property Length -Sum`

## Troubleshooting

### Erro: "Access Denied"
- Verifique se você tem permissões no bucket
- Execute: `gcloud auth application-default login`

### Erro: "Bucket not found"
- Crie o bucket primeiro ou verifique o nome

### Upload muito lento
- Use `-m` para modo paralelo (já incluído)
- Exclua mais arquivos desnecessários
- Use rsync em vez de cp para uploads subsequentes

