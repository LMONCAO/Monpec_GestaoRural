# 🔍 RELATÓRIO DE AUDITORIA DO SISTEMA

## 📊 RESUMO EXECUTIVO

Este relatório identifica problemas, arquivos desnecessários e oportunidades de melhoria no sistema.

---

## 1. ⚠️ ARQUIVOS TEMPORÁRIOS NA RAIZ DO PROJETO

Os seguintes arquivos Python na raiz são scripts temporários/teste e devem ser removidos ou movidos para uma pasta `scripts/`:

### Arquivos de Teste/Verificação:
- `testar_token.py`
- `testar_mercadopago_conexao.py`
- `testar_checkout_mercadopago.py`
- `testar_envio_email.py`
- `testar_envio_monpecnfe.py`
- `testar_autenticacao_gmail.py`
- `verificar_estado_migracao.py`
- `verificar_configuracao.py`
- `verificar_admin.py`
- `verificar_migracoes.py`
- `verificar_logs_email.py`
- `verificar_e_reiniciar.py`

### Arquivos de Correção/Configuração:
- `corrigir_ncm_null.py`
- `corrigir_admin_agora.py`
- `corrigir_admin_via_manage.py`
- `corrigir_admin_producao.py`
- `corrigir_senhas_hardcoded.py` (em scripts/)
- `configurar_email.py`
- `configurar_email_oauth2_completo.py`
- `autenticar_gmail.py`
- `fazer_configuracao_oauth2.py`

### Arquivos de Criação de Admin (múltiplos):
- `create_superuser.py`
- `criar_admin.py`
- `criar_admin_cloud.py`
- `criar_admin_cloud_sql.py`
- `criar_admin_cloud_run.py`
- `criar_admin_cloud_shell.py`
- `criar_admin_producao.py`
- `criar_admin_fix.py`
- `criar_admin_simples.py`
- `criar_admin_definitivo.py`
- `criar_admin_via_shell.py`

### Arquivos de Atualização/Migração:
- `atualizar_precos_db.py`
- `atualizar_precos_temp.py`
- `atualizar_credenciais_mercadopago.py`
- `aplicar_migracoes.py`
- `aplicar_migrations.py`
- `aplicar_migrations_nfe.py`
- `aplicar_migracoes_mercadopago.py`

### Outros Scripts Temporários:
- `executar_criar_dados.py`
- `redefinir_senha_admin.py`
- `redefinir_senha_usuario.py`
- `diagnosticar_erro_producao.py`
- `listar_propriedades_proprietarios.py`

**TOTAL: ~40 arquivos temporários identificados**

---

## 2. 🔒 PROBLEMAS DE SEGURANÇA

### Senhas Hardcoded Encontradas:

1. **`criar_admin_cloud_sql.py:63`**
   ```python
   password = 'L6171r12@@'
   ```

2. **`criar_admin_producao.py:20`**
   ```python
   password = 'L6171r12@@'
   ```

3. **`criar_admin_fix.py:28`**
   ```python
   password = 'L6171r12@@'
   ```

4. **`gestao_rural/views.py:209`**
   ```python
   password='monpec',
   ```

### SECRET_KEY Hardcoded:

1. **`sistema_rural/settings_gcp.py:14`**
   ```python
   SECRET_KEY = '0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_$1ap4+4t'
   ```

2. **`sistema_rural/settings.py:45`**
   ```python
   SECRET_KEY = 'YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE'
   ```

**⚠️ AÇÃO NECESSÁRIA:** Remover todas as senhas e SECRET_KEYs hardcoded. Usar variáveis de ambiente ou arquivo `.env`.

---

## 3. 📁 ARQUIVOS MUITO GRANDES

Arquivos que podem precisar de refatoração:

- `gestao_rural/views.py` - **4719 linhas** ⚠️ (muito grande, considerar dividir)
- `templates/site/landing_page.html` - **2962 linhas** ⚠️
- `gestao_rural/urls.py` - **505 linhas**
- `templates/gestao_rural/pecuaria_projecao.html` - **906 linhas**
- `templates/gestao_rural/pecuaria_planejamento_dashboard.html` - **1393 linhas**

**Recomendação:** Dividir `views.py` em múltiplos arquivos por módulo (views_vendas.py, views_compras.py, etc.)

---

## 4. 📝 COMENTÁRIOS TODO/FIXME

Foram encontrados comentários TODO/FIXME no código que indicam tarefas pendentes. Revisar e resolver.

---

## 5. 🔧 ARQUIVOS DE CONFIGURAÇÃO

### Settings Duplicados:
- `sistema_rural/settings.py` - Desenvolvimento
- `sistema_rural/settings_gcp.py` - Google Cloud Platform
- `sistema_rural/settings_producao.py` - Produção Locaweb

**Status:** ✅ Normal - diferentes ambientes

---

## 📋 RECOMENDAÇÕES PRIORITÁRIAS

### 🔴 CRÍTICO (Fazer Imediatamente):
1. **Remover senhas hardcoded** - Mover para variáveis de ambiente
2. **Remover SECRET_KEYs hardcoded** - Usar apenas variáveis de ambiente
3. **Limpar arquivos temporários** - Mover para `scripts/` ou remover

### 🟡 IMPORTANTE (Fazer em Breve):
4. **Refatorar views.py** - Dividir em módulos menores
5. **Revisar comentários TODO/FIXME** - Resolver pendências
6. **Organizar scripts** - Criar estrutura `scripts/` organizada

### 🟢 MELHORIAS (Fazer Quando Possível):
7. **Adicionar linting** - Configurar pylint/flake8
8. **Adicionar formatação** - Configurar black/autopep8
9. **Documentação** - Melhorar docstrings e comentários

---

## 🚀 PRÓXIMOS PASSOS

1. Executar `limpar_arquivos_temporarios.py` para organizar scripts
2. Corrigir problemas de segurança identificados
3. Refatorar `views.py` em módulos menores
4. Configurar ferramentas de qualidade de código

---

**Data da Auditoria:** $(date)
**Versão do Sistema:** Django 4.2.7






