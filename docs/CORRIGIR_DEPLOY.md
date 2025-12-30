# CORREÇÃO DO DEPLOY - MONPEC

## Problema Identificado

O deploy está falhando com erro "Container import failed". Isso geralmente acontece por:

1. **Arquivos muito grandes** sendo enviados
2. **Dockerfile com problemas**
3. **Dependências faltando**

## Solução Passo a Passo

### 1. Verificar e Limpar Arquivos Grandes

Execute no diretório do projeto:

```powershell
# Verificar tamanho dos diretórios
Get-ChildItem -Directory | ForEach-Object { 
    $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | 
             Measure-Object -Property Length -Sum).Sum / 1MB
    [PSCustomObject]@{Diretorio=$_.Name; TamanhoMB=[math]::Round($size, 2)}
} | Sort-Object TamanhoMB -Descending
```

### 2. Atualizar .gcloudignore

Certifique-se de que o `.gcloudignore` exclui:
- `venv/`, `env/`, `.venv`
- `__pycache__/`, `*.pyc`
- `db.sqlite3` (banco local)
- `media/` (se muito grande)
- `backups/`
- `.git/`

### 3. Criar Dockerfile Simplificado

Crie um `Dockerfile` na raiz do projeto:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar código
COPY . .

# Coletar estáticos
RUN python manage.py collectstatic --noinput || true

EXPOSE $PORT

CMD exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120
```

### 4. Deploy Manual Passo a Passo

```powershell
# 1. Navegar para o projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# 2. Coletar estáticos
python manage.py collectstatic --noinput

# 3. Fazer deploy
gcloud run deploy monpec-gestao-rural `
    --source . `
    --region southamerica-east1 `
    --platform managed `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10
```

### 5. Alternativa: Deploy via App Engine

Se Cloud Run continuar falhando, use App Engine:

```powershell
# Copiar app.yaml para raiz
copy deploy\config\app.yaml app.yaml

# Deploy
gcloud app deploy
```

## Verificar Logs Detalhados

```powershell
# Ver logs do build
gcloud builds list --limit=5

# Ver logs de um build específico
gcloud builds log [BUILD_ID]

# Ver logs do serviço
gcloud run services logs read monpec-gestao-rural --region southamerica-east1
```

## Checklist de Deploy

- [ ] `.gcloudignore` configurado corretamente
- [ ] `Dockerfile` criado e testado localmente
- [ ] `requirements.txt` atualizado
- [ ] Arquivos estáticos coletados
- [ ] Nenhum arquivo grande sendo enviado
- [ ] Variáveis de ambiente configuradas no GCP Console

## Próximos Passos Após Deploy Bem-Sucedido

1. **Configurar Variáveis de Ambiente** no GCP Console:
   - `DEBUG=False`
   - `SECRET_KEY` (gerar uma nova)
   - `ALLOWED_HOSTS` (URL do serviço)
   - Configurações de Stripe
   - Configurações de Email

2. **Executar Migrações**:
```powershell
gcloud run services update monpec-gestao-rural \
    --region southamerica-east1 \
    --command "python" \
    --args "manage.py,migrate"
```

3. **Criar Superusuário**:
```powershell
gcloud run services update monpec-gestao-rural \
    --region southamerica-east1 \
    --command "python" \
    --args "manage.py,createsuperuser"
```

## Suporte

Se o problema persistir:
1. Verificar logs detalhados no Cloud Console
2. Verificar se há erros no Dockerfile
3. Tentar deploy com menos recursos primeiro (menos memória/CPU)
4. Considerar usar App Engine como alternativa
































