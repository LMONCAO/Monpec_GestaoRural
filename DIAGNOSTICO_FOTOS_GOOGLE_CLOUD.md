# 🔍 DIAGNÓSTICO: Fotos não aparecendo no Google Cloud

## Problema Identificado

As fotos da landing page não estão aparecendo no site hospedado no Google Cloud Run.

## Análise do Problema

### 1. **Localização das Fotos**
- ✅ Fotos estão em: `static/site/foto1.jpeg` até `foto6.jpeg`
- ✅ Template usa: `{% static 'site/foto1.jpeg' %}` (correto)
- ⚠️ Problema: Fotos precisam estar em `STATIC_ROOT` (`/app/staticfiles/site/`) no servidor

### 2. **Configuração Atual**

**settings_gcp.py:**
- `STATIC_ROOT = '/app/staticfiles'` ✅
- `STATICFILES_DIRS = [BASE_DIR / 'static']` ✅ (herdado de settings.py)
- `WHITENOISE_ROOT = STATIC_ROOT` ✅
- `WHITENOISE_USE_FINDERS = False` ⚠️ (só serve de STATIC_ROOT)

### 3. **Dockerfile**
- `collectstatic` é executado com `|| true` ⚠️ (pode falhar silenciosamente)
- Executado antes de copiar todos os arquivos (pode estar faltando arquivos)

### 4. **Possíveis Causas**

1. **collectstatic não copiou as fotos**
   - O comando pode ter falhado silenciosamente (`|| true`)
   - Arquivos podem não estar no container

2. **WhiteNoise não está servindo JPEG corretamente**
   - MIME types configurados, mas pode haver problema de cache

3. **Caminho incorreto no servidor**
   - Fotos podem não estar em `/app/staticfiles/site/`

4. **Permissões de arquivo**
   - Arquivos podem não ter permissão de leitura

## Soluções Propostas

### Solução 1: Verificar e Corrigir Dockerfile (RECOMENDADO)

1. Garantir que `collectstatic` seja executado corretamente
2. Verificar se as fotos foram copiadas
3. Adicionar logs para diagnóstico

### Solução 2: Adicionar Fallback para servir fotos

1. Criar view customizada para servir fotos se WhiteNoise falhar
2. Adicionar rota de fallback

### Solução 3: Usar Cloud Storage (FUTURO)

1. Configurar Cloud Storage para arquivos estáticos
2. Mais robusto para produção

## Soluções Implementadas

### ✅ 1. Dockerfile Corrigido
- Removido `|| true` do collectstatic para que falhe se houver erro
- Adicionadas verificações antes e depois do collectstatic
- Adicionados logs para diagnóstico
- Garantidas permissões corretas nos arquivos

### ✅ 2. Configuração WhiteNoise Melhorada
- Adicionados mais tipos MIME (webp, svg, ico)
- Configurado cache apropriado para imagens
- Mantida configuração de servir apenas de STATIC_ROOT

### ✅ 3. Script de Diagnóstico Criado
- Script `diagnosticar_fotos_cloud.py` para verificar:
  - Se as fotos existem no diretório original
  - Se as fotos foram coletadas para STATIC_ROOT
  - Se WhiteNoise está configurado corretamente
  - Se os finders do Django encontram as fotos

## Próximos Passos para Resolver

### 1. Executar Diagnóstico no Servidor
```bash
# No Cloud Shell ou container
python diagnosticar_fotos_cloud.py
```

### 2. Rebuild e Deploy
```bash
# Rebuild da imagem com as correções
gcloud builds submit --tag gcr.io/[PROJECT-ID]/monpec

# Deploy no Cloud Run
gcloud run deploy monpec --image gcr.io/[PROJECT-ID]/monpec --platform managed
```

### 3. Verificar Logs do Build
- Verificar se o collectstatic executou com sucesso
- Verificar se as fotos foram coletadas
- Verificar se há erros de permissão

### 4. Testar no Navegador
- Acessar https://monpec.com.br
- Abrir DevTools (F12)
- Verificar Network tab para ver se as fotos estão sendo carregadas
- Verificar se há erros 404 ou de CORS

## Comandos Úteis

### Verificar arquivos no container
```bash
# Listar fotos coletadas
ls -la /app/staticfiles/site/

# Verificar tamanho das fotos
du -sh /app/staticfiles/site/*.jpeg

# Testar se WhiteNoise está servindo
curl -I https://monpec.com.br/static/site/foto1.jpeg
```

### Re-executar collectstatic manualmente
```bash
python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp
```
