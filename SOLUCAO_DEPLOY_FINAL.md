# SOLUÇÃO FINAL PARA DEPLOY - MONPEC

## Status Atual

- ✅ Backup completo criado
- ✅ APIs habilitadas
- ✅ Arquivos estáticos coletados
- ✅ .gcloudignore atualizado
- ✅ Dockerfile criado
- ❌ Deploy no Cloud Run falhando (Container import failed)

## Problema Identificado

O erro "Container import failed" no Cloud Run geralmente indica:
1. Problemas com o build do container
2. Arquivos muito grandes
3. Dependências faltando no requirements.txt

## Soluções Disponíveis

### Opção 1: Verificar Logs Detalhados do Build

```powershell
# Ver últimos builds
gcloud builds list --limit=5

# Ver logs de um build específico
gcloud builds log [BUILD_ID]
```

### Opção 2: Deploy via App Engine (Recomendado)

App Engine é mais simples e pode funcionar melhor:

```powershell
# 1. Criar aplicação App Engine
gcloud app create --region=southamerica-east1

# 2. Copiar app.yaml para raiz
copy deploy\config\app.yaml app.yaml

# 3. Deploy
gcloud app deploy
```

Ou execute o script:
```powershell
.\DEPLOY_APP_ENGINE.bat
```

### Opção 3: Deploy Manual com Build Local

Se o deploy automático continuar falhando:

```powershell
# 1. Build local da imagem Docker
docker build -t gcr.io/monpec-sistema-rural/monpec-gestao-rural .

# 2. Push para Container Registry
docker push gcr.io/monpec-sistema-rural/monpec-gestao-rural

# 3. Deploy da imagem
gcloud run deploy monpec-gestao-rural \
    --image gcr.io/monpec-sistema-rural/monpec-gestao-rural \
    --region southamerica-east1 \
    --platform managed \
    --allow-unauthenticated
```

### Opção 4: Simplificar Requirements

Algumas dependências podem estar causando problemas. Criar `requirements_minimal.txt`:

```txt
Django==4.2.7
Pillow>=10.1.0
python-decouple==3.8
psycopg2-binary==2.9.9
gunicorn
```

E usar no Dockerfile:
```dockerfile
COPY requirements_minimal.txt requirements.txt
```

## Próximos Passos Recomendados

1. **Tentar App Engine primeiro** (mais simples):
   ```powershell
   .\DEPLOY_APP_ENGINE.bat
   ```

2. **Se App Engine funcionar**, configurar variáveis de ambiente:
   - Ir para: https://console.cloud.google.com/appengine
   - Settings > Environment Variables
   - Adicionar todas as variáveis necessárias

3. **Se App Engine também falhar**, verificar logs detalhados:
   ```powershell
   gcloud builds list --limit=5
   gcloud builds log [BUILD_ID]
   ```

## Checklist Final

- [ ] Backup completo feito ✅
- [ ] .gcloudignore atualizado ✅
- [ ] Dockerfile criado ✅
- [ ] Arquivos estáticos coletados ✅
- [ ] Tentar App Engine
- [ ] Configurar variáveis de ambiente
- [ ] Executar migrações
- [ ] Criar superusuário
- [ ] Testar sistema

## Arquivos Criados

- `DEPLOY_APP_ENGINE.bat` - Script para deploy no App Engine
- `SOLUCAO_DEPLOY_FINAL.md` - Este arquivo
- `CORRIGIR_DEPLOY.md` - Instruções detalhadas
- `BACKUP_COMPLETO.md` - Documentação completa

## Suporte Adicional

Se nenhuma solução funcionar:
1. Verificar logs no Google Cloud Console
2. Verificar se há erros de sintaxe no código
3. Considerar usar um serviço de hospedagem alternativo temporariamente
4. Verificar se todas as dependências estão corretas no requirements.txt






