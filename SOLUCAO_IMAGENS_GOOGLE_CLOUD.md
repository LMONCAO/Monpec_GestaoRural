# Solução para Imagens não Aparecerem no Google Cloud

## Status das Correções

✅ **Correção na View**: A view `gestao_rural/views_static.py` foi corrigida para verificar primeiro em `STATIC_ROOT` (produção) e depois em `STATICFILES_DIRS`.

✅ **Collectstatic no Build**: O Dockerfile já executa `collectstatic` durante o build, então as imagens devem estar coletadas.

## Problema Identificado

O job do Cloud Run para executar collectstatic está falhando, mas isso pode não ser necessário se o collectstatic já foi executado durante o build do Docker.

## Soluções

### Solução 1: Verificar se as Imagens Estão no Container (Recomendado)

O collectstatic já é executado durante o build do Docker (linha 47 do Dockerfile.prod). As imagens devem estar em `/app/staticfiles/site/` dentro do container.

**Verificar no Cloud Run:**
1. Acesse o console do Google Cloud
2. Vá em Cloud Run > monpec > Revisions
3. Verifique se a última revisão foi implantada recentemente
4. Se não, faça um novo deploy

### Solução 2: Fazer Novo Deploy (Garante que tudo está atualizado)

Se você fez alterações recentes, faça um novo deploy completo:

```powershell
# Usar o script de deploy completo que já existe
.\scripts\deploy\DEPLOY_COMPLETO_FINAL.ps1
```

Isso vai:
1. Construir a nova imagem com collectstatic
2. Fazer deploy no Cloud Run
3. Garantir que todas as imagens estejam coletadas

### Solução 3: Verificar WhiteNoise

O WhiteNoise está configurado no `settings_gcp.py` e deve servir os arquivos de `/app/staticfiles` automaticamente.

**Verificar configuração:**
- WhiteNoise middleware está ativo
- `STATIC_ROOT = '/app/staticfiles'`
- `WHITENOISE_ROOT = STATIC_ROOT`

### Solução 4: Testar URLs Diretamente

Teste se as imagens estão acessíveis diretamente:

```
https://monpec.com.br/static/site/foto1.jpeg
https://monpec.com.br/static/site/foto2.jpeg
https://monpec.com.br/static/site/foto3.jpeg
https://monpec.com.br/static/site/foto4.jpeg
https://monpec.com.br/static/site/foto5.jpeg
https://monpec.com.br/static/site/foto6.jpeg
```

Se retornar 404, o problema é que as imagens não estão sendo servidas.

### Solução 5: Verificar Logs do Cloud Run

```bash
gcloud run services logs read monpec --region us-central1 --limit 100
```

Procure por erros relacionados a arquivos estáticos ou 404 nas requisições de imagens.

## Comando Rápido para Novo Deploy

Se você só precisa garantir que o collectstatic foi executado, faça um rebuild rápido:

```powershell
# 1. Construir nova imagem (vai executar collectstatic automaticamente)
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# 2. Fazer deploy da nova imagem
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec:latest --region us-central1
```

## Verificação Final

Após o deploy, verifique:

1. **No navegador**: Acesse https://monpec.com.br e veja se as imagens aparecem
2. **URLs diretas**: Teste as URLs das imagens listadas acima
3. **Console do navegador**: Abra DevTools (F12) > Network e veja se há erros 404 para as imagens

## Nota Importante

A correção na view `gestao_rural/views_static.py` já está aplicada. Ela agora:
- Verifica primeiro em `STATIC_ROOT` (`/app/staticfiles` em produção)
- Depois em `STATICFILES_DIRS` (fallback)
- Serve com os tipos MIME corretos
- Adiciona headers de cache

Se as imagens ainda não aparecerem após um novo deploy, o problema pode ser:
1. As imagens não estão no diretório `static/site/` no código fonte
2. O WhiteNoise não está configurado corretamente
3. Há um problema de permissões no container


