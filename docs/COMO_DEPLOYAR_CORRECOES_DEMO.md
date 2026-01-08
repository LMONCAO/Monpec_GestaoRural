# Como Fazer Deploy das Correções de Usuário Demo no Google Cloud

## 📋 Resumo das Correções

Foram corrigidos os seguintes arquivos:
- ✅ `gestao_rural/helpers_acesso.py` - Função `is_usuario_demo()` centralizada e `is_usuario_assinante()` agora exclui usuários demo
- ✅ `gestao_rural/middleware_liberacao_acesso.py` - Verifica se é demo ANTES de verificar assinatura
- ✅ `gestao_rural/context_processors.py` - Usa função centralizada

**Problema corrigido:** Usuários demo estavam sendo validados como assinantes no login.

---

## 🚀 Opção 1: Deploy Direto (Recomendado - Mais Rápido)

Esta opção faz deploy direto sem passar pelo GitHub. **Recomendado para correções urgentes**.

### Passo a Passo:

1. **Execute o script de deploy:**
   ```batch
   DEPLOY_GARANTIR_VERSAO_CORRETA.bat
   ```

2. **O que o script faz:**
   - ✅ Verifica que você está na pasta correta
   - ✅ Valida que o Dockerfile existe
   - ✅ Verifica autenticação no Google Cloud
   - ✅ Faz build da imagem Docker SEM CACHE (garante versão nova)
   - ✅ Faz deploy no Cloud Run
   - ✅ Verifica status do serviço

3. **Tempo estimado:** 10-25 minutos

4. **Durante o processo:**
   - ⚠️ **NÃO feche a janela** mesmo que pareça travado
   - Você verá mensagens de progresso
   - O build pode levar 5-15 minutos
   - O deploy pode levar 3-10 minutos

5. **Após o deploy:**
   - Aguarde 1-2 minutos para o serviço inicializar
   - Limpe o cache do navegador (Ctrl+F5)
   - Teste o login com um usuário demo

---

## 🔄 Opção 2: Deploy via GitHub Actions (Mais Organizado)

Esta opção faz commit, push para o GitHub e o GitHub Actions faz o deploy automaticamente.

### Passo a Passo:

#### 2.1. Verificar Status do Git

```batch
git status
```

Isso mostra quais arquivos foram modificados.

#### 2.2. Adicionar Arquivos Modificados

```batch
git add gestao_rural/helpers_acesso.py
git add gestao_rural/middleware_liberacao_acesso.py
git add gestao_rural/context_processors.py
```

Ou adicionar tudo:

```batch
git add .
```

#### 2.3. Fazer Commit

```batch
git commit -m "Corrigir validação: usuários demo não devem ser tratados como assinantes

- Adicionar função is_usuario_demo() centralizada em helpers_acesso.py
- Atualizar is_usuario_assinante() para excluir usuários demo
- Ajustar middleware para verificar demo ANTES de verificar assinatura
- Atualizar context_processors para usar função centralizada

Fixes: Usuários demo sendo validados como assinantes no login"
```

#### 2.4. Fazer Push para GitHub

```batch
git push origin main
```

Ou, se o branch for `master`:

```batch
git push origin master
```

#### 2.5. Monitorar Deploy no GitHub

1. Acesse: https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions
2. Clique na workflow "🚀 Deploy Principal - Google Cloud Run"
3. Acompanhe o progresso do deploy

**Tempo estimado:** 15-30 minutos (build + deploy via GitHub Actions)

---

## ✅ Verificação Pós-Deploy

Após o deploy (qualquer método), verifique:

### 1. Verificar que o Serviço Está Rodando

```batch
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

### 2. Testar Login com Usuário Demo

1. Acesse a URL do serviço
2. Preencha o formulário de demonstração
3. Faça login com o usuário criado
4. **Verificar:** O sistema deve reconhecer como usuário demo (não assinante)

### 3. Verificar Logs (se necessário)

```batch
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50
```

Procure por:
- Mensagens de login
- Erros relacionados a autenticação
- Mensagens sobre usuário demo

---

## 🔍 Troubleshooting

### Se o deploy falhar:

1. **Verificar autenticação:**
   ```batch
   gcloud auth list
   ```
   Se não estiver autenticado:
   ```batch
   gcloud auth login
   ```

2. **Verificar projeto:**
   ```batch
   gcloud config get-value project
   ```
   Deve mostrar: `monpec-sistema-rural`
   
   Se não:
   ```batch
   gcloud config set project monpec-sistema-rural
   ```

3. **Verificar build anterior:**
   ```batch
   gcloud builds list --limit=5
   ```
   Veja se há builds recentes e seus status

4. **Verificar serviço atual:**
   ```batch
   gcloud run services describe monpec --region=us-central1
   ```

### Se o login ainda não funcionar corretamente:

1. **Limpar cache do navegador** (Ctrl+Shift+Delete)
2. **Testar em janela anônima** (Ctrl+Shift+N)
3. **Verificar logs do Cloud Run** para erros
4. **Verificar se as mudanças foram aplicadas:**
   - O middleware deve verificar demo ANTES de assinante
   - A função `is_usuario_assinante()` deve retornar False para usuários demo

---

## 📝 Arquivos Modificados (Resumo)

Para referência, os arquivos que foram alterados:

1. **gestao_rural/helpers_acesso.py**
   - Adicionada função `is_usuario_demo(user)`
   - Atualizada `is_usuario_assinante(user)` para excluir usuários demo

2. **gestao_rural/middleware_liberacao_acesso.py**
   - Verifica se é demo ANTES de verificar assinatura
   - Usa função centralizada `is_usuario_demo()`

3. **gestao_rural/context_processors.py**
   - Removida função local `_is_usuario_demo()`
   - Agora usa `is_usuario_demo()` de `helpers_acesso`

---

## 🎯 Recomendação

**Use a Opção 1 (Deploy Direto)** para esta correção porque:
- ✅ Mais rápido (10-25 min vs 15-30 min)
- ✅ Não requer commit/push
- ✅ Ideal para correções urgentes
- ✅ Você tem controle total do processo

**Use a Opção 2 (GitHub Actions)** quando:
- ✅ Quiser manter histórico no Git
- ✅ Tiver múltiplas correções para deployar juntas
- ✅ Quiser rastreabilidade completa

---

## 📞 Suporte

Se houver problemas:

1. Verifique os logs do Cloud Run
2. Verifique os logs do build no Google Cloud Console
3. Execute o script de deploy novamente com `--no-cache`
4. Verifique que os arquivos modificados estão no diretório correto


