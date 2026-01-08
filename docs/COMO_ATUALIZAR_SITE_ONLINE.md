# Como Atualizar o Site Online no Google Cloud

## Problema Identificado

As fotos (foto1.jpeg a foto6.jpeg) não estavam aparecendo na landing page online porque:
1. **Problema de z-index**: O overlay estava cobrindo as imagens
2. **Problema de deploy**: As imagens podem não estar sendo coletadas/servidas corretamente

## Correções Aplicadas

### 1. Correção do CSS (templates/site/landing_page.html)
- ✅ Ajustado z-index do slide ativo de 1 para 2
- ✅ Ajustado z-index do overlay de 1 para 3
- ✅ Ajustado z-index do container do hero de 2 para 4
- ✅ Reduzida opacidade do overlay de 0.3 para 0.2 (imagens mais visíveis)
- ✅ Melhorado JavaScript com logs de debug e retry automático

### 2. Melhorias no Dockerfile.prod
- ✅ Adicionada verificação específica das 6 imagens durante o build
- ✅ Melhorado comando collectstatic com fallback
- ✅ Adicionados logs detalhados para debug

### 3. Melhorias no settings_gcp.py
- ✅ Adicionada configuração de MIME types para imagens JPEG
- ✅ Garantido que WhiteNoise serve imagens corretamente

## Como Fazer o Deploy

### Opção 1: Script Automatizado (Recomendado)

Execute o script que foi criado:

```batch
DEPLOY_GARANTIR_VERSAO_CORRETA.bat
```

Este script:
1. ✅ Verifica se todas as 6 imagens existem localmente
2. ✅ Faz build SEM CACHE (garante versão nova)
3. ✅ Faz deploy no Cloud Run
4. ✅ Verifica se as imagens estão acessíveis online
5. ✅ **NOVO**: Fornece feedback em tempo real durante o processo
6. ✅ **NOVO**: Mostra mensagens claras de progresso (evita travamentos aparentes)
7. ✅ **NOVO**: Captura e exibe códigos de erro para diagnóstico
8. ✅ **NOVO**: Resumo final claro de sucesso/falha

**Importante**: O script pode levar 10-25 minutos no total. Durante o build e deploy, você verá mensagens de progresso. **NÃO feche a janela** mesmo que pareça travado - os processos estão rodando em segundo plano.

### Opção 2: Deploy Manual

Se preferir fazer manualmente:

```batch
# 1. Verificar imagens locais
dir static\site\foto*.jpeg

# 2. Fazer build sem cache
gcloud builds submit --no-cache --tag gcr.io/monpec-sistema-rural/sistema-rural .

# 3. Fazer deploy
gcloud run deploy monpec ^
    --image gcr.io/monpec-sistema-rural/sistema-rural ^
    --region=us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db ^
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" ^
    --memory=2Gi ^
    --cpu=2
```

## Melhorias no Script de Deploy

O script `DEPLOY_GARANTIR_VERSAO_CORRETA.bat` foi melhorado para resolver problemas de feedback:

### O que foi corrigido:
- ✅ **Feedback em tempo real**: Agora você vê mensagens claras durante todo o processo
- ✅ **Avisos de progresso**: Mensagens indicam quando processos longos estão rodando
- ✅ **Captura de erros**: Códigos de erro são capturados e exibidos claramente
- ✅ **Resumo final**: Ao final, você sabe exatamente se o deploy foi bem-sucedido
- ✅ **Troubleshooting**: Mensagens de erro incluem dicas de como resolver problemas

### Como interpretar o script:
1. **Durante o build** (5-15 min): Você verá o output do `gcloud builds submit` em tempo real
2. **Durante o deploy** (3-10 min): Você verá o progresso do `gcloud run deploy`
3. **Ao final**: Um resumo mostra se BUILD e DEPLOY foram bem-sucedidos

### Se o script parecer travado:
- **NÃO feche a janela** - processos longos podem não mostrar output imediatamente
- Aguarde pelo menos 20 minutos antes de considerar que travou
- O script mostra mensagens como "[AVISO] Este processo pode levar X minutos..."

## Verificação Pós-Deploy

Após o deploy, verifique:

1. **Aguarde 1-2 minutos** para o serviço inicializar completamente

2. **Limpe o cache do navegador** (Ctrl+F5 ou Ctrl+Shift+R)

3. **Verifique as imagens diretamente**:
   ```
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto1.jpeg
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto2.jpeg
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto3.jpeg
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto4.jpeg
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto5.jpeg
   https://monpec-fzzfjppzva-uc.a.run.app/static/site/foto6.jpeg
   ```

4. **Verifique o console do navegador** (F12):
   - Abra a aba "Console"
   - Procure por mensagens de erro relacionadas a imagens
   - Procure por mensagens do slideshow (ex: "Slideshow: Imagem 1 carregada")

5. **Verifique os logs do Cloud Run**:
   ```batch
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50
   ```

## Troubleshooting

### Se as imagens ainda não aparecerem:

1. **Verifique se o collectstatic coletou as imagens**:
   - Os logs do build devem mostrar: "✅ foto1.jpeg encontrado" até "✅ foto6.jpeg encontrado"

2. **Verifique se o WhiteNoise está servindo**:
   - Acesse diretamente uma URL de imagem
   - Se retornar 404, o problema é no collectstatic ou no WhiteNoise

3. **Verifique o console do navegador**:
   - Erros 404 = imagens não coletadas
   - Erros CORS = problema de configuração
   - Erros de z-index = problema de CSS (já corrigido)

4. **Force um novo build sem cache**:
   ```batch
   gcloud builds submit --no-cache --tag gcr.io/monpec-sistema-rural/sistema-rural .
   ```

## Estrutura de Arquivos Esperada

```
static/
  site/
    foto1.jpeg ✅
    foto2.jpeg ✅
    foto3.jpeg ✅
    foto4.jpeg ✅
    foto5.jpeg ✅
    foto6.jpeg ✅
```

## Próximos Passos

Após o deploy bem-sucedido:
1. ✅ As imagens devem aparecer no slideshow da landing page
2. ✅ O slideshow deve alternar entre as 6 imagens a cada 5 segundos
3. ✅ O overlay escuro deve estar mais transparente (opacidade 0.2)

## Suporte

Se ainda houver problemas:
1. Verifique os logs do Cloud Run
2. Verifique o console do navegador (F12)
3. Teste as URLs das imagens diretamente
4. Execute o script de deploy novamente com `--no-cache`

---

## 📚 Guias Relacionados

- **Como Deployar Correções de Usuário Demo:** Veja `COMO_DEPLOYAR_CORRECOES_DEMO.md`
- **Sincronizar com GitHub:** Veja `GUIA_SINCRONIZAR_GITHUB_GCLOUD.md`

