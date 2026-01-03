# 📋 Próximos Passos - Deploy Falhou

## ⚠️ Situação Atual

O build foi **bem-sucedido**, mas o deploy falhou porque o container não iniciou a tempo.

## 🔍 Passo 1: Verificar Logs

Execute no Cloud Shell para ver o erro específico:

```bash
bash VERIFICAR_LOGS_DEPLOY.sh
```

Ou execute diretamente:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50 --format="table(timestamp,severity,textPayload)"
```

## 🔧 Possíveis Problemas e Soluções

### Problema 1: Script `diagnostico_banco_cloud.py` não existe

**Sintoma:** Erro sobre script não encontrado

**Solução:** Atualizei o Dockerfile.prod para não depender desse script. Você precisa fazer um novo build.

### Problema 2: Timeout muito curto

**Sintoma:** Container não inicia a tempo

**Solução:** Execute o script V2 que tem timeout aumentado:

```bash
bash DEPLOY_CORRECOES_DEMO_V2.sh
```

### Problema 3: Erro ao conectar ao banco

**Sintoma:** Erro de conexão com PostgreSQL

**Solução:** Verifique:
1. CLOUD_SQL_CONNECTION_NAME está correto
2. Permissões IAM configuradas
3. Cloud SQL instance está rodando

## ✅ Solução Rápida: Rebuild com Dockerfile Corrigido

Como atualizei o Dockerfile.prod para remover a dependência do script problemático, você precisa fazer um novo build:

```bash
cd ~/Monpec_GestaoRural
bash DEPLOY_CORRECOES_DEMO_V2.sh
```

Este script tem:
- ✅ Timeout aumentado (900s ao invés de 600s)
- ✅ Startup CPU boost habilitado
- ✅ Melhor tratamento de erros

## 📝 O Que Foi Corrigido no Dockerfile

1. ✅ Removida dependência do script `diagnostico_banco_cloud.py`
2. ✅ Simplificado o CMD para executar diretamente migrações
3. ✅ Adicionado fallback para criar admin diretamente via Python
4. ✅ Melhor tratamento de erros (não para em avisos)

## 🚀 Após o Deploy Bem-Sucedido

1. Aguarde 1-2 minutos para o serviço inicializar
2. Limpe o cache do navegador (Ctrl+F5)
3. Teste o login com usuário demo
4. Verifique que o sistema reconhece corretamente como usuário demo

---

**Importante:** Os arquivos de correção estão no repositório local. Faça commit e push se quiser manter as mudanças, ou simplesmente execute o novo build que usará o Dockerfile atualizado.

