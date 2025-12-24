# 🔒 GUIA DE CORREÇÕES DE SEGURANÇA IMPLEMENTADAS

Este documento descreve as correções de segurança implementadas e como aplicá-las.

---

## ✅ 1. SENHAS HARDCODED REMOVIDAS

### O que foi corrigido:
- Scripts de administração agora usam variável de ambiente `ADMIN_PASSWORD`
- Exemplo: `corrigir_admin_producao.py`

### Como usar:

**Antes (❌ INSEGURO):**
```python
password = 'L6171r12@@'  # Senha exposta no código
```

**Depois (✅ SEGURO):**
```bash
# Configure a variável de ambiente antes de executar
export ADMIN_PASSWORD='sua-senha-segura'
python corrigir_admin_producao.py
```

### Arquivos que precisam ser atualizados:

Todos os scripts que criam/corrigem usuário admin devem ser atualizados. Lista parcial:

- ✅ `corrigir_admin_producao.py` - **CORRIGIDO**
- ⚠️ `corrigir_admin_agora.py` - **PRECISA CORREÇÃO**
- ⚠️ `CORRIGIR_SENHA_ADMIN.py` - **PRECISA CORREÇÃO**
- ⚠️ `criar_admin_simples.py` - **PRECISA CORREÇÃO**
- ⚠️ `fix_admin.py` - **PRECISA CORREÇÃO**
- ⚠️ E outros 40+ arquivos similares...

### Como corrigir outros arquivos:

```python
# Substituir:
password = 'L6171r12@@'

# Por:
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável ADMIN_PASSWORD não configurada!")
    sys.exit(1)
```

---

## ✅ 2. SECRET_KEY CORRIGIDO

### O que foi corrigido:
- `settings.py` agora exige `SECRET_KEY` de variável de ambiente em produção
- Em desenvolvimento, ainda permite fallback com aviso

### Como configurar:

```bash
# Gerar uma nova SECRET_KEY segura:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar variável de ambiente:
export SECRET_KEY='sua-chave-gerada-aqui'
```

### Comportamento:

- **Desenvolvimento (DEBUG=True):** Permite fallback com aviso
- **Produção (DEBUG=False):** **FALHA** se `SECRET_KEY` não estiver configurada

---

## ✅ 3. VALIDAÇÃO DE WEBHOOKS

### O que foi corrigido:
- Webhook do WhatsApp agora valida token se configurado
- Webhook do Stripe já tinha validação (mantido)

### Como configurar:

```bash
# Gerar token seguro para WhatsApp:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Configurar variável de ambiente:
export WHATSAPP_WEBHOOK_TOKEN='seu-token-aqui'
```

### Como usar nos webhooks:

O webhook do WhatsApp agora verifica o header `X-Webhook-Token`:

```bash
# Exemplo de chamada ao webhook:
curl -X POST https://monpec.com.br/whatsapp/webhook/ \
  -H "X-Webhook-Token: seu-token-aqui" \
  -H "Content-Type: application/json" \
  -d '{"from": "5511999999999", "type": "audio"}'
```

Se `WHATSAPP_WEBHOOK_TOKEN` não estiver configurado, o webhook aceita qualquer requisição (apenas para desenvolvimento).

---

## ⚠️ 4. VERIFICAÇÃO DE PERMISSÕES EM VIEWS

### Status:
- ✅ Decorator `@verificar_propriedade_usuario` já existe em `gestao_rural/decorators.py`
- ⚠️ **PRECISA SER APLICADO** em ~50+ views que ainda não o usam

### Como aplicar:

**Antes (❌ INSEGURO):**
```python
@login_required
def minha_view(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    # Usuário pode acessar qualquer propriedade!
    ...
```

**Depois (✅ SEGURO):**
```python
from gestao_rural.decorators import verificar_propriedade_usuario

@login_required
@verificar_propriedade_usuario
def minha_view(request, propriedade_id):
    propriedade = request.propriedade  # Já validada e disponível
    ...
```

### Views que precisam ser corrigidas:

Segundo análise, as seguintes views precisam do decorator:

1. **views_compras.py** - 19 ocorrências
2. **views_curral.py** - múltiplas linhas
3. **views_analise.py** - 6 ocorrências
4. **views_pecuaria_completa.py**
5. **views_rastreabilidade.py**
6. **views_exportacao.py**
7. E outros...

### Exemplo de correção:

```python
# views_compras.py - linha 217
# ANTES:
@login_required
def compras_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    ...

# DEPOIS:
from gestao_rural.decorators import verificar_propriedade_usuario

@login_required
@verificar_propriedade_usuario
def compras_dashboard(request, propriedade_id):
    propriedade = request.propriedade  # Já validado
    ...
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Prioridade CRÍTICA:

- [x] Remover senha hardcoded de `corrigir_admin_producao.py`
- [ ] Remover senhas hardcoded dos outros 40+ scripts
- [x] Corrigir SECRET_KEY em `settings.py`
- [x] Adicionar validação de token no webhook WhatsApp
- [ ] Aplicar `@verificar_propriedade_usuario` em todas as views (50+ views)

### Próximos Passos:

1. **Script para corrigir todos os scripts de admin:**
   ```bash
   # Criar script que substitui senhas hardcoded em todos os arquivos
   ```

2. **Auditoria de views:**
   ```bash
   # Criar script para identificar todas as views que precisam do decorator
   ```

3. **Aplicar decorator:**
   - Aplicar manualmente ou criar script de migração

---

## 🔐 CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE

### Arquivo .env (criar na raiz do projeto):

Copie o arquivo `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
# Editar .env com suas configurações reais
```

### Para desenvolvimento local:

```bash
# Linux/Mac
export SECRET_KEY='sua-chave-aqui'
export ADMIN_PASSWORD='sua-senha-admin'
export WHATSAPP_WEBHOOK_TOKEN='seu-token-webhook'

# Windows PowerShell
$env:SECRET_KEY='sua-chave-aqui'
$env:ADMIN_PASSWORD='sua-senha-admin'
$env:WHATSAPP_WEBHOOK_TOKEN='seu-token-webhook'

# Windows CMD
set SECRET_KEY=sua-chave-aqui
set ADMIN_PASSWORD=sua-senha-admin
set WHATSAPP_WEBHOOK_TOKEN=seu-token-webhook
```

### Para produção (Google Cloud Run / servidor):

Configure as variáveis de ambiente no painel de controle ou via CLI:

```bash
# Google Cloud Run
gcloud run services update monpec \
  --set-env-vars SECRET_KEY='sua-chave',ADMIN_PASSWORD='sua-senha'
```

---

## ⚠️ IMPORTANTE

1. **NUNCA commite senhas ou tokens no Git**
   - Adicione `.env` ao `.gitignore`
   - Use apenas `.env.example` como template

2. **Gere novas senhas/tokens para produção**
   - Não reutilize senhas de desenvolvimento
   - Use geradores seguros de senhas

3. **Rotacione senhas expostas**
   - Se senhas hardcoded já foram expostas, mude-as imediatamente
   - Revise logs de acesso

4. **Teste as correções**
   - Teste em ambiente de desenvolvimento primeiro
   - Verifique que tudo funciona antes de produção

---

## 📚 RECURSOS

- [Django Security Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App - Config](https://12factor.net/config)

---

**Última atualização:** 2025-01-28











