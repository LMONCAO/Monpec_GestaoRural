# 🔍 RELATÓRIO COMPLETO - PROBLEMAS DE DEPLOY NO GCP

**Data:** 2025-01-27  
**Projeto:** monpec-sistema-rural  
**Serviço:** monpec (Cloud Run)  
**Região:** us-central1

---

## 📋 RESUMO EXECUTIVO

Este relatório identifica **6 problemas críticos** que estão impedindo o deploy correto do sistema MONPEC no Google Cloud Platform (GCP). Cada problema foi analisado em detalhes com suas causas raiz e soluções propostas.

---

## ❌ PROBLEMA 1: Erro de Conexão Cloud SQL

### Descrição
O sistema não consegue conectar ao banco de dados Cloud SQL PostgreSQL.

### Sintomas
- Erros 502 Bad Gateway no Cloud Run
- Logs mostram: `FATAL: password authentication failed`
- Logs mostram: `could not translate host name`
- Timeout ao tentar conectar ao banco

### Causa Raiz
1. **Variáveis de ambiente não configuradas** no Cloud Run:
   - `DB_HOST` não configurado ou incorreto
   - `DB_NAME` não configurado
   - `DB_USER` não configurado
   - `DB_PASSWORD` não configurado ou incorreto

2. **Cloud SQL Proxy não configurado** corretamente:
   - Conexão Unix socket não habilitada
   - Instância Cloud SQL não vinculada ao Cloud Run

3. **Credenciais incorretas**:
   - Senha do banco diferente da configurada
   - Usuário do banco não existe

### Solução
1. Configurar variáveis de ambiente no Cloud Run
2. Vincular instância Cloud SQL ao serviço Cloud Run
3. Verificar e corrigir credenciais do banco
4. Testar conexão antes do deploy

---

## ❌ PROBLEMA 2: Erro de ALLOWED_HOSTS

### Descrição
Django bloqueia requisições porque o host não está na lista ALLOWED_HOSTS.

### Sintomas
- Erro 400 Bad Request
- Logs mostram: `Invalid HTTP_HOST header`
- Acesso via domínio personalizado falha
- Acesso via URL do Cloud Run funciona

### Causa Raiz
1. **ALLOWED_HOSTS não inclui**:
   - URL do Cloud Run: `monpec-xxxxx-uc.a.run.app`
   - Domínio personalizado: `monpec.com.br`
   - Domínio www: `www.monpec.com.br`

2. **Configuração hardcoded** em settings que não considera variáveis de ambiente

### Solução
1. Adicionar todos os hosts necessários ao ALLOWED_HOSTS
2. Usar variável de ambiente `ALLOWED_HOSTS` com valores separados por vírgula
3. Configurar no Cloud Run: `ALLOWED_HOSTS=monpec.com.br,www.monpec.com.br,*.run.app`

---

## ⚠️ PROBLEMA 3: Problemas de Memória/Timeout

### Descrição
O serviço Cloud Run está com recursos insuficientes, causando timeouts e erros 503.

### Sintomas
- Erro 503 Service Unavailable
- Timeout durante o build
- Timeout durante migrações
- Processo sendo morto por falta de memória

### Causa Raiz
1. **Memória insuficiente**: Configurado com 2Gi, mas precisa de mais
2. **Timeout muito baixo**: 300s não é suficiente para migrações e build
3. **CPU limitada**: Pode estar causando lentidão

### Solução
1. Aumentar memória para **4Gi** (ou mais se necessário)
2. Aumentar timeout para **600s** (10 minutos)
3. Considerar aumentar CPU para 2 vCPUs se necessário

---

## ❌ PROBLEMA 4: Configurações Conflitantes

### Descrição
Múltiplos arquivos de configuração antigos estão causando conflitos.

### Sintomas
- Comportamento inconsistente entre deploys
- Configurações sendo sobrescritas
- Erros diferentes a cada deploy

### Causa Raiz
1. **Múltiplos arquivos de configuração**:
   - `app.yaml` (App Engine - não usado)
   - `cloudbuild.yaml` (antigo)
   - `cloudbuild-config.yaml` (novo)
   - Configurações hardcoded no código

2. **Variáveis de ambiente duplicadas** em diferentes lugares

3. **Scripts antigos** ainda sendo executados

### Solução
1. Remover arquivos de configuração antigos e não utilizados
2. Consolidar configurações em um único arquivo
3. Usar apenas variáveis de ambiente para configurações dinâmicas
4. Limpar recursos antigos do GCP antes de novo deploy

---

## ❌ PROBLEMA 5: Variáveis de Ambiente Faltando

### Descrição
Variáveis de ambiente críticas não estão configuradas no Cloud Run.

### Sintomas
- Erros de configuração no Django
- Funcionalidades não funcionam (Mercado Pago, email, etc.)
- Logs mostram: `KeyError` ou `NoneType`

### Variáveis Faltando
1. **SECRET_KEY**: Chave secreta do Django (obrigatória)
2. **DB_HOST**: Host do banco de dados
3. **DB_NAME**: Nome do banco
4. **DB_USER**: Usuário do banco
5. **DB_PASSWORD**: Senha do banco
6. **ALLOWED_HOSTS**: Hosts permitidos
7. **MERCADOPAGO_ACCESS_TOKEN**: Token do Mercado Pago (opcional)
8. **MERCADOPAGO_PUBLIC_KEY**: Chave pública do Mercado Pago (opcional)
9. **EMAIL_HOST**: Servidor de email (opcional)
10. **EMAIL_PORT**: Porta do email (opcional)
11. **EMAIL_HOST_USER**: Usuário do email (opcional)
12. **EMAIL_HOST_PASSWORD**: Senha do email (opcional)

### Solução
1. Criar script para configurar todas as variáveis
2. Documentar todas as variáveis necessárias
3. Validar variáveis antes do deploy
4. Usar Secret Manager para dados sensíveis

---

## ⚠️ PROBLEMA 6: Migrações Não Aplicadas

### Descrição
Migrações do Django não estão sendo aplicadas no banco de dados.

### Sintomas
- Erros de tabelas não encontradas
- Funcionalidades não funcionam
- Erros de campos faltando

### Causa Raiz
1. **Migrações não executadas** após deploy
2. **Banco de dados inconsistente** com o código
3. **Script de migração não configurado** no Cloud Build

### Solução
1. Executar migrações automaticamente no Cloud Build
2. Criar job do Cloud Run para migrações
3. Validar migrações antes de marcar deploy como completo
4. Documentar processo de migração

---

## 🎯 PRIORIZAÇÃO DOS PROBLEMAS

### Críticos (Bloqueiam deploy)
1. ❌ Erro de Conexão Cloud SQL
2. ❌ Erro de ALLOWED_HOSTS
3. ❌ Variáveis de Ambiente Faltando

### Importantes (Causam instabilidade)
4. ⚠️ Problemas de Memória/Timeout
5. ⚠️ Migrações Não Aplicadas

### Moderados (Causam confusão)
6. ❌ Configurações Conflitantes

---

## 📊 IMPACTO

### Impacto no Sistema
- **Disponibilidade**: Sistema completamente inacessível
- **Funcionalidade**: Nenhuma funcionalidade funciona
- **Experiência do Usuário**: Erros 502/503/400 constantes
- **Confiabilidade**: Sistema instável e imprevisível

### Impacto no Negócio
- **Perda de receita**: Sistema não disponível para clientes
- **Imagem**: Sistema parece não funcionar
- **Produtividade**: Tempo gasto tentando corrigir problemas

---

## ✅ SOLUÇÕES PROPOSTAS

### Solução Rápida (Temporária)
1. Configurar variáveis de ambiente manualmente
2. Aumentar recursos do Cloud Run
3. Executar migrações manualmente

### Solução Definitiva (Recomendada)
1. **Limpar todos os recursos antigos** do GCP
2. **Instalar tudo do zero** com configurações corretas
3. **Automatizar** todo o processo com scripts
4. **Documentar** todo o processo

---

## 📝 PRÓXIMOS PASSOS

1. ✅ Criar scripts de limpeza de recursos
2. ✅ Criar scripts de instalação do zero
3. ✅ Documentar processo completo
4. ⏳ Executar limpeza e instalação
5. ⏳ Validar funcionamento
6. ⏳ Configurar monitoramento

---

## 🔗 ARQUIVOS RELACIONADOS

- `LIMPAR_RECURSOS_GCP.sh` / `.ps1` - Scripts de limpeza
- `INSTALAR_DO_ZERO.sh` / `.ps1` - Scripts de instalação
- `GUIA_USO_SCRIPTS_LIMPEZA.md` - Guia de uso
- `RESUMO_EXECUTIVO_SOLUCAO.md` - Resumo executivo

---

**Status:** ✅ Análise Completa  
**Próxima Ação:** Executar scripts de limpeza e instalação























